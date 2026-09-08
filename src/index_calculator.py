"""Price Return Index calculation engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import pandas as pd

from .validator import (
    validate_date_range,
    validate_price_data,
    validate_selected_tickers,
)
from .weighting import equal_weights, market_cap_weights, custom_weights


@dataclass
class IndexResult:
    """Container for a completed index calculation."""

    index_levels: pd.DataFrame
    stock_returns: pd.DataFrame
    weights: pd.Series
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    base_level: float
    methodology: str


class IndexCalculator:
    """Calculate a daily rebalanced Price Return Index.

    The selected constituent weights are fixed over the requested period.
    The index is calculated from weighted daily simple returns:

        index_return_t = sum(weight_i * stock_return_i,t)

        index_level_t = index_level_(t-1) * (1 + index_return_t)

    No dividends are included.
    """

    def __init__(
        self,
        prices: pd.DataFrame,
        universe: pd.DataFrame,
        base_level: float = 100.0,
    ) -> None:
        if base_level <= 0:
            raise ValueError("Base level must be positive.")

        self.prices = prices.copy()
        self.prices["date"] = pd.to_datetime(self.prices["date"])
        self.universe = universe.copy()
        self.base_level = float(base_level)

    def _prepare_price_matrix(
        self,
        selected_tickers: Sequence[str],
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
    ) -> pd.DataFrame:
        """Create a date-by-ticker price matrix for the requested period."""
        data = self.prices[
            (self.prices["ticker"].isin(selected_tickers))
            & (self.prices["date"] >= start_date)
            & (self.prices["date"] <= end_date)
        ].copy()

        matrix = (
            data.pivot(index="date", columns="ticker", values="close_price")
            .sort_index()
            .reindex(columns=list(selected_tickers))
        )

        if matrix.empty:
            raise ValueError(
                "No price observations exist in the selected date range."
            )

        if len(matrix) < 2:
            raise ValueError(
                "At least two trading dates are required to calculate returns."
            )

        # Record the number of missing observations before substitution.
        missing_cells = int(matrix.isna().sum().sum())

        # Forward-fill missing prices using the most recent valid price.
        # This results in a 0% return for a constituent on an isolated
        # missing-price date.
        if missing_cells > 0:
            matrix = matrix.ffill()

        # Leading missing observations cannot be forward-filled because
        # there is no previous valid price available.
        if matrix.isna().any().any():
            remaining_missing = int(matrix.isna().sum().sum())
            raise ValueError(
                f"{remaining_missing} missing price observations occur before a "
                "valid price is available and cannot be substituted."
            )

        return matrix

    def calculate(
        self,
        selected_tickers: Sequence[str],
        start_date: str | pd.Timestamp,
        end_date: str | pd.Timestamp,
        methodology: str = "equal",
        custom_weight_values: Sequence[float] | dict[str, float] | None = None,
    ) -> IndexResult:
        """Calculate the Price Return Index for selected constituents."""
        tickers = validate_selected_tickers(
            selected_tickers, self.universe["ticker"].tolist()
        )
        validate_price_data(self.prices, tickers)
        start, end = validate_date_range(start_date, end_date, self.prices)

        methodology = methodology.lower().strip()
        if methodology == "equal":
            weights = equal_weights(tickers)
        elif methodology in {"market_cap", "float_market_cap"}:
            weights = market_cap_weights(tickers, self.universe)
            methodology = "market_cap"
        elif methodology == "custom":
            if custom_weight_values is None:
                raise ValueError("Custom weights must be provided for custom methodology.")
            weights = custom_weights(tickers, custom_weight_values)
        else:
            raise ValueError(
                "Unknown methodology. Use: equal, market_cap, or custom."
            )

        price_matrix = self._prepare_price_matrix(tickers, start, end)
        stock_returns = price_matrix.pct_change().iloc[1:]

        weighted_index_returns = stock_returns.mul(weights, axis=1).sum(axis=1)
        index_levels = self.base_level * (1.0 + weighted_index_returns).cumprod()

        levels = pd.DataFrame(
            {
                "date": index_levels.index,
                "index_return": weighted_index_returns.values,
                "index_level": index_levels.values,
            }
        )

        return IndexResult(
            index_levels=levels,
            stock_returns=stock_returns,
            weights=weights,
            start_date=pd.Timestamp(price_matrix.index.min()),
            end_date=pd.Timestamp(price_matrix.index.max()),
            base_level=self.base_level,
            methodology=methodology,
        )
