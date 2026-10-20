from openvisio.connector_geometry import connector_endpoints

def test_boundary():
    assert connector_endpoints({'x':0,'y':0},{'x':300,'y':0}) == ((70.0,0.0),(230.0,0.0))
