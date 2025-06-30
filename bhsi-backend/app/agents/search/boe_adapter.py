import json
from typing import Dict, Any
from app.crud.raw_docs import raw_docs  # This is your CRUD utility

def boe_to_rawdoc_dict(boe_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a BOE result dict to a dict suitable for RawDoc insertion.
    """
    payload_bytes = json.dumps(boe_result).encode("utf-8")
    meta = {
        "url": boe_result.get("url_html") or boe_result.get("url"),
        "pub_date": boe_result.get("fechaPublicacion"),
        "identificador": boe_result.get("identificador"),
        "seccion": boe_result.get("seccion_codigo"),
        "seccion_nombre": boe_result.get("seccion_nombre"),
    }
    return {
        "source": "BOE",
        "payload": payload_bytes,
        "meta": meta
    }
