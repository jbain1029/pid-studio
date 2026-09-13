import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase,QImage,QPainter,QFont
from PySide6.QtWidgets import QGraphicsScene
from test_editor import APP
from app import Window,Symbol
import pidcore as core
import routing
import operations
import deliverables
from component_browser import CatalogDialog


class ExpandedCatalogTests(unittest.TestCase):
    def test_every_port_is_clear_in_each_rotation(self):
        self.assertEqual(len(core.CATALOG),141)
        for kind,definition in core.CATALOG.items():
            if 'artwork' not in definition:
                continue # Existing legacy geometry is covered separately.
            for rotation in (0,90,180,270):
                record={'type':kind,'position':[0,0],'rotation':rotation}
                box=core.routing_bounds(record)
                for name,point in definition['ports'].items():
                    with self.subTest(kind=kind,rotation=rotation,port=name):
                        x,y=point
                        for _ in range(rotation//90):x,y=-y,x
                        dx,dy=((1 if x>0 else -1),0) if abs(x)>abs(y) else (0,1 if y>0 else -1)
                        end=(x+200*dx,y+200*dy)
                        route=routing.route((x,y),end,(dx,dy),(-dx,-dy),[box])
                        self.assertEqual(route[0],(x,y))
                        self.assertEqual(route[-1],end)
                        self.assertTrue(all(routing.clear(a,b,[box]) for a,b in zip(route,route[1:])))

    def test_catalog_browser_search_insert_and_undo(self):
        window=Window()
        try:
            before=copy.deepcopy(window.document)
            browser=CatalogDialog(window)
            browser.show()
            APP.processEvents()
            self.assertFalse(browser.insert.isEnabled())
            folder = browser.list.topLevelItem(0)
            browser.list.setCurrentItem(folder)
            browser.list.itemDoubleClicked.emit(folder,0)
            self.assertFalse(browser.insert.isEnabled())
            self.assertEqual(window.document,before)
            self.assertTrue(browser.isVisible())
            browser.search.setText('gate valve')
            scene_rect = browser.scene.sceneRect()
            self.assertTrue(browser.view.viewport().rect().contains(browser.view.mapFromScene(scene_rect.topLeft())))
            self.assertTrue(browser.view.viewport().rect().contains(browser.view.mapFromScene(scene_rect.bottomRight())))
            visible=[item.text(0) for item in browser.leaves.values() if not item.isHidden()]
            self.assertIn('Gate valve',visible)
            browser.insert_component()
            self.assertEqual(len(window.document['components']),1)
            window.undo()
            self.assertEqual(window.document,before)
            browser=CatalogDialog(window)
            browser.search.setText('no-such-component-xyz')
            self.assertFalse(browser.insert.isEnabled())
            browser.reject()
            window.palette.filter_symbols('PT')
            self.assertTrue(any(not window.palette.topLevelItem(i).isHidden() for i in range(window.palette.topLevelItemCount())))
        finally:
            window.saved=copy.deepcopy(window.document)
            window.close()

    def test_all_types_roundtrip_context_reports_and_gallery(self):
        window=Window()
        try:
            for index,kind in enumerate(core.CATALOG):
                window.document['components'].append(core.component(kind,(index%10)*160,(index//10)*180,window.document))
            self.assertEqual(core.validate(window.document),[])
            self.assertEqual(set(operations.context(window.document)['catalog']),set(core.CATALOG))
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'all.pid'
                core.save(window.document,path)
                self.assertEqual(core.load(path),window.document)
                for category,prefix in [('valves','Valves'),('instruments','Instrumentation')]:
                    report=Path(folder)/(category+'.csv')
                    deliverables.export_register(window,report,category)
                    with report.open(encoding='utf-8-sig',newline='') as stream:
                        rows=list(csv.DictReader(stream))
                    self.assertEqual(len(rows),sum(d['category'].startswith(prefix) for d in core.CATALOG.values()))
            folder=Path(__file__).parent/'build'/'catalog-gallery'
            folder.mkdir(parents=True,exist_ok=True)
            for font in ('segoeui.ttf','segoeuib.ttf'):
                QFontDatabase.addApplicationFont(str(Path('C:/Windows/Fonts')/font))
            groups={}
            for kind,definition in core.CATALOG.items():groups.setdefault(definition['category'],[]).append(kind)
            class Context:
                exporting=True
            context=Context()
            context.document=window.document
            for group,kinds in groups.items():
                scene=QGraphicsScene()
                for index,kind in enumerate(kinds):
                    x,y=(index%5)*220+110,(index//5)*180+68
                    record=copy.deepcopy(next(record for record in window.document['components'] if record['type']==kind))
                    record['position']=[x,y]
                    scene.addItem(Symbol(record,context))
                    label=scene.addText(core.CATALOG[kind]['label'])
                    font=QFont('Segoe UI');font.setPixelSize(13)
                    label.setFont(font);label.setTextWidth(208);label.setPos(x-104,y+70)
                width,height=1100,((len(kinds)+4)//5)*180
                scene.setSceneRect(0,0,width,height)
                image=QImage(width,height,QImage.Format_ARGB32);image.fill(Qt.white)
                painter=QPainter(image)
                scene.render(painter);painter.end()
                self.assertTrue(image.save(str(folder/(group.replace('/','-').replace('&','and')+'.png'))))
        finally:
            window.saved=copy.deepcopy(window.document)
            window.close()
