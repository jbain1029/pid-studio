import unittest
import routing

class RoutingTests(unittest.TestCase):
    def assert_clear(self, points, boxes):
        for a,b in zip(points, points[1:]):
            self.assertTrue(routing.clear(a,b,boxes), (a,b))

    def test_avoids_equipment_and_preserves_ports(self):
        boxes = [(-29,-29,29,29),(131,-29,189,29),(291,-29,349,29)]
        points = routing.route((40,0),(280,0),(1,0),(-1,0),boxes)
        self.assertEqual(points[0],(40,0))
        self.assertEqual(points[-1],(280,0))
        self.assertTrue(any(abs(y)>29 for x,y in points))
        self.assert_clear(points,boxes)

    def test_vertical_ports_and_waypoint(self):
        boxes = [(-29,-29,29,29),(171,171,229,229)]
        points = routing.route((0,30),(200,170),(0,1),(0,-1),boxes,[(80,100)])
        self.assert_clear(points,boxes)
        self.assertEqual(points[1][0],0)
        self.assertEqual(points[-2][0],200)
        self.assertTrue(any(min(a[0],b[0])<=80<=max(a[0],b[0]) and min(a[1],b[1])<=100<=max(a[1],b[1]) for a,b in zip(points,points[1:])))

    def test_blocked_waypoint_fails_explicitly(self):
        with self.assertRaises(routing.RouteError):
            routing.route((0,0),(200,0),(1,0),(-1,0),[(80,-20,120,20)],[(100,0)])

if __name__ == '__main__':
    unittest.main()
