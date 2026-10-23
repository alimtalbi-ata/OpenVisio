"""Equipment property validation, independent of the GUI. Author: Abdelhalim Talbi."""
import ipaddress

def normalize_properties(label, hostname="", address="", vendor="", model="", role="", location="", serial_number="", firmware="", notes=""):
    label = label.strip()
    if not label or len(label) > 120:
        raise ValueError("Nom obligatoire (120 caractères maximum)")
    values = {"label": label}
    for key, value in (("hostname", hostname), ("address", address), ("vendor", vendor), ("model", model), ("role", role), ("location", location), ("serial_number", serial_number), ("firmware", firmware), ("notes", notes)):
        value = value.strip()
        if len(value) > (2000 if key == "notes" else 120):
            raise ValueError(f"{key} : 120 caractères maximum")
        if key == "address" and value:
            try:
                ipaddress.ip_address(value)
            except ValueError as exc:
                raise ValueError("Adresse IP invalide (IPv4 ou IPv6)") from exc
        values[key] = value
    return values
