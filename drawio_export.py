"""Editable draw.io objects with embedded vector artwork and attached edges."""
import base64
import copy
import json
import math
import xml.etree.ElementTree as ET
from PySide6.QtCore import QBuffer,QIODevice,QRectF,QSize
from PySide6.QtGui import QPainter
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QFileDialog,QMessageBox
import pidcore as core
import deliverables
from annotations import Note

def artwork(record,document=None):
    # Use the application's own renderer, so artwork cannot drift between exports.
    from app import Symbol
    class Context:
        exporting = True
        hide_external_tags = True
    context = Context()
    context.document = document
    symbol = Symbol(copy.deepcopy(record),context)
    symbol.setPos(0,0)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    generator = QSvgGenerator()
    generator.setOutputDevice(buffer)
    generator.setSize(QSize(100,100))
    generator.setViewBox(QRectF(-50,-50,100,100))
    painter = QPainter(generator)
    symbol.paint(painter,None,None)
    painter.end()
    return bytes(buffer.data())

def export(window,path):
    errors = core.validate(window.document)
    if errors:
        raise ValueError('\n'.join(errors))
    width,height,_ = deliverables.page_spec(window.document)
    file = ET.Element('mxfile',host='PID Studio',version='1')
    diagram = ET.SubElement(file,'diagram',id='pid-sheet',name=window.document['title'])
    graph = ET.SubElement(diagram,'mxGraphModel',grid='1',gridSize='10',page='1',pageScale='1',pageWidth=str(round(width*96/25.4)),pageHeight=str(round(height*96/25.4)))
    root = ET.SubElement(graph,'root')
    ET.SubElement(root,'mxCell',id='0')
    ET.SubElement(root,'mxCell',id='1',parent='0')
    bounds = window.scene.itemsBoundingRect()
    dx,dy = 60-bounds.left(),60-bounds.top()
    nodes = {r['id']:r for r in window.document['components']}
    def identifier(value):
        return 'pid-'+value
    for record in nodes.values():
        encoded = base64.b64encode(artwork(record,window.document)).decode()
        wrapper = ET.SubElement(root,'object',id=identifier(record['id']),label=record['tag'],pid_type=record['type'],description=record['description'],pid_metadata=json.dumps(record.get('metadata',{})))
        cell = ET.SubElement(wrapper,'mxCell',vertex='1',parent='1',style=f'shape=image;imageAspect=0;image=data:image/svg+xml,{encoded};verticalLabelPosition=bottom;verticalAlign=top;align=center;spacingTop=0;fontSize=12;html=0;whiteSpace=wrap;')
        x,y = record['position']
        ET.SubElement(cell,'mxGeometry',x=str(x-50+dx),y=str(y-50+dy),width='100',height='100',attrib={'as':'geometry'})
    for pipe in window.pipes:
        record = pipe.record
        style = 'edgeStyle=none;rounded=0;endArrow=none;startArrow=none;strokeWidth=2;html=0;'
        if record['kind']=='signal':
            style += 'dashed=1;'
        for end,prefix in [('from','exit'),('to','entry')]:
            endpoint = record[end]
            local = window.symbols[endpoint['component']].port_local(endpoint['port'])
            style += f'{prefix}X={(local.x()+50)/100};{prefix}Y={(local.y()+50)/100};{prefix}Perimeter=0;'
        wrapper = ET.SubElement(root,'object',id=identifier(record['id']),label=record['label'],pid_metadata=json.dumps(record.get('metadata',{})),pid_from_port=record['from']['port'],pid_to_port=record['to']['port'])
        cell = ET.SubElement(wrapper,'mxCell',edge='1',parent='1',source=identifier(record['from']['component']),target=identifier(record['to']['component']),style=style)
        geometry = ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
        points = ET.SubElement(geometry,'Array',attrib={'as':'points'})
        polygon = list(pipe.path().toSubpathPolygons()[0])
        for point in polygon[1:-1]:
            ET.SubElement(points,'mxPoint',x=str(point.x()+dx),y=str(point.y()+dy))
    for record in window.document.get('notes',[]):
        # Reuse the editor's wrapped text measurement, including its small safety
        # margin. Match its font and avoid draw.io's default label inset reducing
        # the available wrapping width.
        height = math.ceil(Note(record,window).boundingRect().height())
        cell = ET.SubElement(root,'mxCell',id=identifier(record['id']),value=record['text'],vertex='1',parent='1',style='text;html=0;whiteSpace=wrap;align=left;verticalAlign=top;fontFamily=Segoe UI;fontSize=13;spacing=0;')
        x,y = record['position']
        ET.SubElement(cell,'mxGeometry',x=str(x+dx),y=str(y+dy),width=str(record['width']),height=str(height),attrib={'as':'geometry'})
    ET.indent(file)
    ET.ElementTree(file).write(path,encoding='utf-8',xml_declaration=True)

def install(window):
    menu = next(a.menu() for a in window.menuBar().actions() if a.text()=='File')
    def save():
        path,_ = QFileDialog.getSaveFileName(window,'Export editable draw.io diagram','drawing.drawio','draw.io (*.drawio)')
        if path:
            try:
                export(window,path)
                window.statusBar().showMessage('Exported draw.io drawing. Components use embedded SVG artwork; labels and pipes are editable.')
            except (OSError,ValueError) as error:
                QMessageBox.warning(window,'Export failed',str(error))
    menu.addAction('Export draw.io…').triggered.connect(save)
