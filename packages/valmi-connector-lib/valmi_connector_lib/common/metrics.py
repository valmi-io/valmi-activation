def get_metric_type(sync_op: str):
    """
    Returns the metric type for the given sync operation.
    """
    if sync_op.endswith("e"):
        return f"{sync_op}d"
    elif (sync_op.endswith("ed")):
        return f"{sync_op}"
    else:
        return f"{sync_op}d"
