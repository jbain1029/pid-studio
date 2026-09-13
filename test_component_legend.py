import copy
import json
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from test_deliverables import APP
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import Qt
import component_legend
import custom_symbols
import pidcore as core


class ComponentLegendTests(unittest.TestCase):
    def test_primary_source_is_not_mislabeled_as_supplied_chart(self):
        from app import Symbol
        from types import SimpleNamespace
        document = core.new_document()
        record = core.component('pump',0,0,document)
        document['components'].append(record)
        definition = copy.deepcopy(core.CATALOG['pump'])
        definition.pop('legend_reference',None)
        definition['symbol_reference'] = 'Published primary convention, figure 1'
        with patch.dict(core.CATALOG,{'pump':definition}):
            data = component_legend.artwork(document)
            tooltip = Symbol(record,SimpleNamespace(document=document)).toolTip()
        self.assertIn(b'Source convention (adapted where noted)',data)
        self.assertNotIn(b'Selected chart entry',data)
        self.assertIn('Published primary convention',tooltip)
        self.assertNotIn('pid-legend.pdf',tooltip)

    def test_long_unbroken_labels_wrap_without_losing_characters(self):
        value = 'W'*160
        lines = component_legend.wrapped(value,800,True)
        self.assertGreater(len(lines),1)
        self.assertEqual(''.join(lines),value)

    def test_all_components_render_once_and_document_unchanged(self):
        document = core.new_document()
        for kind in core.CATALOG:
            document['components'].append(core.component(kind,0,0,document))
        document['components'].append(core.component('pump',100,0,document))
        before = copy.deepcopy(document)
        data = component_legend.artwork(document)
        root = ET.fromstring(data)
        ns = '{'+component_legend.NS+'}'
        self.assertEqual(len([g for g in root.findall(ns+'g') if 'data-component' in g.attrib]), len(core.CATALOG))
        metadata = json.loads(root.find(ns+'metadata').text)
        self.assertEqual(set(metadata['types']), set(core.CATALOG))
        self.assertTrue(QSvgRenderer(data).isValid())
        self.assertEqual(document,before)
        self.assertEqual(data,component_legend.artwork(document))

    def test_symbol_ink_is_visible_not_just_valid_svg(self):
        document = core.new_document()
        document['components'].append(core.component('pump',0,0,document))
        renderer = QSvgRenderer(component_legend.artwork(document))
        image = QImage(renderer.defaultSize(),QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        # Text begins at x=150 and horizontal rules are gray. Only actual
        # symbol ink can satisfy this region/threshold assertion.
        group = ET.fromstring(component_legend.artwork(document)).find('{'+component_legend.NS+'}g')
        top = int(re.search(r'translate\(30 (\d+)\)',group.attrib['transform']).group(1))
        pixels = sum(image.pixelColor(x,y).red()<100 for x in range(30,131)
                     for y in range(top,top+100))
        self.assertGreater(pixels,100)

    def test_library_fingerprint_tracks_builtin_changes_independently_of_drawing(self):
        document = core.new_document()
        document['components'].append(core.component('pump',0,0,document))
        def metadata():
            return json.loads(ET.fromstring(component_legend.artwork(document)).find(
                '{'+component_legend.NS+'}metadata').text)
        before = metadata()
        changed = copy.deepcopy(core.CATALOG['pump'])
        changed['label'] += ' - revised drawing convention'
        with patch.dict(core.CATALOG,{'pump':changed}):
            after = metadata()
        self.assertEqual(before['drawing_sha256'],after['drawing_sha256'])
        self.assertNotEqual(before['library_sha256'],after['library_sha256'])

    def test_every_builtin_is_visible_in_the_combined_legend(self):
        document = core.new_document()
        document['components'] = [core.component(kind,0,0,document) for kind in core.CATALOG]
        data = component_legend.artwork(document)
        renderer = QSvgRenderer(data)
        image = QImage(renderer.defaultSize(),QImage.Format.Format_ARGB32)
        self.assertFalse(image.isNull())
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        groups = ET.fromstring(data).findall('{'+component_legend.NS+'}g')
        for group in groups:
            kind = group.attrib['data-component']
            top = int(re.search(r'translate\(30 (\d+)\)',group.attrib['transform']).group(1))
            pixels = sum(image.pixelColor(x,y).red()<100 for x in range(30,131)
                         for y in range(top,top+100))
            with self.subTest(kind=kind):
                self.assertGreater(pixels,20)

    def test_custom_text_is_escaped_and_uses_embedded_artwork(self):
        envelope = custom_symbols.fixture()
        envelope['definition']['label'] = 'Sight glass <review> & verify'
        document = custom_symbols.merge(core.new_document(),envelope)
        document['components'].append(core.component(envelope['kind'],0,0,document))
        data = component_legend.artwork(document)
        self.assertIn(b'&lt;review&gt; &amp; verify',data)
        self.assertTrue(QSvgRenderer(data).isValid())

    def test_empty_drawing_does_not_overwrite_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'legend.svg'
            document = core.new_document()
            document['components'].append(core.component('pump',0,0,document))
            component_legend.export(document,path)
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                component_legend.export(core.new_document(),path)
            self.assertEqual(path.read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
