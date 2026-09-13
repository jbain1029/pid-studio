import unittest
import pidcore
import routing


class RouteGeometryTests(unittest.TestCase):
    def test_every_catalog_port_can_exit_its_rotated_body(self):
        for kind, definition in pidcore.CATALOG.items():
            for rotation in (0,90,180,270):
                record = {'type':kind, 'rotation':rotation, 'position':[120,80]}
                bounds = pidcore.routing_bounds(record)
                for name, point in definition['ports'].items():
                    x,y = point
                    for _ in range(rotation//90):
                        x,y = -y,x
                    direction = ((1 if x>0 else -1),0) if abs(x)>abs(y) else (0,(1 if y>0 else -1))
                    start = (x+120,y+80)
                    end = (start[0]+direction[0]*20,start[1]+direction[1]*20)
                    self.assertTrue(routing.clear(start,end,[bounds]), (kind,rotation,name))

    def test_tank_top_and_actuator_are_obstacles(self):
        for kind, height in [('tank',-34),('control_valve',-34),('relief_valve',-38)]:
            bounds = pidcore.routing_bounds({'type':kind,'rotation':0,'position':[0,0]})
            points = routing.segment((-100,height),(100,height),[bounds])
            self.assertGreater(len(points),2)
            for a,b in zip(points,points[1:]):
                self.assertTrue(routing.clear(a,b,[bounds]))

    def test_rotation_and_live_position(self):
        record = {'type':'tank','rotation':90,'position':[0,0]}
        self.assertEqual(pidcore.routing_bounds(record,(100,200)),(69,171,137,229))

    def test_cache_is_geometry_based_and_defensive(self):
        routing._route.cache_clear()
        args = ((0,0),(200,0),(1,0),(-1,0),[])
        first = routing.route(*args)
        first.append((999,999))
        second = routing.route(*args)
        self.assertNotIn((999,999),second)
        self.assertEqual(routing._route.cache_info().hits,1)
        changed = routing.route(*args[:-1],[(80,-20,120,20)])
        self.assertNotEqual(second,changed)
        self.assertEqual(routing._route.cache_info().misses,2)
