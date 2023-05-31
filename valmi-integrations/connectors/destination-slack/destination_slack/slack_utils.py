from typing import Any, Dict


def map_data(mapping: list[Dict[str, str]], data: Dict[str, Any]):
    mapped_data = {}
    if "_valmi_meta" in data:
        mapped_data["_valmi_meta"] = data["_valmi_meta"]
    for item in mapping:
        k = item["stream"]
        v = item["sink"]
        if k in data:
            mapped_data[v] = data[k]
    return mapped_data
