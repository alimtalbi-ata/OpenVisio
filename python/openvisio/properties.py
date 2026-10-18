"""Equipment property validation, independent of the GUI. Author: Abdelhalim Talbi."""
import ipaddress

def normalize_properties(label, hostname="", address="", vendor="", model=""):
    label = label.strip()
    if not label or len(label) > 120:
        raise ValueError("Nom obligatoire (120 caractères maximum)")
    values = {"label": label}
    for key, value in (("hostname", hostname), ("address", address), ("vendor", vendor), ("model", model)):
        value = value.strip()
        if len(value) > 120:
            raise ValueError(f"{key} : 120 caractères maximum")
        if key == "address" and value:
            try:
                ipaddress.ip_address(value)
            except ValueError as exc:
                raise ValueError("Adresse IP invalide (IPv4 ou IPv6)") from exc
        values[key] = value
    return values
