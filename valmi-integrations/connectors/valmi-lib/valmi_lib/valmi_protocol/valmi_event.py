def add_event_meta(data, key, val):
    if "_valmi_meta" not in data:
        data["_valmi_meta"] = {}
    data["_valmi_meta"][key] = val
