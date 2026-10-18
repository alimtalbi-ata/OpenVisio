import unittest
from openvisio.render import draw_document

class Canvas:
    def __init__(self): self.calls=[]
    def delete(self,*args): pass
    def create_line(self,*args,**kwargs): self.calls.append(("line",kwargs))
    def create_text(self,*args,**kwargs): self.calls.append(("text",kwargs))
    def create_rectangle(self,*args,**kwargs): self.calls.append(("rectangle",kwargs))

class EdgeLabelTests(unittest.TestCase):
    def test_protocol_is_rendered(self):
        canvas=Canvas()
        doc={"nodes":[{"id":"a","x":0,"y":0},{"id":"b","x":200,"y":0}],"edges":[{"id":"ab","from":"a","to":"b","protocol":"FC","speed_gbps":"32","fabric":"A","source_port":"1/1","target_port":"2/1"}]}
        draw_document(canvas,doc)
        labels=[call[1].get("text") for call in canvas.calls if call[0]=="text"]
        self.assertTrue(any("FC" in str(label) and "32 Gbit/s" in str(label) and "Fabric A" in str(label) and "1/1" in str(label) for label in labels))
    def test_missing_protocol_is_ok(self):
        canvas=Canvas()
        doc={"nodes":[{"id":"a","x":0,"y":0},{"id":"b","x":200,"y":0}],"edges":[{"id":"ab","from":"a","to":"b"}]}
        draw_document(canvas,doc)
        labels=[call[1].get("text") for call in canvas.calls if call[0]=="text"]
        self.assertNotIn(None,labels)
