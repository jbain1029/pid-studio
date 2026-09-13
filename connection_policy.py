"""Creation policy, deliberately separate from legacy document validation."""
import pidcore as core


def attachment_reason(document, endpoint):
    component = next((item for item in document['components']
                      if item['id'] == endpoint.get('component')), None)
    if component is None:
        return None
    meaning = core.definition(component, document).get('port_meanings', {}).get(endpoint.get('port'))
    if meaning:
        return (f"{component['tag']}.{endpoint['port']}: {meaning} "
                'This illustrative attachment does not support new line connections. '
                'Use a drawing note to describe the physical relationship. Existing legacy links are retained for review.')
    return None


def require_supported_connection(document, candidate, original=None):
    """Allow legacy geometry/label edits, but never new physical-as-signal links."""
    endpoints = [candidate['from'], candidate['to']]
    if original is not None:
        previous = [original['from'], original['to']]
        if endpoints == previous or endpoints == previous[::-1]:
            return
    for endpoint in endpoints:
        reason = attachment_reason(document, endpoint)
        if reason:
            raise ValueError(reason)
