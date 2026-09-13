"""Shared, UI-independent document model for humans and future AI importers."""
import copy
import json
import os
import tempfile
import uuid
from pathlib import Path

CATALOG = {
    "tank": {"label": "Tank", "prefix": "TK", "ports": {"inlet": [-40, 0], "outlet": [40, 0]}},
    "pump": {"label": "Centrifugal pump", "prefix": "P", "ports": {"inlet": [-40, 0], "outlet": [40, 0]}},
    "valve": {"label": "Isolation valve", "prefix": "HV", "ports": {"inlet": [-40, 0], "outlet": [40, 0]}},
    "check_valve": {"label": "Check valve", "prefix": "CV", "ports": {"inlet": [-40, 0], "outlet": [40, 0]}},
    "control_valve": {"label": "Control valve", "prefix": "FV", "ports": {"inlet": [-40, 0], "outlet": [40, 0], "signal": [0, -38]}},
    "filter": {"label": "Filter", "prefix": "F", "ports": {"inlet": [-40, 0], "outlet": [40, 0]}},
    "exchanger": {"label": "Heat exchanger", "prefix": "HX", "ports": {"inlet": [-40, 0], "outlet": [40, 0], "utility_in": [0, -30], "utility_out": [0, 30]}},
    "instrument": {"label": "Instrument", "prefix": "PI", "ports": {"process": [0, 30], "signal": [0, -30]}},
    "tee": {"label": "Junction / tee", "prefix": "J", "ports": {"left": [-40, 0], "right": [40, 0], "branch": [0, -30]}},
    "connector": {"label": "Off-page connector", "prefix": "OP", "ports": {"inlet": [-40, 0], "outlet": [40, 0]}},
}

# Category and ports are shared by the toolbox, validator and AI authoring context.
CATALOG['filter']['symbol_notes'] = [
    'Adopted generic filtration body. The solid diagonal is a filter mark, not '
    'a specified medium, filter technology or separate internal flow path.']
CATALOG['connector']['symbol_notes'] = [
    'Graphic-only off-page continuation. Add a drawing note identifying the '
    'destination sheet/drawing and counterpart; this graphic does not create '
    'automatic connectivity between documents.']
for _kind, _definition in CATALOG.items():
    _definition['category'] = ('Instrumentation' if _kind == 'instrument' else 'Piping & Connections' if _kind in ('tee','connector') else 'Valves & Actuators' if 'valve' in _kind else 'Process Equipment')
CATALOG.update({
    'vessel': {'label':'Pressure vessel','prefix':'V','category':'Process Equipment','ports':{'inlet':[-40,0],'outlet':[40,0],'vent':[0,-40],'drain':[0,40]}},
    'gear_pump': {'label':'Positive-displacement pump','prefix':'P','category':'Process Equipment','ports':{'inlet':[-40,0],'outlet':[40,0]}},
    'compressor': {'label':'Compressor','prefix':'K','category':'Process Equipment','ports':{'inlet':[-40,0],'outlet':[40,0]}},
    'ball_valve': {'label':'Ball valve','prefix':'HV','category':'Valves & Actuators','ports':{'inlet':[-40,0],'outlet':[40,0]}},
    'butterfly_valve': {'label':'Butterfly valve','prefix':'HV','category':'Valves & Actuators','ports':{'inlet':[-40,0],'outlet':[40,0]}},
    'relief_valve': {'label':'Pressure relief valve','prefix':'PSV','category':'Valves & Actuators','ports':{'inlet':[-40,0],'outlet':[40,0]}},
    'reducer': {'label':'Reducer','prefix':'R','category':'Piping & Connections','ports':{'inlet':[-40,0],'outlet':[40,0]}},
    'strainer': {'label':'Y-strainer','prefix':'ST','category':'Piping & Connections','ports':{'inlet':[-40,0],'outlet':[40,0]}},
    'controller': {'label':'Panel controller','prefix':'PIC','category':'Instrumentation','ports':{'input':[0,-40],'signal':[0,40]}},
})

for _kind, _definition in CATALOG.items():
    _definition['port_kinds'] = {name:'signal' if name=='signal' or _kind=='controller' else 'process' for name in _definition['ports']}

# Local body/actuator envelopes, excluding nozzle leads and upright tag text.
# Ports on an envelope boundary remain accessible to the orthogonal router.
_ROUTING_BOUNDS = {
    'tank': [-29,-37,29,31], 'pump': [-27,-27,27,27],
    'valve': [-23,-17,23,17], 'check_valve': [-23,-19,25,19],
    'control_valve': [-23,-38,23,17], 'filter': [-26,-22,26,22],
    'exchanger': [-27,-27,27,27], 'instrument': [-27,-27,27,27],
    'tee': [-5,-5,5,5], 'connector': [-26,-16,31,16],
    'vessel': [-25,-33,25,33], 'gear_pump': [-29,-26,29,26],
    'compressor': [-28,-28,28,28], 'ball_valve': [-23,-29,23,17],
    'butterfly_valve': [-24,-24,24,24], 'relief_valve': [-21,-41,21,16],
    'reducer': [-25,-19,25,19], 'strainer': [-24,-11,24,30],
    'controller': [-26,-26,26,26],
}
for _kind, _bounds in _ROUTING_BOUNDS.items():
    CATALOG[_kind]['routing_bounds'] = _bounds

# Original declarative artwork shares the component renderer and port contract.
# Preserve original identifiers for existing drawings.
from catalog_process import CATALOG as _PROCESS
from catalog_valves import CATALOG as _VALVES
from catalog_instruments import CATALOG as _INSTRUMENTS
from catalog_rankine import CATALOG as _RANKINE
for _extension in (_PROCESS, _VALVES, _INSTRUMENTS, _RANKINE):
    if CATALOG.keys() & _extension.keys():
        raise ValueError('Duplicate built-in component identifiers')
    CATALOG.update(copy.deepcopy(_extension))

# Project-reference artwork overlays leave portable/custom definition schemas
# and the original component/port contracts unchanged.
from legend_instruments import apply as _legend_instruments
from legend_process import apply as _legend_process
from legend_valves import apply as _legend_valves
for _apply_legend in (_legend_instruments, _legend_process, _legend_valves):
    _apply_legend(CATALOG)



def catalog_for(document=None):
    """Return the built-in catalog plus this drawing's portable definitions."""
    return {**CATALOG, **(document or {}).get('symbol_definitions', {})}


def definition(record, document=None):
    return catalog_for(document)[record['type']]


def routing_bounds(record, position=None, document=None):
    left, top, right, bottom = definition(record, document)['routing_bounds']
    corners = [(left,top),(right,top),(right,bottom),(left,bottom)]
    for _ in range(record['rotation']//90):
        corners = [(-y,x) for x,y in corners]
    x, y = record['position'] if position is None else position
    return (min(p[0] for p in corners)+x, min(p[1] for p in corners)+y,
            max(p[0] for p in corners)+x, max(p[1] for p in corners)+y)

def port_kind(document, endpoint):
    node = next((c for c in document['components'] if c['id']==endpoint['component']),None)
    return catalog_for(document).get(node['type'],{}).get('port_kinds',{}).get(endpoint['port']) if node else None

def uid():
    return uuid.uuid4().hex[:12]

def new_document():
    return {"format": "pid-studio", "version": 1, "title": "Untitled P&ID", "components": [], "connections": []}

def component(kind, x, y, document):
    prefix = catalog_for(document)[kind]["prefix"]
    tags = {c["tag"] for c in document["components"]}
    n = 101
    while f"{prefix}-{n}" in tags:
        n += 1
    return {"id": uid(), "type": kind, "tag": f"{prefix}-{n}", "description": "", "position": [x, y], "rotation": 0}

def validate(document):
    from jsonschema import Draft202012Validator
    schema = json.loads(Path(__file__).with_name("document.schema.json").read_text(encoding="utf-8"))
    errors = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in Draft202012Validator(schema).iter_errors(document)]
    if errors:
        return errors
    from custom_symbols import definition_errors
    for kind, symbol in document.get('symbol_definitions', {}).items():
        errors.extend(f'{kind}: {error}' for error in definition_errors(symbol))
    catalog = catalog_for(document)
    nodes = {c["id"]: c for c in document["components"]}
    ids = [c["id"] for c in document["components"] + document["connections"] + document.get('notes',[])]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate object IDs")
    tags = [c["tag"] for c in document["components"]]
    if len(tags) != len(set(tags)):
        errors.append("Duplicate component tags")
    for c in nodes.values():
        if c["type"] not in catalog:
            errors.append(f"Unknown component type: {c['type']}")
    for line in document["connections"]:
        for end in ("from", "to"):
            ref = line[end]
            node = nodes.get(ref["component"])
            if not node or ref["port"] not in catalog.get(node["type"], {}).get("ports", {}):
                errors.append(f"Invalid endpoint on {line['id']}: {end}")
        signal_ports = [port_kind(document,line[e]) == 'signal' for e in ('from','to')]
        if any(signal_ports) and line["kind"] != "signal":
            errors.append(f"Signal port needs a signal connection: {line['id']}")
    return errors

def save(document, path):
    errors = validate(document)
    if errors:
        raise ValueError("\n".join(errors))
    path = Path(path)
    fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(document, f, indent=2, allow_nan=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def load(path):
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate(document)
    if errors:
        raise ValueError("\n".join(errors))
    return document

def apply_proposal(document, proposal):
    """Validate a complete draft without touching the current document."""
    from operations import fingerprint
    if proposal.get('base_fingerprint') != fingerprint(document):
        raise ValueError('Draft must reference the current document fingerprint')
    if proposal.get("base_revision") != document.get("revision", 0):
        raise ValueError("Proposal is based on an older document revision")
    draft = copy.deepcopy(proposal["document"])
    errors = validate(draft)
    if errors:
        raise ValueError("\n".join(errors))
    draft["revision"] = document.get("revision", 0) + 1
    return draft
