"""External VSDX page geometry and connector regression tests. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx import import_vsdx

V='http://schemas.microsoft.com/office/visio/2011/1/core'
OR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
R='http://schemas.openxmlformats.org/package/2006/relationships'

class ExternalMultipageTests(unittest.TestCase):
    def _make(self, p, target='page2.xml'):
        pages=f'''<Pages xmlns="{V}" xmlns:r="{OR}">
          <Page ID="0" Name="Fabric A"><PageSheet><Cell N="PageHeight" V="8"/></PageSheet><Rel r:id="rId1"/></Page>
          <Page ID="1" Name="Fabric B"><PageSheet><Cell N="PageHeight" V="10"/></PageSheet><Rel r:id="rId2"/></Page>
        </Pages>'''
        rels=f'''<Relationships xmlns="{R}">
          <Relationship Id="rId1" Target="page1.xml" Type="page"/>
          <Relationship Id="rId2" Target="{target}" Type="page"/>
        </Relationships>'''
        page1=f'''<PageContents xmlns="{V}"><Shapes>
          <Shape ID="1" NameU="Storage Array"><Cell N="PinX" V="2"/><Cell N="PinY" V="3"/><Text>Baie A</Text></Shape>
        </Shapes></PageContents>'''
        page2=f'''<PageContents xmlns="{V}"><Shapes>
          <Shape ID="1" NameU="SAN Switch"><Cell N="PinX" V="3"/><Cell N="PinY" V="4"/><Text>Switch B</Text></Shape>
          <Shape ID="2" NameU="Server"><Cell N="PinX" V="4"/><Cell N="PinY" V="4"/><Text>Hôte B</Text></Shape>
          <Shape ID="3"><Cell N="OneD" V="1"/></Shape>
        </Shapes><Connects>
          <Connect FromSheet="3" FromCell="BeginX" ToSheet="1"/>
          <Connect FromSheet="3" FromCell="EndX" ToSheet="2"/>
        </Connects></PageContents>'''
        with ZipFile(p,'w',ZIP_DEFLATED) as z:
            z.writestr('visio/pages/pages.xml',pages)
            z.writestr('visio/pages/_rels/pages.xml.rels',rels)
            z.writestr('visio/pages/page1.xml',page1)
            z.writestr('visio/pages/page2.xml',page2)

    def test_import_two_pages_preserves_names_and_connections(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'two.vsdx';self._make(p)
            doc=import_vsdx(p)
            self.assertEqual(len(doc['nodes']),3)
            self.assertEqual(len(doc['edges']),1)
            self.assertEqual([l['name'] for l in doc['layers']],['Fabric A','Fabric B'])
            self.assertEqual(doc['nodes'][0]['shape'],'storage')
            self.assertEqual(doc['nodes'][0]['y'],480)
            self.assertEqual(doc['nodes'][1]['y'],768+96+576)
            self.assertEqual(doc['edges'][0]['from'],'visio-p2-s1')
            self.assertEqual(doc['edges'][0]['to'],'visio-p2-s2')
            self.assertEqual(doc['metadata']['page_count'],2)

    def test_external_relationship_target_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'unsafe.vsdx';self._make(p,target='../../evil.xml')
            with self.assertRaisesRegex(ValueError,'non sûre'):
                import_vsdx(p)

    def test_unrelated_external_page_does_not_import_silently(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'missing.vsdx';self._make(p,target='missing.xml')
            with self.assertRaisesRegex(ValueError,'Relation de page'):
                import_vsdx(p)

if __name__=='__main__':unittest.main()

class ExternalMetadataTests(unittest.TestCase):
    def test_import_declares_lossy_transformations(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'multi.vsdx'
            ExternalMultipageTests()._make(p)
            doc=import_vsdx(p)
            self.assertIn('masters',doc['metadata']['limitations'])
            self.assertEqual(doc['metadata']['import_mode'],'flattened-pages')

    def test_rejects_xml_dtd_in_page_list(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'doctype.vsdx'
            with ZipFile(p,'w',ZIP_DEFLATED) as z:
                z.writestr('visio/pages/pages.xml','<!DOCTYPE Pages [<!ENTITY a "unsafe">]><Pages/>')
            with self.assertRaisesRegex(ValueError,'entités externes'):
                import_vsdx(p)

class PageHeightValidationTests(unittest.TestCase):
    def test_nonfinite_page_height_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'nonfinite-height.vsdx'
            ExternalMultipageTests()._make(p)
            with ZipFile(p) as z:
                parts={n:z.read(n) for n in z.namelist()}
            parts['visio/pages/pages.xml']=parts['visio/pages/pages.xml'].replace(b'V="8"',b'V="NaN"')
            with ZipFile(p,'w',ZIP_DEFLATED) as z:
                for n,raw in parts.items():z.writestr(n,raw)
            doc=import_vsdx(p)
            self.assertEqual(len(doc['nodes']),3)
            self.assertTrue(all(isinstance(n['y'],float) for n in doc['nodes']))
