"""Dashboard-ready metrics and constituent views."""
from __future__ import annotations
import pandas as pd
from .index_calculator import IndexResult


def calculate_summary_metrics(result: IndexResult) -> dict:
    """Return headline metrics for a completed index calculation."""
    levels = result.index_levels
    end_level = float(levels["index_level"].iloc[-1])
    return {
        "methodology": result.methodology,
        "return_type": result.return_type,
        "number_of_constituents": int(len(result.weights)),
        "start_date": result.start_date,
        "end_date": result.end_date,
        "start_index_level": float(result.base_level),
        "end_index_level": end_level,
        "cumulative_return": end_level / result.base_level - 1.0,
    }


def build_constituent_table(result: IndexResult, universe: pd.DataFrame) -> pd.DataFrame:
    """Join constituent metadata with calculated fixed weights."""
    required = {"ticker", "company_name", "sector", "float_market_cap"}
    missing = required - set(universe.columns)
    if missing:
        raise ValueError(f"Universe missing columns: {sorted(missing)}")
    weights = result.weights.rename("weight").reset_index().rename(columns={"index": "ticker"})
    table = universe[list(required)].merge(weights, on="ticker", how="inner")
    table["weight_percent"] = table["weight"] * 100.0
    return table.sort_values("weight", ascending=False).reset_index(drop=True)
