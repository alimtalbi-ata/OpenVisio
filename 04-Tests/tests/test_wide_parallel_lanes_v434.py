"""Wide SAN fabrics must retain equipment-attached connector endpoints."""
import unittest
from openvisio.render import edge_routes, clip_route_to_nodes, NODE_HALF_HEIGHT

class WideParallelLanesTests(unittest.TestCase):
    def test_wide_lanes_terminate_on_equipment_border(self):
        nodes = [{'id':'a','x':0,'y':0}, {'id':'b','x':300,'y':0}]
        edges = [{'id':f'fc-{i}','from':'a','to':'b'} for i in range(11)]
        routes = edge_routes(nodes, edges)
        for edge in edges:
            start, end = clip_route_to_nodes(routes[edge['id']], *nodes)
            for (x,y), cx in [(start,0),(end,300)]:
                self.assertLessEqual(abs(x-cx),70)
                self.assertLessEqual(abs(y),NODE_HALF_HEIGHT)
                self.assertTrue(abs(x-cx)==70 or abs(y)==NODE_HALF_HEIGHT)
