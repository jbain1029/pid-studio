import unittest
from pathlib import Path
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QPalette, QFontDatabase
from PySide6.QtWidgets import QComboBox, QDialog, QMenu, QVBoxLayout
from test_editor import APP
import classic


class LightPopupTests(unittest.TestCase):
    def setUp(self):
        for filename in ('segoeui.ttf','segoeuib.ttf'):
            QFontDatabase.addApplicationFont(str(Path('C:/Windows/Fonts')/filename))
        self.palette = APP.palette()
        self.stylesheet = APP.styleSheet()
        dark = QPalette()
        for role in (QPalette.Window,QPalette.Base,QPalette.Button):
            dark.setColor(role,QColor('#202020'))
        dark.setColor(QPalette.Text,QColor('white'))
        APP.setPalette(dark)
        classic.apply_theme(APP)

    def tearDown(self):
        APP.setStyleSheet(self.stylesheet)
        APP.setPalette(self.palette)

    def test_menu_and_combo_override_dark_system_palette(self):
        folder = Path(__file__).parent/'build'/'light-popups'
        folder.mkdir(parents=True,exist_ok=True)
        dialog = QDialog()
        layout = QVBoxLayout(dialog)
        combo = QComboBox()
        combo.addItems(['Process connection','Signal connection','Component port'])
        layout.addWidget(combo)
        dialog.resize(420,140)
        dialog.show()
        menu = QMenu(dialog)
        menu.setMinimumWidth(300)
        action = menu.addAction('Edit connection...')
        menu.addAction('Unavailable').setEnabled(False)
        menu.addSeparator()
        menu.addAction('Cancel')
        try:
            menu.popup(dialog.mapToGlobal(QPoint(10,20)))
            APP.processEvents()
            image = menu.grab().toImage()
            image.save(str(folder/'menu.png'))
            self.assertGreater(image.pixelColor(image.width()-15,10).lightness(),200)
            self.assertLess(menu.palette().color(QPalette.Text).lightness(),60)
            menu.setActiveAction(action)
            APP.processEvents()
            menu.grab().save(str(folder/'menu-selected.png'))
            menu.close()
            combo.showPopup()
            APP.processEvents()
            palette = combo.view().palette()
            self.assertGreater(palette.color(QPalette.Base).lightness(),200)
            self.assertLess(palette.color(QPalette.Text).lightness(),60)
            self.assertGreater(palette.color(QPalette.HighlightedText).lightness(),240)
            combo.view().window().grab().save(str(folder/'combo.png'))
        finally:
            combo.hidePopup()
            menu.close()
            dialog.close()
            APP.processEvents()
