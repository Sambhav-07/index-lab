"""Weight calculation strategies for the Custom Equity Index Builder."""

from __future__ import annotations

from typing import Sequence
import numpy as np
import pandas as pd


class WeightingError(ValueError):
    """Raised when index weights are invalid."""


def equal_weights(tickers: Sequence[str]) -> pd.Series:
    """Return equal weights for the selected tickers."""
    tickers = list(tickers)
    if not tickers:
        raise WeightingError("At least one ticker must be selected.")

    return pd.Series(
        1.0 / len(tickers), index=tickers, name="weight", dtype=float
    )


def market_cap_weights(
    selected_tickers: Sequence[str], universe: pd.DataFrame
) -> pd.Series:
    """Return normalized float market-cap weights."""
    tickers = list(selected_tickers)
    if not tickers:
        raise WeightingError("At least one ticker must be selected.")

    required_columns = {"ticker", "float_market_cap"}
    missing = required_columns - set(universe.columns)
    if missing:
        raise WeightingError(
            f"Universe data is missing required columns: {sorted(missing)}"
        )

    selected = universe[universe["ticker"].isin(tickers)].copy()
    if selected["ticker"].nunique() != len(set(tickers)):
        missing_tickers = sorted(set(tickers) - set(selected["ticker"]))
        raise WeightingError(f"Unknown tickers: {missing_tickers}")

    if selected["float_market_cap"].isna().any():
        raise WeightingError("Float market capitalization cannot contain missing values.")
    if (selected["float_market_cap"] <= 0).any():
        raise WeightingError("Float market capitalization must be positive.")

    weights = selected.set_index("ticker")["float_market_cap"].astype(float)
    weights = weights / weights.sum()

    # Preserve the user's selected ticker order.
    return weights.reindex(tickers).rename("weight")


def custom_weights(
    selected_tickers: Sequence[str],
    weights: Sequence[float] | dict[str, float],
    tolerance: float = 1e-8,
) -> pd.Series:
    """Validate and return user-specified weights.

    Weights may be supplied as decimals summing to 1.0 or percentages summing
    to 100.0. Percentage inputs are automatically converted to decimals.
    """
    tickers = list(selected_tickers)
    if not tickers:
        raise WeightingError("At least one ticker must be selected.")

    if isinstance(weights, dict):
        missing = set(tickers) - set(weights)
        extra = set(weights) - set(tickers)
        if missing or extra:
            raise WeightingError(
                f"Custom weight tickers must match selection. "
                f"Missing: {sorted(missing)}; Extra: {sorted(extra)}"
            )
        series = pd.Series({ticker: weights[ticker] for ticker in tickers}, dtype=float)
    else:
        values = list(weights)
        if len(values) != len(tickers):
            raise WeightingError(
                "The number of custom weights must match the number of selected tickers."
            )
        series = pd.Series(values, index=tickers, dtype=float)

    if series.isna().any():
        raise WeightingError("Custom weights cannot contain missing values.")
    if (series < 0).any():
        raise WeightingError("Custom weights cannot be negative.")

    total = float(series.sum())
    if np.isclose(total, 100.0, atol=tolerance):
        series = series / 100.0
    elif not np.isclose(total, 1.0, atol=tolerance):
        raise WeightingError(
            f"Custom weights must sum to 1.0 or 100.0. Current total: {total:.6f}"
        )

    return series.rename("weight")
