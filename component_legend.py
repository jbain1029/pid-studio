"""Drawing-specific SVG legend using the exact shared component artwork."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
from PySide6.QtGui import QFont, QFontMetricsF

import pidcore as core
import drawio_export

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def wrapped(value, width, bold=False):
    font = QFont('Segoe UI')
    font.setPixelSize(14)
    font.setBold(bold)
    metrics = QFontMetricsF(font)
    lines = []
    for paragraph in value.splitlines() or ['']:
        remaining = paragraph
        while remaining:
            count = 0
            while count < len(remaining) and metrics.horizontalAdvance(remaining[:count+1]) <= width:
                count += 1
            count = max(1,count)
            if count < len(remaining) and ' ' in remaining[:count]:
                count = remaining.rfind(' ',0,count)+1
            lines.append(remaining[:count])
            remaining = remaining[count:]
    return lines or ['']


def entries(document):
    catalog = core.catalog_for(document)
    kinds = sorted({c['type'] for c in document['components']},
                   key=lambda kind: (catalog[kind]['category'], catalog[kind]['label'], kind))
    return [(kind, catalog[kind]) for kind in kinds]


def artwork(document):
    """Return a self-contained SVG without changing the drawing or its tags."""
    rows = entries(document)
    if not rows:
        raise ValueError('Add components before exporting a component legend.')
    root = ET.Element(f'{{{NS}}}svg', {'version':'1.1', 'width':'1000'})
    ET.SubElement(root, f'{{{NS}}}title').text = 'Component legend - ' + document['title']
    digest = hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=False,
                                      separators=(',', ':')).encode('utf-8')).hexdigest()
    library_digest = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False,
                                              separators=(',', ':')).encode('utf-8')).hexdigest()
    ET.SubElement(root, f'{{{NS}}}metadata').text = json.dumps({
        'format':'pid-studio-component-legend', 'version':1,
        'drawing_sha256':digest, 'library_sha256':library_digest,
        'types':[kind for kind,_ in rows]})
    background = ET.SubElement(root, f'{{{NS}}}rect',
                              {'width':'1000', 'fill':'white'})

    def text(x, y, value, size=14, bold=False):
        attrs = {'x':str(x), 'y':str(y), 'font-family':'Segoe UI, sans-serif',
                 'font-size':str(size), 'fill':'#202020'}
        if bold:
            attrs['font-weight'] = 'bold'
        ET.SubElement(root, f'{{{NS}}}text', attrs).text = value

    text(24, 30, 'COMPONENT LEGEND', 20, True)
    y = 55
    header = [document['title'],
        'Project reference variants; not a standards-compliance certificate.',
        'Function and technology are distinct. Instance tags and operating states are on the drawing.',
        'Artwork shown at zero rotation. Ports and leads rotate; functional lettering stays upright.',
        'Issue this legend with its matching drawing; regenerate after component or library changes.']
    basis = document.get('metadata', {}).get('drawing_basis')
    if basis:
        header.insert(1, 'Project drafting specification: ' + basis)
    for paragraph in header:
        for line in wrapped(paragraph, 930):
            text(24, y, line)
            y += 20
    y += 12
    for kind, definition in rows:
        lines = [(line,True) for line in wrapped(definition['label'],800,True)]
        lines.extend((line,False) for line in wrapped(definition['category']+' / '+kind,800))
        if definition.get('legend_reference'):
            note = 'Selected chart entry (adapted where noted): '+definition['legend_reference']
        elif definition.get('symbol_reference'):
            note = 'Source convention (adapted where noted): '+definition['symbol_reference']
        elif definition.get('symbol_notes'):
            note = 'Adopted project convention described below; no exact supplied-chart match claimed.'
        else:
            note = 'Project artwork: no exact supplied-chart match claimed. Verify the adopted convention.'
        lines.extend((line, False) for line in wrapped(note,800))
        for port, meaning in definition.get('port_meanings',{}).items():
            lines.extend((line,False) for line in wrapped('Attachment '+port+': '+meaning,800))
        if definition.get('port_meanings'):
            lines.extend((line,False) for line in wrapped(
                'Illustrative attachment handles do not support new line connections. Use a drawing note; any retained legacy link requires review.',800))
        for meaning in definition.get('symbol_notes',[]):
            lines.extend((line,False) for line in wrapped('Convention: '+meaning,800))
        row_height = max(120, 24 + 20*len(lines))
        ET.SubElement(root, f'{{{NS}}}line', {'x1':'24','x2':'976',
            'y1':str(y),'y2':str(y),'stroke':'#888','stroke-width':'1'})
        record = core.component(kind, 0, 0, document)
        record['tag'] = ''
        symbol = ET.fromstring(drawio_export.artwork(record, document))
        vx,vy,vw,vh = map(float,symbol.attrib['viewBox'].split())
        # Flatten the viewport: Qt SVG accepts nested SVG XML but can omit its
        # artwork. A transformed group renders in both Qt and browser engines.
        group = ET.SubElement(root, f'{{{NS}}}g', {'data-component':kind,
            'transform':f'translate(30 {y+10}) scale({100/vw} {100/vh}) translate({-vx} {-vy})'})
        for child in symbol:
            if child.tag.rsplit('}',1)[-1] not in ('title','desc','metadata'):
                group.append(child)
        for index, (line, bold) in enumerate(lines):
            # Labels from custom libraries are data; never raw XML/HTML.
            text(150, y+24+index*20, line, bold=bold)
        y += row_height
    text(24, y+22, 'Drawing fingerprint: '+digest, 12)
    text(24, y+40, 'Component library fingerprint: '+library_digest, 12)
    height = y+58
    root.set('height', str(height))
    root.set('viewBox', f'0 0 1000 {height}')
    background.set('height', str(height))
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def export(document, path):
    data = artwork(copy.deepcopy(document))
    destination = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.legend-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def choose_export(window):
    from PySide6.QtWidgets import QFileDialog, QMessageBox
    path, _ = QFileDialog.getSaveFileName(window, 'Export component legend',
                                        'component-legend.svg', 'SVG (*.svg)')
    if not path:
        return
    try:
        export(window.document, path)
        window.statusBar().showMessage('Component legend exported. Keep it with the matching drawing.')
    except (OSError, ValueError) as error:
        QMessageBox.warning(window, 'Legend export failed', str(error))
