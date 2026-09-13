"""Synthetic dense-crossing routing microbenchmark; no Qt or UI latency claim.

Run with the project Python. Obstacles are staggered tank bodies; horizontal and
vertical routes span the entire field instead of linking adjacent equipment.
Crossing pipes are allowed by the router, so crossings are not route failures.
"""
import json
import time

import pidcore
import routing


def fixture(size=8):
    """Return deterministic staggered equipment and 2*size opposing routes."""
    if not 2 <= size <= 12:
        raise ValueError('Fixture size must be between 2 and 12')
    boxes = [pidcore.routing_bounds({
        'type': 'tank', 'rotation': 90 if (x+y) % 2 else 0,
        'position': [x*100 + (y % 3)*7, y*100 + (x % 3)*9],
    }) for y in range(size) for x in range(size)]
    far = (size-1)*100+120
    links = [((-120, y*100), (far, (size-1-y)*100), (1, 0), (-1, 0))
             for y in range(size)]
    links += [((x*100, -120), ((size-1-x)*100, far), (0, 1), (0, -1))
              for x in range(size)]
    return boxes, links


def solve(boxes, links):
    paths, failures = [], []
    for index, link in enumerate(links):
        try:
            paths.append(routing.route(*link, boxes))
        except routing.RouteError as error:
            paths.append(None)
            failures.append({'route': index, 'message': str(error)})
    return paths, failures


def check_paths(boxes, links, paths):
    """Return invalid successful route indexes; use no wall-time test threshold."""
    return [index for index, (link, path) in enumerate(zip(links, paths))
            if path is not None and (path[0] != link[0] or path[-1] != link[1]
            or not all(routing.clear(a, b, boxes) for a, b in zip(path, path[1:])))]


def run(size=8, refreshes=10):
    if refreshes < 1:
        raise ValueError('At least one cached refresh is required')
    boxes, links = fixture(size)
    routing._route.cache_clear()
    started = time.perf_counter()
    paths, failures = solve(boxes, links)
    cold = time.perf_counter()-started
    started = time.perf_counter()
    for _ in range(refreshes):
        solve(boxes, links)
    cached = (time.perf_counter()-started)/refreshes
    cache = routing._route.cache_info()
    # Any equipment motion changes the all-obstacles cache key. Measure this
    # explicitly, rather than suggesting cached refresh timing predicts dragging.
    moved = list(boxes)
    index = (size//2)*size+size//2
    left, top, right, bottom = moved[index]
    moved[index] = (left+5, top+5, right+5, bottom+5)
    started = time.perf_counter()
    moved_paths, moved_failures = solve(moved, links)
    changed = time.perf_counter()-started
    return {
        'fixture': 'staggered-tanks-opposing-crossings-v1',
        'components': len(boxes), 'pipes': len(links),
        'cold_seconds': cold, 'cached_refresh_seconds': cached,
        'one_obstacle_moved_seconds': changed,
        'cache_hits_before_move': cache.hits,
        'route_failures': failures, 'moved_route_failures': moved_failures,
        'invalid_routes': check_paths(boxes, links, paths),
        'invalid_moved_routes': check_paths(moved, links, moved_paths),
        'note': 'Geometry-only microbenchmark; pipe crossings/overlap are permitted. Not UI latency.',
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
