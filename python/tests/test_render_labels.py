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
        doc={"nodes":[{"id":"a","x":0,"y":0},{"id":"b","x":200,"y":0}],"edges":[{"id":"ab","from":"a","to":"b","protocol":"FC 32G"}]}
        draw_document(canvas,doc)
        labels=[call[1].get("text") for call in canvas.calls if call[0]=="text"]
        self.assertIn("FC 32G",labels)
    def test_missing_protocol_is_ok(self):
        canvas=Canvas()
        doc={"nodes":[{"id":"a","x":0,"y":0},{"id":"b","x":200,"y":0}],"edges":[{"id":"ab","from":"a","to":"b"}]}
        draw_document(canvas,doc)
        labels=[call[1].get("text") for call in canvas.calls if call[0]=="text"]
        self.assertNotIn(None,labels)
