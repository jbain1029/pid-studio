"""Drafting diagnostics; warnings describe review needs, not engineering approval."""
from collections import defaultdict
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QListWidgetItem
import pidcore as core

def inspect(document):
    findings = []
    errors = core.validate(document)
    for error in errors:
        findings.append(('Error',None,error))
    if errors:
        return findings
    nodes = {c['id']:c for c in document['components']}
    used,labels,pairs = defaultdict(list),defaultdict(list),defaultdict(list)
    for line in document['connections']:
        for end in ('from','to'):
            endpoint = line[end]
            used[(endpoint['component'],endpoint['port'])].append(line['id'])
        if line['label'].strip():
            labels[line['label'].strip()].append(line)
        pair = tuple(sorted((e['component'],e['port']) for e in (line['from'],line['to'])))
        pairs[pair].append(line)
        if line['from']==line['to']:
            findings.append(('Warning',line['id'],'Line connects a port to itself'))
        a,b = (core.port_kind(document,line[e]) for e in ('from','to'))
        meanings = []
        for end in ('from','to'):
            endpoint = line[end]
            node = nodes[endpoint['component']]
            meaning = core.definition(node,document).get('port_meanings',{}).get(endpoint['port'])
            if meaning:
                meanings.append(f"{node['tag']}.{endpoint['port']}: {meaning}")
        if meanings:
            findings.append(('Review',line['id'],
                'Legacy attachment semantics: '+' '.join(meanings)+
                ' This link is stored as signal for file compatibility; its physical relationship and drawing notation require review.'))
        if line['kind']=='signal' and a==b=='process':
            findings.append(('Warning',line['id'],'Signal line has no signal port; confirm its endpoints'))
    for label,lines in labels.items():
        if len(lines)>1:
            # Segment labels can intentionally repeat; never block saving for this.
            findings.append(('Review',lines[0]['id'],f'Line number {label} appears on {len(lines)} segments; confirm continuity'))
    for lines in pairs.values():
        if len(lines)>1:
            findings.append(('Warning',lines[0]['id'],'Duplicate connections between the same ports'))
    for node in nodes.values():
        definition = core.definition(node,document)
        for port in definition['ports']:
            connections = used[(node['id'],port)]
            if not connections:
                findings.append(('Review',node['id'],f"{node['tag']}.{port} is unconnected; confirm it is intentionally open or unused"))
            elif len(connections)>1 and node['type']!='tee':
                findings.append(('Warning',node['id'],f"{node['tag']}.{port} has multiple lines; use an explicit tee for a branch"))
    return findings

def populate(window):
    window.messages.clear()
    findings = inspect(window.document)
    for pipe in window.pipes:
        if pipe.route_error:
            findings.append(('Warning',pipe.record['id'],pipe.route_error))
    if not findings:
        findings = [('Info',None,'No document or connectivity issues found by these drafting checks.')]
    for severity,identifier,text in findings:
        item = QListWidgetItem(f'{severity}: {text}')
        item.setData(Qt.ItemDataRole.UserRole,identifier)
        if severity=='Error':
            item.setForeground(QColor('#ad241e'))
        elif severity=='Warning':
            item.setForeground(QColor('#8a5700'))
        window.messages.addItem(item)
    window.statusBar().showMessage('Validation complete. Click a message to locate the associated component or connection.')

def install(window):
    def locate(item):
        identifier = item.data(Qt.ItemDataRole.UserRole)
        for candidate in window.scene.items():
            if hasattr(candidate,'record') and candidate.record['id']==identifier:
                window.scene.clearSelection()
                candidate.setSelected(True)
                window.view.ensureVisible(candidate)
                break
    window.messages.itemClicked.connect(locate)
