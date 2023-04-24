from typing import Any, Dict


def map_data(mapping: Dict[str, str], data: Dict[str, Any]):
    mapped_data = {}
    if "_valmi_meta" in data:
        mapped_data["_valmi_meta"] = data["_valmi_meta"]
    for k, v in mapping.items():
        if k in data:
            mapped_data[v] = data[k]
    return mapped_data
