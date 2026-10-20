"""Boundary geometry for OpenVisio."""

def connector_endpoints(source, target):
    return (source['x'], source['y']), (target['x'], target['y'])
