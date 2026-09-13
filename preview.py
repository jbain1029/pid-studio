"""Render a reproducible application preview and example document."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QTabWidget
import app
import pidcore
import deliverables
import sketch
import operations
import drawio_export

def capture():
    window = next(w for w in QApplication.topLevelWidgets() if isinstance(w, app.Window))
    window.example()
    window.validate()
    QApplication.processEvents()
    folder = Path(__file__).parent / 'examples'
    folder.mkdir(exist_ok=True)
    pidcore.save(window.document, folder / 'transfer-system.pid')
    window.export_to(folder / 'transfer-system.svg')
    drawio_export.export(window,folder/'transfer-system.drawio')
    deliverables.export_sheet(window, folder / 'transfer-system.png')
    deliverables.export_sheet(window, folder / 'transfer-system.pdf')
    window.grab().save(str(folder / 'editor-preview.png'))
    tabs = window.centralWidget().findChild(QTabWidget)
    tabs.setCurrentWidget(window.sheet_preview)
    QApplication.processEvents()
    window.sheet_preview.fit()
    window.grab().save(str(folder / 'sheet-preview.png'))
    tabs.setCurrentIndex(0)
    proposal = {'contract_version':1,'base_fingerprint':operations.fingerprint(window.document),'operations':[{'operation':'update_drawing','changes':{'title':'Transfer System — Reviewed Draft'}}],'issues':['Confirm pump tag against the original sketch.']}
    def review_capture():
        dialog = QApplication.activeModalWidget()
        dialog.grab().save(str(folder/'proposal-preview.png'))
        dialog.reject()
    QTimer.singleShot(200,review_capture)
    sketch.review(window,proposal)
    window.document = pidcore.new_document()
    window.document['title'] = 'PID Studio — Component Library'
    for index,kind in enumerate(pidcore.CATALOG):
        record = pidcore.component(kind,(index%5)*190,(index//5)*160,window.document)
        record['tag'] = pidcore.CATALOG[kind]['label']
        window.document['components'].append(record)
    window.rebuild()
    deliverables.export_sheet(window,folder/'component-library.png')
    window.saved = window.document.copy()
    QApplication.quit()

if __name__ == '__main__':
    # Schedule after the real application creates its styled window.
    original = app.Window.show
    def show(window):
        original(window)
        QTimer.singleShot(250, capture)
    app.Window.show = show
    app.main()
