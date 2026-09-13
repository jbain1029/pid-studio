"""Reproducible full-catalog SVG raster audit (not a symbology certificate)."""
import argparse
import copy
import hashlib
import html
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QFont, QFontDatabase, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication
import pidcore as core
from app import Symbol
import custom_symbols
import drawio_export


def ink(image):
    gray = image.convertToFormat(QImage.Format.Format_Grayscale8)
    data = bytes(gray.constBits())
    width, height, stride = gray.width(), gray.height(), gray.bytesPerLine()
    return {(x, y) for y in range(height) for x in range(width)
            if data[y*stride+x] < 160}


def expanded(points):
    return {(x+dx,y+dy) for x,y in points for dx,dy in
            ((0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))}


def direct(record, document, size=200, extent=100):
    class Context:
        exporting = True
        hide_external_tags = True
    context = Context()
    context.document = document
    image = QImage(size,size,QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.white)
    painter = QPainter(image)
    painter.translate(size/2,size/2)
    painter.scale(size/extent,size/extent)
    Symbol(copy.deepcopy(record),context).paint(painter,None,None)
    painter.end()
    return image


def inspect(record, document):
    data = drawio_export.artwork(record,document)
    root = ET.fromstring(data)
    renderer = QSvgRenderer(data)
    raster = QImage(200,200,QImage.Format.Format_ARGB32)
    raster.fill(Qt.GlobalColor.white)
    painter = QPainter(raster)
    renderer.render(painter,QRectF(0,0,200,200))
    painter.end()
    expected = ink(direct(record,document))
    actual = ink(raster)
    missing = expected-expanded(actual)
    extra = actual-expanded(expected)
    wide = ink(direct(record,document,240,120))
    outside = {(x,y) for x,y in wide if x<20 or y<20 or x>=220 or y>=220}
    external = [value for node in root.iter() for key,value in node.attrib.items()
                if key.rsplit('}',1)[-1]=='href' and not value.startswith('#')]
    result = {'type':record['type'],'rotation':record['rotation'],
              'valid':renderer.isValid(), 'ink_pixels':len(actual),
              'missing_fraction':len(missing)/max(1,len(expected)),
              'extra_fraction':len(extra)/max(1,len(actual)),
              'clipped_pixels':len(outside), 'external_resources':external,
              'svg_sha256':hashlib.sha256(data).hexdigest()}
    result['passed'] = (result['valid'] and len(actual)>20 and not outside
                        and not external and result['missing_fraction']<0.03
                        and result['extra_fraction']<0.03)
    return result,data,raster


def run(folder):
    application = QApplication.instance() or QApplication([])
    for name in ('segoeui.ttf','segoeuib.ttf'):
        QFontDatabase.addApplicationFont('C:/Windows/Fonts/'+name)
    application.setFont(QFont('Segoe UI',9))
    folder = Path(folder)
    folder.mkdir(parents=True,exist_ok=False)
    (folder/'svg').mkdir()
    document = custom_symbols.merge(core.new_document(),custom_symbols.fixture())
    catalog = core.catalog_for(document)
    results, sheets, browser_rows = [], [], []
    for offset in range(0,len(catalog),10):
        kinds = list(catalog)[offset:offset+10]
        sheet = QImage(1100,70+len(kinds)*150,QImage.Format.Format_ARGB32)
        sheet.fill(Qt.GlobalColor.white)
        painter = QPainter(sheet)
        painter.setFont(QFont('Segoe UI',9))
        painter.drawText(QRectF(0,0,1100,35),Qt.AlignmentFlag.AlignCenter,
                         'Actual exported SVG artwork — rotations 0 / 90 / 180 / 270')
        for row,kind in enumerate(kinds):
            browser_cells = []
            painter.drawText(QRectF(5,45+row*150,290,140),Qt.TextFlag.TextWordWrap,
                             kind+'\n'+catalog[kind]['label'])
            record = core.component(kind,0,0,document)
            for column,rotation in enumerate((0,90,180,270)):
                record['rotation'] = rotation
                result,data,raster = inspect(record,document)
                results.append(result)
                filename = kind.replace(':','_')+'-'+str(rotation)+'.svg'
                (folder/'svg'/filename).write_bytes(data)
                browser_cells.append('<td><img width="140" height="140" src="svg/'+html.escape(filename)+'" alt="'+html.escape(kind)+' '+str(rotation)+'"></td>')
                painter.drawImage(QRectF(310+column*190,40+row*150,140,140),raster)
            browser_rows.append('<tr><th>'+html.escape(kind)+'<br>'+html.escape(catalog[kind]['label'])+'</th>'+''.join(browser_cells)+'</tr>')
        painter.end()
        filename = f'sheet-{offset//10+1:02d}.png'
        sheet.save(str(folder/filename))
        sheets.append(filename)
    report = {'scope':{'builtins':len(core.CATALOG),'custom_fixtures':len(catalog)-len(core.CATALOG),
                       'rotations':[0,90,180,270],'raster_size':200},
              'method':'Qt SVG raster vs direct painter, one-pixel edge tolerance; 3% ink threshold; expanded viewport clipping check',
              'limitations':'Raster fidelity does not verify industry semantics or every third-party SVG engine.',
              'passed':all(row['passed'] for row in results),
              'sheets':sheets,'results':results}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (folder/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>SVG catalog audit</title><style>body{font:14px Arial;color:#111;background:white}table{border-collapse:collapse}th{width:280px;text-align:left}td,th{border-bottom:1px solid #aaa;padding:4px}img{display:block}</style><h1>SVG catalog audit</h1><p>All built-ins and one custom fixture. Columns: 0, 90, 180, 270 degrees. Images are actual SVG exports.</p><table>'+''.join(browser_rows)+'</table></html>',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'cases':len(results),
                      'failures':[row for row in results if not row['passed']],
                      'folder':str(folder.resolve())},indent=2))
    return report


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.folder)['passed'] else 1)
