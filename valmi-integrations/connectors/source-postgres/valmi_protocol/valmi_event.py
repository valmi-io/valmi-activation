def add_event_meta(data, key, val):
    if "_valmi_meta" not in data:
        data["_valmi_meta"] = {}
    data["_valmi_meta"][key] = val


def add_sync_op(data, sync_mode, sync_op):
    add_event_meta(data, "_sync_op", sync_op)
