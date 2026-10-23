"""SAN link metadata and validation. Author: Abdelhalim Talbi."""
PROTOCOLS = ("FC", "iSCSI", "Ethernet", "NFS", "SMB", "NVMe/TCP", "NVMe/FC")
def normalize_link(protocol="FC", source_port="", target_port="", fabric="", speed_gbps=""):
    if protocol not in PROTOCOLS:
        raise ValueError("Protocole non pris en charge")
    fields = {"protocol": protocol}
    for key, value in (("source_port", source_port), ("target_port", target_port), ("fabric", fabric)):
        value = value.strip()
        if len(value) > 120:
            raise ValueError(f"{key} : 120 caractères maximum")
        fields[key] = value
    speed = speed_gbps.strip()
    if speed:
        try:
            number = float(speed)
        except ValueError as exc:
            raise ValueError("Débit numérique attendu en Gbit/s") from exc
        if not (0 < number <= 1600):
            raise ValueError("Débit hors plage : 0 à 1600 Gbit/s")
        speed = str(number)
    fields["speed_gbps"] = speed
    return fields
