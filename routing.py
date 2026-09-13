"""Deterministic orthogonal routing on a compressed visibility grid."""
import heapq
import itertools
from bisect import bisect_right
from functools import lru_cache

class RouteError(ValueError):
    pass

def clear(a, b, boxes):
    if a[0] != b[0] and a[1] != b[1]:
        return False
    for left, top, right, bottom in boxes:
        if a[0] == b[0]:
            if left < a[0] < right and max(min(a[1], b[1]), top) < min(max(a[1], b[1]), bottom):
                return False
        elif top < a[1] < bottom and max(min(a[0], b[0]), left) < min(max(a[0], b[0]), right):
            return False
    return True

def simplify(points):
    result = []
    for p in points:
        if result and p == result[-1]:
            continue
        while len(result) >= 2:
            a, b = result[-2:]
            if (a[0] == b[0] == p[0] and (b[1]-a[1])*(p[1]-b[1]) >= 0) or (a[1] == b[1] == p[1] and (b[0]-a[0])*(p[0]-b[0]) >= 0):
                result.pop()
            else:
                break
        result.append(p)
    return result


def blocked_intervals(intervals):
    """Merge open obstacle spans; endpoints may touch but not enter them."""
    merged = []
    for low, high in sorted(intervals):
        if low >= high:
            continue
        if merged and low <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(high, merged[-1][1]))
        else:
            merged.append((low, high))
    return tuple(low for low, high in merged), tuple(high for low, high in merged)


def interval_clear(a, b, spans):
    if a == b:
        return True
    low, high = sorted((a, b))
    starts, ends = spans
    index = bisect_right(ends, low)
    return index == len(starts) or starts[index] >= high

def segment(start, finish, boxes):
    if start == finish:
        return [start]
    for p in (start, finish):
        if any(l < p[0] < r and t < p[1] < b for l,t,r,b in boxes):
            raise RouteError('A routing waypoint is inside a component')
    # A clear straight route or one-bend Manhattan route is already optimal.
    if clear(start, finish, boxes):
        return [start, finish]
    for corner in ((finish[0], start[1]), (start[0], finish[1])):
        if clear(start, corner, boxes) and clear(corner, finish, boxes):
            return simplify([start, corner, finish])
    xs = sorted({start[0], finish[0]} | {v for l,t,r,b in boxes for v in (l-10, r+10)})
    ys = sorted({start[1], finish[1]} | {v for l,t,r,b in boxes for v in (t-10, b+10)})
    # Each grid line sees only the obstacle interiors that cross that line.
    # Index them once, rather than scanning every box for every A* edge.
    vertical = [blocked_intervals((t,b) for l,t,r,b in boxes if l < x < r) for x in xs]
    horizontal = [blocked_intervals((l,r) for l,t,r,b in boxes if t < y < b) for y in ys]
    origin = (xs.index(start[0]), ys.index(start[1]), -1)
    target = (xs.index(finish[0]), ys.index(finish[1]))
    serial = itertools.count()
    queue = [(0, 0, next(serial), origin)]
    costs, parents = {origin: 0}, {}
    edge_clear = {}
    while queue:
        _, cost, _, state = heapq.heappop(queue)
        if cost != costs[state]:
            continue
        x, y, direction = state
        if (x, y) == target:
            result = []
            while state is not None:
                result.append((xs[state[0]], ys[state[1]]))
                state = parents.get(state)
            return simplify(result[::-1])
        for dx, dy, axis in ((1,0,0),(-1,0,0),(0,1,1),(0,-1,1)):
            nx, ny = x+dx, y+dy
            if not (0 <= nx < len(xs) and 0 <= ny < len(ys)):
                continue
            a, b = (xs[x],ys[y]), (xs[nx],ys[ny])
            edge = tuple(sorted((a,b)))
            if edge not in edge_clear:
                edge_clear[edge] = (interval_clear(a[0],b[0],horizontal[y]) if axis == 0
                                    else interval_clear(a[1],b[1],vertical[x]))
            if not edge_clear[edge]:
                continue
            score = cost + abs(a[0]-b[0]) + abs(a[1]-b[1]) + (20 if direction not in (-1, axis) else 0)
            successor = (nx,ny,axis)
            if score < costs.get(successor, float('inf')):
                costs[successor], parents[successor] = score, state
                heuristic = abs(b[0]-finish[0]) + abs(b[1]-finish[1])
                heapq.heappush(queue, (score+heuristic, score, next(serial), successor))
    raise RouteError('No clear orthogonal route; move components or routing waypoints')

def route(start, finish, start_direction, finish_direction, boxes, waypoints=()):
    # Geometry-only cache: selection, labels and export modes never change a route.
    # Returning a fresh list prevents callers from mutating cached geometry.
    return list(_route(tuple(start), tuple(finish), tuple(start_direction), tuple(finish_direction),
                       tuple(tuple(box) for box in boxes), tuple(tuple(p) for p in waypoints)))


@lru_cache(maxsize=512)
def _route(start, finish, start_direction, finish_direction, boxes, waypoints):
    a = (start[0]+start_direction[0]*20, start[1]+start_direction[1]*20)
    b = (finish[0]+finish_direction[0]*20, finish[1]+finish_direction[1]*20)
    if not clear(start, a, boxes) or not clear(b, finish, boxes):
        raise RouteError('A component blocks a connection port')
    anchors = [a] + [tuple(p) for p in waypoints] + [b]
    points = [start, a]
    for p, q in zip(anchors, anchors[1:]):
        points.extend(segment(p, q, boxes)[1:])
    points.append(finish)
    return tuple(simplify(points))
