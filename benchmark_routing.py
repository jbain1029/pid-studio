"""Reproducible adjacent-pipe routing microbenchmark, not a UI benchmark."""
import json
import time
import pidcore
import routing


def run():
    boxes = [pidcore.routing_bounds({'type':'tank', 'rotation':0,
                                    'position':[x*180,y*140]})
             for y in range(10) for x in range(10)]
    links = [((x*180+40,y*140),((x+1)*180-40,y*140),(1,0),(-1,0))
             for y in range(10) for x in range(9)]
    routing._route.cache_clear()
    start = time.perf_counter()
    paths = [routing.route(*link,boxes) for link in links]
    cold = time.perf_counter()-start
    start = time.perf_counter()
    for _ in range(20):
        for link in links:
            routing.route(*link,boxes)
    warm = (time.perf_counter()-start)/20
    assert all(routing.clear(a,b,boxes) for path in paths for a,b in zip(path,path[1:]))
    return {'components':100,'pipes':90,'cold_seconds':cold,
            'cached_refresh_seconds':warm,'cache_hits':routing._route.cache_info().hits}


if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
