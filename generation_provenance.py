"""Local request-time provenance. Never accepts headers, credentials or replies wholesale."""
import base64
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import operations
import pidcore


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def capture(document, body, payload):
    """Capture the actual prepared request, before submission; no network effects."""
    if json.loads(payload) != body:
        raise ValueError('Prepared request and serialized payload do not match.')
    content = body['input'][0]['content']
    text = json.loads(content[0]['text'])
    images = [item for item in content if item['type'] == 'input_image']
    if len(images) > 1:
        raise ValueError('Only one reference image is supported.')
    image_hash = None
    if images:
        prefix, encoded = images[0]['image_url'].split(',', 1)
        if prefix != 'data:image/png;base64':
            raise ValueError('Expected the locally prepared PNG image.')
        image_hash = sha256(base64.b64decode(encoded, validate=True))
    return {
        'version': 1, 'provider': 'openai', 'requested_at': now(), 'received_at': None,
        'requested_model': body['model'], 'response_model': None, 'response_id': None,
        'base_fingerprint': operations.fingerprint(document),
        'request_fingerprint': sha256(payload),
        'user_instruction_fingerprint': sha256(text['request'].encode('utf-8')),
        'instructions_fingerprint': sha256(body['instructions'].encode('utf-8')),
        'wire_schema_fingerprint': operations.fingerprint(body['text']['format']['schema']),
        'catalog_fingerprint': operations.fingerprint(text['catalog']),
        'document_schema_fingerprint': sha256(Path(pidcore.__file__).with_name('document.schema.json').read_bytes()),
        'image_included': bool(images), 'sent_image_fingerprint': image_hash,
        'input_tokens': None, 'output_tokens': None, 'total_tokens': None,
    }


def finish(captured, response):
    """Allowlist response metadata. Missing or malformed optional metadata stays unknown."""
    result = copy.deepcopy(captured)
    result['received_at'] = now()
    for source, target in (('id', 'response_id'), ('model', 'response_model')):
        value = response.get(source)
        result[target] = value if isinstance(value, str) and 0 < len(value) <= 256 else None
    usage = response.get('usage')
    if isinstance(usage, dict):
        for key in ('input_tokens', 'output_tokens', 'total_tokens'):
            value = usage.get(key)
            result[key] = value if type(value) is int and value >= 0 else None
    return result


def validate(generation, base_fingerprint):
    from jsonschema import Draft202012Validator
    schema = json.loads(Path(pidcore.__file__).with_name('document.schema.json').read_text())
    check = {'$ref': '#/$defs/generation_record', '$defs': schema['$defs']}
    errors = list(Draft202012Validator(check).iter_errors(generation))
    if errors:
        raise ValueError('Invalid generation record: ' + errors[0].message)
    if generation['base_fingerprint'] != base_fingerprint:
        raise ValueError('Generation record belongs to a different drawing state.')
    if generation['image_included'] != (generation['sent_image_fingerprint'] is not None):
        raise ValueError('Generation image flag and fingerprint disagree.')


def describe(record):
    if record is None:
        return 'GENERATION\nNo request-time provenance available (offline or older proposal).'
    return '\n'.join([
        'GENERATION — local record, not signed proof of provider processing',
        f"Requested: {record['requested_at']} | Received: {record['received_at'] or 'unknown'}",
        f"Requested model: {record['requested_model']} | Response model: {record['response_model'] or 'unknown'}",
        f"Response ID: {record['response_id'] or 'unknown'}",
        f"Image included in submitted payload: {'yes' if record['image_included'] else 'no'}",
        f"Submitted PNG SHA-256: {record['sent_image_fingerprint'] or 'none'}",
        f"Request body SHA-256: {record['request_fingerprint']}",
        f"User instructions SHA-256: {record['user_instruction_fingerprint']}",
        f"System instructions SHA-256: {record['instructions_fingerprint']}",
        f"Wire schema: {record['wire_schema_fingerprint']}",
        f"Request-time local validation schema (not sent in full): {record['document_schema_fingerprint']}",
        f"Request-time catalog: {record['catalog_fingerprint']}",
        f"Tokens (input/output/total): {record['input_tokens']} / {record['output_tokens']} / {record['total_tokens']}",
        'Only fingerprints are retained for request content; this is not a replayable request archive.',
    ])
