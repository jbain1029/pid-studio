"""Selection arrangement and consistent snap control."""
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QInputDialog
import math


def grid_spacing(window):
    """Keep visible dots on snap multiples while limiting density when zoomed out."""
    base = getattr(window,'snap_spacing',10)
    scale = max(.001,window.view.transform().m11())
    return base * max(1,math.ceil(8/(base*scale)))


def update_display(window):
    import classic
    window.view.viewport().update()
    classic.refresh_status(window)

def snap(window,value):
    spacing = getattr(window,'snap_spacing',10)
    return round(value/spacing)*spacing if getattr(window,'snap_enabled',True) else value

def arrange(window, mode):
    items = [i for i in window.scene.selectedItems() if hasattr(i,'record') and 'position' in i.record]
    if len(items)<2:
        window.statusBar().showMessage('Select at least two components to align.')
        return
    axis = 1 if mode in ('horizontal','distribute_vertical') else 0
    if mode.startswith('distribute') and len(items)<3:
        window.statusBar().showMessage('Select at least three components to distribute.')
        return
    window.checkpoint()
    if mode.startswith('distribute'):
        items.sort(key=lambda i:i.record['position'][axis])
        first,last = items[0].record['position'][axis],items[-1].record['position'][axis]
        values = [first+(last-first)*n/(len(items)-1) for n in range(len(items))]
    else:
        values = [sum(i.record['position'][axis] for i in items)/len(items)]*len(items)
    ids = [i.record['id'] for i in items]
    for item,value in zip(items,values):
        item.record['position'][axis] = snap(window,value)
    window.rebuild()
    for identifier in ids:
        for item in window.scene.items():
            if hasattr(item,'record') and item.record['id']==identifier:
                item.setSelected(True)

def install(window):
    window.snap_enabled,window.snap_spacing = True,10
    menu = window.menuBar().addMenu('Arrange')
    for label,mode in [('Align horizontally','horizontal'),('Align vertically','vertical'),('Distribute horizontally','distribute_horizontal'),('Distribute vertically','distribute_vertical')]:
        action = menu.addAction(label)
        action.triggered.connect(lambda checked=False,m=mode:arrange(window,m))
    menu.addSeparator()
    action = menu.addAction('Snap to grid')
    action.setCheckable(True)
    action.setChecked(True)
    action.toggled.connect(lambda on:(setattr(window,'snap_enabled',on),update_display(window)))
    def spacing():
        value,ok = QInputDialog.getInt(window,'Snap spacing','Canvas units',window.snap_spacing,1,100)
        if ok:
            window.snap_spacing = value
            update_display(window)
    menu.addAction('Snap spacing…').triggered.connect(spacing)
