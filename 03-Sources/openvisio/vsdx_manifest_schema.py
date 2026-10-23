"""Strict OpenVisio VSDX manifest schema verification. Author: Abdelhalim Talbi."""
def validate_manifest_schema(manifest):
    """Reject JSON booleans, floats and strings even if Python considers True == 1."""
    if not isinstance(manifest, dict):
        raise ValueError("Manifeste OpenVisio/VSDX invalide : objet JSON attendu")
    schema = manifest.get("schema")
    if type(schema) is not int or schema not in (1, 2):
        raise ValueError("Intégrité OpenVisio/VSDX invalide")
    return schema
