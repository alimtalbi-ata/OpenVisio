"""Orthogonal route, editing, SVG, safety and Visio fidelity contract.
Author: Abdelhalim Talbi. Synthetic test diagrams only.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from openvisio.routing import route_points, set_edge_routing, RoutingError, _blocked, _bounds
from openvisio.render import edge_at, draw_document
from openvisio.export import to_svg
from openvisio.model import save, load, validate
from openvisio.vsdx import export_vsdx
from openvisio.history import History


def topology():
    return {'nodes': [{'id':'src','x':0,'y':0,'label':'ESXi'},
                      {'id':'dst','x':400,'y':0,'label':'SAN'},
                      {'id':'block','x':200,'y':0,'label':'Pare-feu'}],
            'edges': [{'id':'fc','from':'src','to':'dst','routing':'orthogonal'}]}


class OrthogonalRoutingTests(unittest.TestCase):
    def test_obstacle_is_avoided_and_endpoints_on_borders(self):
        doc=topology()
        pts=route_points(doc['edges'][0],doc['nodes'])
        self.assertEqual(pts[0],(70,0))
        self.assertEqual(pts[-1],(330,0))
        self.assertGreaterEqual(len(pts),4)
        for p,q in zip(pts,pts[1:]):
            self.assertTrue(p[0]==q[0] or p[1]==q[1],(p,q))
            self.assertFalse(_blocked(p,q,[_bounds(doc['nodes'][2])]),(p,q))

    def test_unobstructed_horizontal_is_two_points(self):
        doc=topology();doc['nodes'].pop()
        self.assertEqual(route_points(doc['edges'][0],doc['nodes']),[(70,0),(330,0)])

    def test_vertical_obstacle_and_reverse_direction(self):
        nodes=[{'id':'src','x':0,'y':0},{'id':'dst','x':0,'y':300},{'id':'block','x':0,'y':150}]
        edge={'id':'e','from':'dst','to':'src','routing':'orthogonal'}
        pts=route_points(edge,nodes)
        self.assertEqual(pts[0],(0,270))
        self.assertEqual(pts[-1],(0,30))
        for a,b in zip(pts,pts[1:]):self.assertFalse(_blocked(a,b,[_bounds(nodes[2])]))

    def test_reroute_when_obstacle_moves(self):
        doc=topology()
        original=route_points(doc['edges'][0],doc['nodes'])
        doc['nodes'][2]['y']=500
        moved=route_points(doc['edges'][0],doc['nodes'])
        self.assertNotEqual(original,moved)
        self.assertEqual(moved,[(70,0),(330,0)])

    def test_canvas_and_hit_testing_use_same_path(self):
        class Canvas:
            def __init__(self):self.lines=[]
            def delete(self,*args):pass
            def create_line(self,*args,**kw):self.lines.append(args)
            def create_rectangle(self,*args,**kw):pass
            def create_text(self,*args,**kw):pass
        doc=topology();canvas=Canvas()
        draw_document(canvas,doc)
        path=route_points(doc['edges'][0],doc['nodes'])
        self.assertEqual(canvas.lines[0],tuple(v for p in path for v in p))
        self.assertIsNone(edge_at(doc['nodes'],doc['edges'],200,0,tolerance=3))
        mid=((path[1][0]+path[2][0])/2,(path[1][1]+path[2][1])/2)
        self.assertEqual(edge_at(doc['nodes'],doc['edges'],*mid,tolerance=3)['id'],'fc')

    def test_svg_polyline_matches_route(self):
        doc=topology();svg=ET.fromstring(to_svg(doc))
        ns='{http://www.w3.org/2000/svg}'
        poly=svg.find(ns+'polyline')
        self.assertIsNotNone(poly)
        expected=' '.join(f'{x},{y}' for x,y in route_points(doc['edges'][0],doc['nodes']))
        self.assertEqual(poly.attrib['points'],expected)

    def test_undo_redo_and_persistence(self):
        doc=topology();doc['edges'][0].pop('routing')
        before=copy.deepcopy(doc)
        after=set_edge_routing(doc,'fc','orthogonal')
        self.assertEqual(doc,before)
        h=History(doc);h.record(after)
        self.assertEqual(h.undo(),before)
        self.assertEqual(h.redo(),after)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'diagram.openvisio'
            save(p,after)
            self.assertEqual(load(p),after)

    def test_bad_routing_is_rejected_by_model(self):
        doc=topology();doc['edges'][0]['routing']='curve'
        with self.assertRaisesRegex(ValueError,'routage'):validate(doc)

    def test_transaction_rejects_missing_edge_without_mutation(self):
        doc=topology();before=copy.deepcopy(doc)
        with self.assertRaisesRegex(ValueError,'introuvable'):
            set_edge_routing(doc,'missing','orthogonal')
        self.assertEqual(doc,before)

    def test_distant_equipment_does_not_limit_orthogonal_routing(self):
        doc=topology()
        for i in range(81):
            doc['nodes'].append({'id':f'extra-{i}','x':1000+i*150,'y':900})
        points = route_points(doc['edges'][0],doc['nodes'])
        self.assertGreaterEqual(len(points), 4)
        self.assertTrue(all(not _blocked(a, b, [_bounds(n) for n in doc['nodes'][2:]])
                            for a, b in zip(points, points[1:])))

    def test_vsdx_export_preserves_orthogonal_bends(self):
        # V42.12: static VSDX geometry now represents the routed elbows.
        from zipfile import ZipFile
        doc=topology()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'diagram.vsdx'
            export_vsdx(p,doc)
            with ZipFile(p) as archive:
                page=ET.fromstring(archive.read('visio/pages/page1.xml'))
            ns='{http://schemas.microsoft.com/office/visio/2011/1/core}'
            shape=next(x for x in page.findall(f'.//{ns}Shape')
                       if x.get('NameU')=='OpenVisio connector')
            rows=shape.findall(f'./{ns}Section/{ns}Row')
            self.assertGreaterEqual(len(rows),4)
            self.assertEqual(rows[0].get('T'),'MoveTo')
            self.assertTrue(all(x.get('T')=='LineTo' for x in rows[1:]))

    def test_straight_route_preserves_existing_perimeter_behavior(self):
        doc=topology();doc['edges'][0]['routing']='straight'
        self.assertEqual(route_points(doc['edges'][0],doc['nodes']),[(70,0),(330,0)])

    def test_performance_on_large_straight_topology(self):
        # Regression: straight routing uses an already-built index, not O(nodes*edges).
        nodes={f'n{i}':{'id':f'n{i}','x':i*160,'y':0} for i in range(750)}
        for i in range(1499):
            edge={'id':f'e{i}','from':f'n{i%750}','to':f'n{(i+1)%750}'}
            self.assertEqual(len(route_points(edge,nodes)),2)


if __name__=='__main__':unittest.main()

class InvalidRouteGuiRegression(unittest.TestCase):
    def test_overlap_never_crashes_render_or_hit_test(self):
        doc={'nodes':[{'id':'a','x':0,'y':0},{'id':'b','x':400,'y':0},
                      {'id':'l','x':-150,'y':0},{'id':'r','x':150,'y':0},
                      {'id':'u','x':0,'y':-80},{'id':'d','x':0,'y':80}],
             'edges':[{'id':'e','from':'a','to':'b','routing':'orthogonal'}]}
        class Canvas:
            def __init__(self):self.labels=[];self.lines=[]
            def delete(self,*args):pass
            def create_line(self,*args,**kw):self.lines.append(args)
            def create_rectangle(self,*args,**kw):pass
            def create_text(self,*args,**kw):self.labels.append(kw.get('text'))
        canvas=Canvas()
        draw_document(canvas,doc)
        self.assertEqual(canvas.lines,[])
        self.assertTrue(any('Routage impossible' in str(label) for label in canvas.labels))
        self.assertIsNone(edge_at(doc['nodes'],doc['edges'],200,0))
