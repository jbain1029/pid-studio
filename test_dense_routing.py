import random
import unittest

import benchmark_dense_routing as benchmark
import routing


class DenseRoutingTests(unittest.TestCase):
    def test_indexed_spans_match_box_scan_on_boundaries_and_overlaps(self):
        boxes = [(-20, -20, 10, 10), (10, -20, 30, 10),
                 (-10, -5, 20, 20), (40, 0, 40, 20), (0, 40, 20, 40)]
        coordinates = [-30, -20, -10, -5, 0, 5, 10, 20, 30, 40, 50]
        for axis in (0, 1):
            for fixed in coordinates:
                spans = routing.blocked_intervals(
                    ((l, r) if axis == 0 else (t, b)) for l, t, r, b in boxes
                    if (t < fixed < b if axis == 0 else l < fixed < r))
                for first in coordinates:
                    for last in coordinates:
                        a = (first, fixed) if axis == 0 else (fixed, first)
                        b = (last, fixed) if axis == 0 else (fixed, last)
                        with self.subTest(axis=axis, a=a, b=b):
                            self.assertEqual(routing.interval_clear(first, last, spans),
                                             routing.clear(a, b, boxes))

    def test_dense_crossing_routes_clear_and_cache_stable(self):
        boxes, links = benchmark.fixture(4)
        routing._route.cache_clear()
        paths, failures = benchmark.solve(boxes, links)
        self.assertEqual(failures, [])
        self.assertEqual(benchmark.check_paths(boxes, links, paths), [])
        self.assertEqual(benchmark.solve(boxes, links)[0], paths)
        self.assertEqual(routing._route.cache_info().hits, len(links))
        # The fixture really exercises obstacle detours, not just direct routes.
        self.assertTrue(any(len(path) > 4 for path in paths))

    def test_obstacle_motion_preserves_clear_routes(self):
        boxes, links = benchmark.fixture(4)
        l, t, r, b = boxes[10]
        boxes[10] = (l+5, t+5, r+5, b+5)
        paths, failures = benchmark.solve(boxes, links)
        self.assertEqual(failures, [])
        self.assertEqual(benchmark.check_paths(boxes, links, paths), [])

    def test_seeded_overlapping_boxes_have_clear_deterministic_detours(self):
        rng = random.Random(7401)
        for case in range(100):
            boxes = []
            for _ in range(12):
                x, y = rng.randrange(-80, 81, 10), rng.randrange(-80, 81, 10)
                w, h = rng.choice([10, 20, 30]), rng.choice([10, 20, 30])
                boxes.append((x, y, x+w, y+h))
            start = (-120, rng.randrange(-100, 101, 10))
            finish = (140, rng.randrange(-100, 101, 10))
            with self.subTest(case=case):
                path = routing.segment(start, finish, boxes)
                self.assertEqual(path[0], start)
                self.assertEqual(path[-1], finish)
                self.assertTrue(all(routing.clear(a, b, boxes)
                                    for a, b in zip(path, path[1:])))
                self.assertEqual(path, routing.segment(start, finish, boxes))


if __name__ == '__main__':
    unittest.main()
