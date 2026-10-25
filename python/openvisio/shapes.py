"""Infrastructure shape catalogue. Author: Abdelhalim Talbi."""
SHAPES = {
    "server": {"label": "Serveur", "group": "Compute", "fill": "#dbeafe"},
    "storage": {"label": "Baie de stockage", "group": "Storage", "fill": "#dcfce7"},
    "san-switch": {"label": "Switch SAN", "group": "SAN", "fill": "#fef3c7"},
    # Historical generic switch: identity is deliberately neither LAN nor SAN.
    "switch": {"label": "Commutateur (type non précisé)", "group": "Unclassified", "fill": "#e2e8f0"},
    "nas": {"label": "NAS", "group": "Storage", "fill": "#ccfbf1"},
    "network-switch": {"label": "Switch réseau", "group": "Network", "fill": "#ede9fe"},
    "firewall": {"label": "Pare-feu", "group": "Security", "fill": "#fee2e2"},
    "database": {"label": "Base de données", "group": "Application", "fill": "#e0e7ff"},
    "application": {"label": "Application", "group": "Application", "fill": "#fce7f3"},
}
def get_shape(name):
    return SHAPES.get(name, SHAPES["server"])
