"""Versioned transactional edits shared by future AI and document import."""
import copy
import hashlib
import json
from pathlib import Path
import pidcore as core

def fingerprint(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def context(document):
    schema = json.loads(Path(core.__file__).with_name('document.schema.json').read_text())
    return {'contract_version': 1, 'base_fingerprint': fingerprint(document),
            'document_schema': schema, 'proposal_schema': proposal_schema(),
            'instructions': (Path(__file__).parent/'ai'/'AUTHORING.md').read_text(encoding='utf-8'),
            'catalog': copy.deepcopy(core.catalog_for(document)), 'document': copy.deepcopy(document)}

def proposal_schema():
    definitions = json.loads(Path(core.__file__).with_name('document.schema.json').read_text())['$defs']
    variants = []
    for kind, collection in [('component','component'),('connection','connection')]:
        for verb in ('add','update','remove'):
            properties = {'operation':{'const':f'{verb}_{kind}'}}
            if verb == 'add':
                properties['value'] = {'$ref':f'#/$defs/{collection}'}
            else:
                properties['id'] = {'type':'string'}
            if verb == 'update':
                fields = copy.deepcopy(definitions[collection]['properties'])
                fields.pop('id')
                properties['changes'] = {'type':'object','additionalProperties':False,'properties':fields}
            variants.append({'type':'object','additionalProperties':False,'required':list(properties),'properties':properties})
    variants.append({'type':'object','additionalProperties':False,'required':['operation','changes'],'properties':{'operation':{'const':'update_drawing'},'changes':{'type':'object','additionalProperties':False,'properties':{'title':{'type':'string'},'metadata':{'$ref':'#/$defs/metadata'}}}}})
    region = {'type':'object','additionalProperties':False,'required':['x','y','width','height'],
              'properties':{key:{'type':'number','minimum':0,'maximum':1} for key in ('x','y','width','height')}}
    finding = {'type':'object','additionalProperties':False,'required':['id','message','region','object_ids'],
               'properties':{'id':{'type':'string','minLength':1},'message':{'type':'string','minLength':1},
                             'region':{'anyOf':[region,{'type':'null'}]},
                             'object_ids':{'type':'array','items':{'type':'string'},'uniqueItems':True}}}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','additionalProperties':False,
        'required':['contract_version','base_fingerprint','operations'], '$defs':definitions,
        'properties':{'contract_version':{'const':1},'base_fingerprint':{'type':'string','pattern':'^[a-f0-9]{64}$'},
            'operations':{'type':'array','maxItems':2000,'items':{'oneOf':variants}},'issues':{'type':'array','items':{'type':'string'}},
            'review_findings':{'type':'array','maxItems':200,'items':finding}}}

def apply(document, proposal):
    """Apply all operations to a copy, rejecting stale or invalid proposals atomically."""
    from jsonschema import Draft202012Validator
    failures = list(Draft202012Validator(proposal_schema()).iter_errors(proposal))
    if failures:
        raise ValueError('Invalid proposal: '+failures[0].message)
    if proposal.get('contract_version') != 1:
        raise ValueError('Unsupported edit contract version')
    if proposal.get('base_fingerprint') != fingerprint(document):
        raise ValueError('Drawing changed since this proposal was created. Generate a fresh proposal.')
    if set(proposal) - {'contract_version','base_fingerprint','operations','issues','review_findings'}:
        raise ValueError('Unknown proposal fields')
    identifiers = set()
    for finding in proposal.get('review_findings', []):
        if finding['id'] in identifiers:
            raise ValueError('Review finding IDs must be unique')
        identifiers.add(finding['id'])
        region = finding['region']
        if region and (region['width'] <= 0 or region['height'] <= 0 or
                       region['x']+region['width'] > 1 or region['y']+region['height'] > 1):
            raise ValueError('Review regions must be nonempty and within the source image')
        if region and not document.get('reference'):
            raise ValueError('A source-region finding requires an attached reference image')
    edits = proposal.get('operations')
    if not isinstance(edits,list) or len(edits)>2000:
        raise ValueError('Expected at most 2000 operations')
    draft = copy.deepcopy(document)
    for index, edit in enumerate(edits):
        if not isinstance(edit,dict):
            raise ValueError(f'Operation {index+1} must be an object')
        action = edit.get('operation')
        collection = 'components' if action in ('add_component','update_component','remove_component') else 'connections'
        if action in ('add_component','add_connection'):
            if set(edit) != {'operation','value'} or not isinstance(edit['value'],dict):
                raise ValueError('Add requires a value object')
            draft[collection].append(copy.deepcopy(edit['value']))
        elif action in ('update_component','update_connection'):
            if set(edit) != {'operation','id','changes'} or not isinstance(edit['changes'],dict):
                raise ValueError('Update requires id and changes')
            record = next((r for r in draft[collection] if r['id']==edit['id']),None)
            if record is None:
                raise ValueError(f"Unknown object {edit['id']}")
            if 'id' in edit['changes']:
                raise ValueError('IDs cannot be changed')
            record.update(copy.deepcopy(edit['changes']))
        elif action in ('remove_component','remove_connection'):
            if set(edit) != {'operation','id'}:
                raise ValueError('Remove requires id')
            if not any(r['id']==edit['id'] for r in draft[collection]):
                raise ValueError(f"Unknown object {edit['id']}")
            draft[collection] = [r for r in draft[collection] if r['id'] != edit['id']]
            # Referenced lines must be explicitly removed or reconnected by the proposal.
        elif action == 'update_drawing':
            if set(edit) != {'operation','changes'} or not isinstance(edit['changes'],dict) or set(edit['changes'])-{'title','metadata'}:
                raise ValueError('Drawing edits may change title and metadata only')
            draft.update(copy.deepcopy(edit['changes']))
        else:
            raise ValueError(f'Unknown operation: {action}')
    errors = core.validate(draft)
    if errors:
        raise ValueError('\n'.join(errors))
    from connection_policy import require_supported_connection
    old_lines = {line['id']: line for line in document['connections']}
    for line in draft['connections']:
        require_supported_connection(draft, line, old_lines.get(line['id']))
    draft_ids = {r['id'] for key in ('components','connections','notes') for r in draft.get(key,[])}
    for finding in proposal.get('review_findings', []):
        if set(finding['object_ids']) - draft_ids:
            raise ValueError('Review finding refers to an unknown draft object')
    draft['revision'] = document.get('revision',0)+1
    return draft

def diff(before, after):
    lines = []
    for key in ('components','connections'):
        old,new = ({r['id']:r for r in d[key]} for d in (before,after))
        for identifier in old.keys()-new.keys():
            lines.append('Remove '+old[identifier].get('tag',identifier))
        for identifier in new.keys()-old.keys():
            lines.append('Add '+new[identifier].get('tag',identifier))
        for identifier in old.keys() & new.keys():
            if old[identifier] != new[identifier]:
                changed = ', '.join(k for k in set(old[identifier])|set(new[identifier]) if old[identifier].get(k)!=new[identifier].get(k))
                lines.append(f"Update {new[identifier].get('tag',identifier)}: {changed}")
    if before.get('title') != after.get('title') or before.get('metadata') != after.get('metadata'):
        lines.append('Update drawing settings')
    return lines
