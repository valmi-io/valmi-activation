# Purpose: MetricDisplayOrder class to format metrics for display order

import copy
from typing import Dict, List

SOURCE_DISPLAY_ORDER = {
    "total": 0,
    "new": 4,
    "valid": 8,
    "invalid": 12,
    "success": 16,
    "succeeded": 20,
}

DESTINATION_DISPLAY_ORDER = {
    "succeeded": 0,
    "failed": 4
}


class MetricDisplayOrder:
    def __init__(self) -> None:
        pass

    def format_metric(self, dispaly_order: Dict[str, int], metric: Dict[str, int]) -> List[Dict[str, int]]:
        formatted_metrics = copy.deepcopy(metric)
        for k, v in metric.items():
            formatted_metrics[k] = {
                "value": v,
                "display_order": dispaly_order.get(k.split("$$")[0].lower(), 1000)
            }
        return formatted_metrics

    def format(self, metrics: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, Dict[str, int]]]:

        formatted_metrics = copy.deepcopy(metrics)
        formatted_metrics["src"] = self.format_metric(SOURCE_DISPLAY_ORDER, metrics.get("src", {}))
        formatted_metrics["dest"] = self.format_metric(DESTINATION_DISPLAY_ORDER, metrics.get("dest", {}))
        return formatted_metrics
