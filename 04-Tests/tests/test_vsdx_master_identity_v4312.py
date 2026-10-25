"""V43.12: external Visio master catalogue identity (synthetic OPC fixtures).

These tests do NOT exercise Microsoft Visio Desktop. Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_external import V, R, OR


def fixture(path, *, master_name="Brocade G720", master_name_u="Sheet.70",
            duplicate=False, visible_name="Sheet.1", include_links=False,
            caption="Fabric A"):
    def cell(name, value):
        return f'<Cell N="{name}" V="{value}"/>'

    shapes = [
        f'<Shape ID="1" NameU="Sheet.1" Name="{visible_name}" Master="70">'
        + ''.join(cell(k, v) for k, v in (("PinX", 2), ("PinY", 2),
                                          ("Width", 1.4), ("Height", 0.8)))
        + f'<Text>{caption}</Text></Shape>',
        '<Shape ID="2" NameU="Sheet.2" Master="71">'
        + ''.join(cell(k, v) for k, v in (("PinX", 6), ("PinY", 2),
                                          ("Width", 1.4), ("Height", 0.8)))
        + '<Text>Storage A</Text></Shape>',
    ]
    links = []
    if include_links:
        for ident, label in ((101, 'Fabric A FC0/1'), (102, 'Fabric B FC0/2')):
            shapes.append(f'<Shape ID="{ident}" NameU="Dynamic connector.{ident}">'
                          '<Cell N="OneD" V="1"/><Text>' + label + '</Text></Shape>')
            links.extend((f'<Connect FromSheet="{ident}" FromCell="BeginX" ToSheet="1" ToCell="PinX"/>',
                          f'<Connect FromSheet="{ident}" FromCell="EndX" ToSheet="2" ToCell="PinX"/>'))
    master = (f'<Master ID="70" NameU="{master_name_u}" Name="{master_name}"/>'
              '<Master ID="71" NameU="Sheet.71" Name="Storage Array"/>')
    if duplicate:
        master += '<Master ID="70" NameU="Network Switch" Name="Network Switch"/>'
    ns = f'xmlns="{V}"'
    page = f'<PageContents {ns}><Shapes>{"".join(shapes)}</Shapes><Connects>{"".join(links)}</Connects></PageContents>'
    pages = f'<Pages {ns}><Page ID="0" Name="SAN"><PageSheet><Cell N="PageHeight" V="8"/></PageSheet><Rel xmlns:r="{OR}" r:id="rId1"/></Page></Pages>'
    rels = f'<Relationships xmlns="{R}"><Relationship Id="rId1" Target="page1.xml" Type="page"/></Relationships>'
    masters = f'<Masters {ns}>{master}</Masters>'
    with ZipFile(path, 'w') as archive:
        for name, xml in (("visio/pages/pages.xml", pages),
                          ("visio/pages/_rels/pages.xml.rels", rels),
                          ("visio/pages/page1.xml", page),
                          ("visio/masters/masters.xml", masters)):
            archive.writestr(name, xml.encode('utf-8'))


class ExternalMasterIdentity(unittest.TestCase):
    def test_brocade_master_classifies_generic_sheet_without_using_caption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            fixture(path, caption='Ordinary caption')
            doc = import_vsdx(path)
            self.assertEqual(doc['nodes'][0]['shape'], 'san-switch')
            self.assertEqual(doc['nodes'][0]['label'], 'Ordinary caption')
            self.assertEqual(doc['nodes'][1]['shape'], 'storage')

    def test_cisco_mds_master_and_parallel_links_survive_public_reexport(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            fixture(path, master_name='Cisco MDS 9148', include_links=True)
            doc = import_vsdx(path)
            self.assertEqual(doc['nodes'][0]['shape'], 'san-switch')
            self.assertEqual(len(doc['edges']), 2)
            self.assertEqual([e['label'] for e in doc['edges']], ['Fabric A FC0/1', 'Fabric B FC0/2'])
            exported = Path(tmp) / 'reexport.vsdx'
            export_vsdx(exported, doc)
            self.assertEqual(import_vsdx(exported), doc)

    def test_explicit_openvisio_type_overrides_conflicting_master(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            fixture(path, visible_name='OpenVisio network-switch')
            doc = import_vsdx(path)
            self.assertEqual(doc['nodes'][0]['shape'], 'network-switch')

    def test_unknown_master_preserves_generic_server_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            fixture(path, master_name='Custom abstract template')
            self.assertEqual(import_vsdx(path)['nodes'][0]['shape'], 'server')

    def test_duplicate_master_ids_are_rejected_not_arbitrarily_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            fixture(path, duplicate=True)
            with self.assertRaisesRegex(ValueError, 'Master.*dupliqu'):
                import_vsdx(path)

    def test_master_catalog_does_not_infer_hardware_from_caption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            fixture(path, master_name='Abstract box', caption='Brocade G720')
            doc = import_vsdx(path)
            self.assertEqual(doc['nodes'][0]['shape'], 'server')
            self.assertEqual(doc['nodes'][0]['label'], 'Brocade G720')


if __name__ == '__main__':
    unittest.main()
