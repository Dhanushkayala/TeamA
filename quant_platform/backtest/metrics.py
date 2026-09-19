"""Performance metrics tabulation and formatting."""

import pandas as pd
from typing import Dict, Any


def calculate_performance_summary(metrics_dict: Dict[str, Any]) -> pd.DataFrame:
    """
    Format metrics dictionary into a clean comparison DataFrame for UI display.
    """
    strat = metrics_dict.get("Strategy", {})
    bench = metrics_dict.get("Benchmark", {})

    all_keys = list(strat.keys())
    data = {
        "Metric": all_keys,
        "Strategy": [strat.get(k, "-") for k in all_keys],
        "Benchmark (Buy & Hold)": [bench.get(k, "-") for k in all_keys],
    }

    df = pd.DataFrame(data)
    return df
