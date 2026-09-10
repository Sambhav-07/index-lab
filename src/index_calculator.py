"""Price Return and Total Return Index calculation engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import pandas as pd

from .validator import (
    validate_date_range,
    validate_dividend_data,
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
    return_type: str


class IndexCalculator:
    """Calculate a fixed-weight Price Return or Total Return Index.

    Selected constituent weights remain fixed over the requested period; there is
    no periodic rebalancing or constituent reconstitution in this demonstration.

    Price Return:
        R_i,t = P_i,t / P_i,t-1 - 1

    Total Return (synthetic dividends):
        R_i,t = (P_i,t + D_i,t) / P_i,t-1 - 1

    The Total Return calculation assumes dividends are reinvested on the dividend date.
    """

    def __init__(
        self,
        prices: pd.DataFrame,
        universe: pd.DataFrame,
        base_level: float = 100.0,
        dividends: pd.DataFrame | None = None,
    ) -> None:
        if base_level <= 0:
            raise ValueError("Base level must be positive.")
        self.prices = prices.copy()
        self.prices["date"] = pd.to_datetime(self.prices["date"])
        self.universe = universe.copy()
        self.base_level = float(base_level)
        if dividends is None:
            dividends = pd.DataFrame(columns=["date", "ticker", "dividend"])
        self.dividends = dividends.copy()
        if not self.dividends.empty:
            self.dividends["date"] = pd.to_datetime(self.dividends["date"])

    def _prepare_price_matrix(self, selected_tickers, start_date, end_date) -> pd.DataFrame:
        """Create a date-by-ticker price matrix and apply documented missing-price handling."""
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
            raise ValueError("No price observations exist in the selected date range.")
        if len(matrix) < 2:
            raise ValueError("At least two trading dates are required to calculate returns.")
        missing_cells = int(matrix.isna().sum().sum())
        if missing_cells > 0:
            matrix = matrix.ffill()
        if matrix.isna().any().any():
            remaining_missing = int(matrix.isna().sum().sum())
            raise ValueError(
                f"{remaining_missing} missing price observations occur before a valid price is available and cannot be substituted."
            )
        return matrix

    def _prepare_dividend_matrix(self, selected_tickers, price_index) -> pd.DataFrame:
        """Align sparse dividend observations to the trading-date price matrix."""
        if self.dividends.empty:
            return pd.DataFrame(0.0, index=price_index, columns=list(selected_tickers))
        validate_dividend_data(self.dividends, selected_tickers)
        data = self.dividends[
            self.dividends["ticker"].isin(selected_tickers)
            & self.dividends["date"].isin(price_index)
        ]
        matrix = (
            data.pivot(index="date", columns="ticker", values="dividend")
            .reindex(index=price_index, columns=list(selected_tickers))
            .fillna(0.0)
        )
        return matrix

    def calculate(
        self,
        selected_tickers: Sequence[str],
        start_date: str | pd.Timestamp,
        end_date: str | pd.Timestamp,
        methodology: str = "equal",
        custom_weight_values: Sequence[float] | dict[str, float] | None = None,
        return_type: str = "price",
    ) -> IndexResult:
        """Calculate the selected Price Return or Total Return Index."""
        tickers = validate_selected_tickers(selected_tickers, self.universe["ticker"].tolist())
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
            raise ValueError("Unknown methodology. Use: equal, market_cap, or custom.")

        return_type = return_type.lower().strip()
        if return_type not in {"price", "total"}:
            raise ValueError("Unknown return type. Use: price or total.")

        price_matrix = self._prepare_price_matrix(tickers, start, end)
        previous_prices = price_matrix.shift(1)
        if return_type == "price":
            stock_returns = price_matrix.pct_change().iloc[1:]
        else:
            dividend_matrix = self._prepare_dividend_matrix(tickers, price_matrix.index)
            stock_returns = ((price_matrix + dividend_matrix) / previous_prices - 1.0).iloc[1:]

        weighted_index_returns = stock_returns.mul(weights, axis=1).sum(axis=1)
        index_levels = self.base_level * (1.0 + weighted_index_returns).cumprod()
        levels = pd.DataFrame({
            "date": index_levels.index,
            "index_return": weighted_index_returns.values,
            "index_level": index_levels.values,
        })
        return IndexResult(
            index_levels=levels,
            stock_returns=stock_returns,
            weights=weights,
            start_date=pd.Timestamp(price_matrix.index.min()),
            end_date=pd.Timestamp(price_matrix.index.max()),
            base_level=self.base_level,
            methodology=methodology,
            return_type=return_type,
        )
