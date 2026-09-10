"""Service layer between Streamlit and the index calculation engine."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
import pandas as pd
from .data_loader import load_dividends, load_prices, load_universe
from .index_calculator import IndexCalculator, IndexResult
from .metrics import build_constituent_table, calculate_summary_metrics


@dataclass
class IndexBuildResponse:
    result: IndexResult
    metrics: dict
    constituent_table: pd.DataFrame


class IndexService:
    """Load synthetic data once and expose dashboard-ready index operations."""
    def __init__(self) -> None:
        self.universe = load_universe()
        self.prices = load_prices()
        self.dividends = load_dividends()
        self.calculator = IndexCalculator(self.prices, self.universe, dividends=self.dividends)

    def available_tickers(self) -> list[str]:
        return self.universe["ticker"].tolist()

    def available_date_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        return (pd.Timestamp(self.prices["date"].min()), pd.Timestamp(self.prices["date"].max()))

    def build_index(self, selected_tickers: Sequence[str], start_date, end_date,
                    methodology: str, custom_weight_values=None, return_type: str = "price") -> IndexBuildResponse:
        result = self.calculator.calculate(
            selected_tickers=selected_tickers, start_date=start_date, end_date=end_date,
            methodology=methodology, custom_weight_values=custom_weight_values, return_type=return_type,
        )
        return IndexBuildResponse(result=result, metrics=calculate_summary_metrics(result),
                                  constituent_table=build_constituent_table(result, self.universe))

    def build_comparison(self, selected_tickers: Sequence[str], start_date, end_date,
                         methodology: str, custom_weight_values=None) -> tuple[IndexBuildResponse, IndexBuildResponse]:
        price = self.build_index(selected_tickers, start_date, end_date, methodology, custom_weight_values, "price")
        total = self.build_index(selected_tickers, start_date, end_date, methodology, custom_weight_values, "total")
        return price, total
