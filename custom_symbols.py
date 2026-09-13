"""Portable, declarative symbols. No executable scripts or external resources."""
import copy
import json
import math
import os
from pathlib import Path
import tempfile

from jsonschema import Draft202012Validator
from routing import clear

MAX_FILE_BYTES = 256 * 1024


def envelope_schema():
    document = json.loads(Path(__file__).with_name('document.schema.json').read_text(encoding='utf-8'))
    return {
        '$schema': document['$schema'], '$defs': document['$defs'],
        'type': 'object', 'additionalProperties': False,
        'required': ['format', 'version', 'kind', 'definition'],
        'properties': {
            'format': {'const': 'pid-studio-symbol'}, 'version': {'const': 1},
            'kind': {'type': 'string', 'pattern': '^custom:[a-z][a-z0-9_]{0,47}$'},
            'definition': {'$ref': '#/$defs/custom_symbol'},
        },
    }


def definition_errors(definition):
    """Semantic geometry checks, after the definition has passed JSON Schema."""
    errors = []
    left, top, right, bottom = definition['routing_bounds']
    if not all(math.isfinite(v) for v in (left, top, right, bottom)) or left >= right or top >= bottom:
        errors.append('Routing bounds must be finite with left < right and top < bottom')
    if definition['ports'].keys() != definition['port_kinds'].keys():
        errors.append('Port kinds must have exactly the same names as ports')
    seen = set()
    for name, (x, y) in definition['ports'].items():
        if not math.isfinite(x) or not math.isfinite(y):
            errors.append(f'Port {name} coordinates must be finite')
        if x == 0 and y == 0:
            errors.append(f'Port {name} must not be at the origin')
        if left < x < right and top < y < bottom:
            errors.append(f'Port {name} is inside the routing bounds')
        # The editor infers nozzle direction from the port's dominant radial
        # axis. An offset body must not block that mandatory outward stub.
        if math.isfinite(x) and math.isfinite(y):
            px, py = x, y
            box = tuple(definition['routing_bounds'])
            # Diagonal ties always choose the current screen Y axis, so the
            # choice at 90 degrees need not rotate the choice at zero degrees.
            for rotation in (0, 90, 180, 270):
                stub = ((px + (20 if px > 0 else -20), py) if abs(px) > abs(py)
                        else (px, py + (20 if py > 0 else -20)))
                if not clear((px, py), stub, [box]):
                    errors.append(f'Port {name} outward routing stub crosses the component body at {rotation} degrees')
                    break
                px, py = -py, px
                l, t, r, b = box
                box = (-b, l, -t, r)
        if (x, y) in seen:
            errors.append(f'Port {name} overlaps another port')
        seen.add((x, y))
    for index, primitive in enumerate(definition['artwork']):
        if primitive['kind'] in ('rect', 'ellipse'):
            x, y, width, height = primitive['rect']
            if (not all(math.isfinite(v) for v in primitive['rect'])
                    or width <= 0 or height <= 0 or x < -45 or y < -45
                    or x + width > 45 or y + height > 45):
                errors.append(f'Artwork {index} needs positive dimensions inside [-45, 45]')
        elif any(not math.isfinite(v) for point in primitive['points'] for v in point):
            errors.append(f'Artwork {index} coordinates must be finite')
    return errors


def validate(envelope):
    # Reject excessive nesting before schema error formatting can recurse into
    # malformed values; legitimate primitive envelopes need fewer than10 levels.
    pending = [(envelope, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > 16:
            return ['Component definition JSON is nested too deeply']
        if isinstance(value, dict):
            pending.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            pending.extend((item, depth + 1) for item in value)
    errors = [f"{'/'.join(map(str, e.path))}: {e.message}"
              for e in Draft202012Validator(envelope_schema()).iter_errors(envelope)]
    if not errors:
        errors.extend(definition_errors(envelope['definition']))
    return errors


def load(path):
    # Bound the actual read, not just a potentially stale filesystem stat.
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError('Component definition file exceeds 256 KB')
    try:
        envelope = json.loads(raw.decode('utf-8'))
    except RecursionError as error:
        raise ValueError('Component definition JSON is nested too deeply') from error
    errors = validate(envelope)
    if errors:
        raise ValueError('\n'.join(errors))
    return envelope


def save(envelope, path):
    errors = validate(envelope)
    if errors:
        raise ValueError('\n'.join(errors))
    raw = json.dumps(envelope, indent=2, allow_nan=False).encode('utf-8')
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError('Component definition file exceeds 256 KB')
    path = Path(path)
    fd, temporary = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def merge(document, envelope):
    """Copy a validated definition into a drawing, never silently replacing one."""
    import pidcore
    errors = validate(envelope)
    if errors:
        raise ValueError('\n'.join(errors))
    draft = copy.deepcopy(document)
    definitions = draft.setdefault('symbol_definitions', {})
    kind = envelope['kind']
    if kind in definitions and definitions[kind] != envelope['definition']:
        raise ValueError(f'A different definition already uses {kind}')
    definitions[kind] = copy.deepcopy(envelope['definition'])
    errors = pidcore.validate(draft)
    if errors:
        raise ValueError('\n'.join(errors))
    return draft


def fixture():
    """An editable starting point using the same safe primitives as user symbols."""
    return {'format': 'pid-studio-symbol', 'version': 1, 'kind': 'custom:sight_glass',
            'definition': {
                'label': 'Sight glass', 'prefix': 'SG', 'category': 'Custom Symbols',
                'ports': {'inlet': [-40, 0], 'outlet': [40, 0]},
                'port_kinds': {'inlet': 'process', 'outlet': 'process'},
                'routing_bounds': [-20, -15, 20, 15],
                'artwork': [
                    {'kind': 'rect', 'rect': [-20, -15, 40, 30]},
                    {'kind': 'line', 'points': [[-40, 0], [-20, 0]]},
                    {'kind': 'line', 'points': [[20, 0], [40, 0]]},
                    {'kind': 'line', 'points': [[-15, 10], [15, -10]]},
                ],
            }}
