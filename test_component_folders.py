import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTreeWidget

import component_folders as folders
import pidcore as core


class ComponentFolderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tree = QTreeWidget()
        self.leaves = folders.populate(self.tree, core.CATALOG, None)

    def tearDown(self):
        self.tree.close()

    def test_catalog_appears_once_and_folders_cannot_be_inserted_or_dragged(self):
        self.assertEqual(len(core.CATALOG), 141)
        actual = []
        for item in folders._walk(self.tree):
            kind = item.data(0, Qt.ItemDataRole.UserRole)
            if kind:
                actual.append(kind)
                self.assertTrue(item.flags() & Qt.ItemFlag.ItemIsDragEnabled)
                self.assertIn('Ports:', item.toolTip(0))
            else:
                self.assertIsNone(kind)
                self.assertTrue(item.flags() & Qt.ItemFlag.ItemIsSelectable)
                self.assertFalse(item.flags() & Qt.ItemFlag.ItemIsDragEnabled)
                self.assertFalse(item.isExpanded())
                self.assertFalse(item.icon(0).isNull())
        self.assertCountEqual(actual, core.CATALOG)
        self.assertEqual(set(self.leaves), set(core.CATALOG))

    def test_expected_folders(self):
        expected = {
            'pump': ('Process components', 'Pumps'),
            'horizontal_vessel': ('Process components', 'Tanks & vessels'),
            'solenoid_valve': ('Valves', 'Actuated & control'),
            'gate_valve': ('Valves', 'Manual valves'),
            'pressure_transmitter': ('Instrumentation', 'Pressure'),
            'pressure_controller': ('Instrumentation', 'Controllers'),
            'orifice_plate': ('Instrumentation', 'Flow'),
            'tee': ('Piping', 'Junctions & connectors'),
            'float_steam_trap': ('Steam & utilities', 'Steam traps'),
        }
        for kind, path in expected.items():
            self.assertEqual(folders.folder_path(kind, core.CATALOG[kind]), path)
        self.assertEqual(folders.folder_path('custom:sight_glass', {'category': 'Inspection'}),
                         ('Custom components', 'Inspection'))

    def test_category_icons_are_distinct_and_cover_subcategories(self):
        from category_icons import category_icon
        roots = ('Process components','Valves','Piping','Instrumentation',
                 'Steam & utilities','Pressure protection','Custom components')
        images = [category_icon((name,)).pixmap(20,20).toImage() for name in roots]
        for index, image in enumerate(images):
            self.assertFalse(image.isNull())
            for other in images[index+1:]:
                self.assertNotEqual(image,other)
        for kind, definition in core.CATALOG.items():
            icon = category_icon(folders.folder_path(kind,definition))
            self.assertFalse(icon.pixmap(20,20).isNull())
            self.assertFalse(icon.pixmap(40,40).isNull())
        self.assertFalse(category_icon(('Custom components','User category')).isNull())

    def test_search_restores_previous_folder_expansion(self):
        pump = self.leaves['pump']
        pump.parent().setExpanded(True)
        pump.parent().parent().setExpanded(True)
        before = {tuple(item.data(0, Qt.ItemDataRole.UserRole + 1)): item.isExpanded()
                  for item in folders._walk(self.tree) if not item.data(0, Qt.ItemDataRole.UserRole)}
        visible = folders.filter_tree(self.tree, core.CATALOG, 'instrumentation pressure transmitter')
        self.assertEqual({item.data(0, Qt.ItemDataRole.UserRole) for item in visible},
                         {'pressure_transmitter', 'differential_pressure_transmitter'})
        for item in visible:
            self.assertTrue(item.parent().isExpanded())
            self.assertTrue(item.parent().parent().isExpanded())
        self.assertTrue(pump.parent().parent().isHidden())
        self.assertEqual(folders.filter_tree(self.tree, core.CATALOG, 'not a component name'), [])
        visible = folders.filter_tree(self.tree, core.CATALOG, '')
        self.assertEqual(len(visible), len(core.CATALOG))
        after = {tuple(item.data(0, Qt.ItemDataRole.UserRole + 1)): item.isExpanded()
                 for item in folders._walk(self.tree) if not item.data(0, Qt.ItemDataRole.UserRole)}
        self.assertEqual(before, after)

    def test_search_folder_prefix_and_type_tokens(self):
        for query, expected in [('manual valves gate', 'gate_valve'),
                                ('gear_pump', 'gear_pump'), ('pumps', 'pump')]:
            visible = folders.filter_tree(self.tree, core.CATALOG, query)
            self.assertIn(self.leaves[expected], visible)
        prefix = core.CATALOG['pressure_transmitter']['prefix']
        self.assertIn(self.leaves['pressure_transmitter'], folders.filter_tree(self.tree, core.CATALOG, prefix))


if __name__ == '__main__':
    unittest.main()
