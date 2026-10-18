"""Strict JSON model round-trip and SAN field auditing. Auteur: Abdelhalim Talbi."""
import json
EPHEMERAL = frozenset(('exportedAt','exported_at','savedAt','saved_at','generatedAt','generated_at'))
SAN_KEYS = frozenset(('wwpn','wwnn','fabric','fabricid','fabric_id','zone','zones','zoneset','zone_set','zoning','vsan','fcid','switchwwn','switch_wwn','initiator','target','lun','port','portid','port_id'))
def canonical(value):
    if isinstance(value,dict):
        return {key:canonical(item) for key,item in sorted(value.items()) if key not in EPHEMERAL}
    if isinstance(value,list):return [canonical(item) for item in value]
    return value
def san_fields(value, path='$'):
    found={}
    if isinstance(value,dict):
        for key,item in value.items():
            loc=path+'.'+key
            if key.lower().replace('-','_') in SAN_KEYS:found[loc]=canonical(item)
            found.update(san_fields(item,loc))
    elif isinstance(value,list):
        for index,item in enumerate(value):found.update(san_fields(item,f'{path}[{index}]'))
    return found
def compare(before,after):
    a,b=canonical(before),canonical(after)
    fields_before,fields_after=san_fields(a),san_fields(b)
    return {'equal':a==b,'san_equal':fields_before==fields_after,'san_fields_before':len(fields_before),'san_fields_after':len(fields_after),'san_changed_paths':sorted(path for path in set(fields_before)|set(fields_after) if fields_before.get(path,object()) != fields_after.get(path,object())) if fields_before!=fields_after else []}
