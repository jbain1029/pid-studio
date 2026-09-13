"""Presentation-only component folders shared by the toolbox and browser.

Folder names are not document identifiers and never change saved component types.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem
try:
    from category_icons import category_icon
except ModuleNotFoundError as error:
    if error.name != 'category_icons':
        raise
    # The optional category artwork must not prevent opening a drawing.
    def category_icon(path):
        from PySide6.QtWidgets import QApplication, QStyle
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)


def folder_path(kind, definition):
    """Return a stable, human-readable folder path for any catalog entry."""
    category = definition.get('category', 'Other')
    if kind.startswith('custom:'):
        return ('Custom components', category)
    if category == 'Instrumentation':
        if 'controller' in kind:
            group = 'Controllers'
        elif kind.startswith(('pressure_', 'differential_pressure_')):
            group = 'Pressure'
        elif kind.startswith('temperature_') or kind in ('thermowell', 'thermocouple'):
            group = 'Temperature'
        elif kind == 'humidity_sensor':
            group = 'Analysis'
        elif kind in ('acoustic_sensor', 'hall_speed_sensor'):
            group = 'Acoustic & speed'
        elif 'level' in kind:
            group = 'Level'
        elif kind.startswith(('analysis_', 'ph_', 'conductivity_', 'density_')):
            group = 'Analysis'
        elif kind in ('instrument', 'current_pressure_converter'):
            group = 'General & signal conversion'
        else:
            group = 'Flow'
        return ('Instrumentation', group)
    if category == 'Valves & Actuators':
        if kind in ('control_valve', 'motor_operated_valve', 'solenoid_valve', 'pneumatic_piston_valve'):
            group = 'Actuated & control'
        elif 'regulator' in kind:
            group = 'Regulators'
        elif kind in ('check_valve', 'foot_valve'):
            group = 'Check valves'
        elif kind == 'relief_valve':
            return ('Pressure protection', 'Relief & venting')
        else:
            group = 'Manual valves'
        return ('Valves', group)
    if category == 'Pressure Protection':
        return ('Pressure protection', 'Flame protection' if kind == 'flame_arrester' else 'Relief & venting')
    if category in ('Steam & Condensate', 'Steam & Utilities'):
        group = 'Steam traps' if category == 'Steam & Condensate' else 'Utility equipment'
        return ('Steam & utilities', group)
    if category == 'Piping & Connections':
        if 'strainer' in kind:
            group = 'Strainers'
        elif kind in ('tee', 'pipe_cross', 'connector'):
            group = 'Junctions & connectors'
        else:
            group = 'Fittings & joints'
        return ('Piping', group)
    if category == 'Heat Transfer' or kind == 'exchanger':
        group = 'Heat transfer'
    elif category == 'Separation & Treatment' or kind == 'filter':
        group = 'Separation & treatment'
    elif kind == 'turbine':
        group = 'Turbines & expanders'
    elif 'compressor' in kind or kind == 'blower':
        group = 'Compressors & blowers'
    elif 'pump' in kind:
        group = 'Pumps'
    elif kind in ('agitated_tank', 'jacketed_reactor', 'static_mixer'):
        group = 'Reactors & mixers'
    elif category == 'Vessels & Reactors' or kind in ('tank', 'vessel'):
        group = 'Tanks & vessels'
    else:
        group = category
    return ('Process components', group)


def _walk(tree):
    def descendants(item):
        yield item
        for index in range(item.childCount()):
            yield from descendants(item.child(index))
    for index in range(tree.topLevelItemCount()):
        yield from descendants(tree.topLevelItem(index))


def populate(tree, catalog, icon_factory):
    """Replace a tree with collapsed folders and return kind-to-leaf mapping."""
    tree.clear()
    tree._component_folder_search = ''
    tree._component_folder_expansion = {}
    folders, leaves = {}, {}
    roots = ('Process components', 'Valves', 'Piping', 'Instrumentation',
             'Steam & utilities', 'Pressure protection', 'Custom components')
    def order(entry):
        kind, definition = entry
        path = folder_path(kind, definition)
        return (roots.index(path[0]) if path[0] in roots else len(roots),
                path, definition.get('label', kind).casefold(), kind)
    for kind, definition in sorted(catalog.items(), key=order):
        path = folder_path(kind, definition)
        parent = None
        for depth, label in enumerate(path, 1):
            key = path[:depth]
            if key not in folders:
                folder = QTreeWidgetItem([label])
                folder.setData(0, Qt.ItemDataRole.UserRole, None)
                folder.setData(0, Qt.ItemDataRole.UserRole + 1, key)
                folder.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                folder.setIcon(0, category_icon(key))
                if parent is None:
                    tree.addTopLevelItem(folder)
                else:
                    parent.addChild(folder)
                folders[key] = folder
            parent = folders[key]
        leaf = QTreeWidgetItem([definition.get('label', kind)])
        leaf.setData(0, Qt.ItemDataRole.UserRole, kind)
        leaf.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)
        if icon_factory is not None:
            leaf.setIcon(0, icon_factory(kind))
        ports = ', '.join(definition.get('ports', {})) or 'None'
        leaf.setToolTip(0, f"{definition.get('label', kind)}\nType: {kind}\nTag prefix: {definition.get('prefix', '')}\nPorts: {ports}\nFolder: {' / '.join(path)}")
        parent.addChild(leaf)
        leaves[kind] = leaf
    tree.collapseAll()
    return leaves


def filter_tree(tree, catalog, text):
    """Filter leaves recursively; temporarily expand matches during a search."""
    query = text.strip().casefold()
    previous = getattr(tree, '_component_folder_search', '')
    if query and not previous:
        tree._component_folder_expansion = {
            tuple(item.data(0, Qt.ItemDataRole.UserRole + 1)): item.isExpanded()
            for item in _walk(tree) if not item.data(0, Qt.ItemDataRole.UserRole)
        }
    tokens = query.replace('_', ' ').split()
    visible = []
    def visit(item):
        kind = item.data(0, Qt.ItemDataRole.UserRole)
        if kind:
            definition = catalog[kind]
            haystack = ' '.join((*folder_path(kind, definition), definition.get('label', ''),
                                 definition.get('prefix', ''), kind)).casefold().replace('_', ' ')
            match = all(token in haystack for token in tokens)
            item.setHidden(not match)
            if match:
                visible.append(item)
            return match
        match = False
        for index in range(item.childCount()):
            match = visit(item.child(index)) or match
        item.setHidden(not match)
        if query:
            item.setExpanded(match)
        elif previous:
            key = tuple(item.data(0, Qt.ItemDataRole.UserRole + 1))
            item.setExpanded(tree._component_folder_expansion.get(key, False))
        return match
    for index in range(tree.topLevelItemCount()):
        visit(tree.topLevelItem(index))
    tree._component_folder_search = query
    return visible
