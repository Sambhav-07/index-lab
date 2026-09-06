import pandas as pd
import pytest

from src.index_calculator import IndexCalculator


def test_index_calculation_with_equal_weights():
    universe = pd.DataFrame(
        {
            "ticker": ["A", "B"],
            "company_name": ["Alpha", "Beta"],
            "sector": ["Tech", "Finance"],
            "float_market_cap": [100, 100],
        }
    )

    prices = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2025-01-01", "2025-01-02", "2025-01-03",
                    "2025-01-01", "2025-01-02", "2025-01-03",
                ]
            ),
            "ticker": ["A", "A", "A", "B", "B", "B"],
            "close_price": [100, 110, 121, 100, 100, 100],
        }
    )

    calculator = IndexCalculator(prices, universe, base_level=100)

    result = calculator.calculate(
        selected_tickers=["A", "B"],
        start_date="2025-01-01",
        end_date="2025-01-03",
        methodology="equal",
    )

    # Day 1: A +10%, B 0% => Index +5% => 105
    # Day 2: A +10%, B 0% => Index +5% => 110.25
    assert result.index_levels.iloc[0]["index_level"] == pytest.approx(105.0)
    assert result.index_levels.iloc[1]["index_level"] == pytest.approx(110.25)
    assert result.weights.sum() == pytest.approx(1.0)


def test_market_cap_weights_change_index_return():
    universe = pd.DataFrame(
        {
            "ticker": ["A", "B"],
            "company_name": ["Alpha", "Beta"],
            "sector": ["Tech", "Finance"],
            "float_market_cap": [300, 100],
        }
    )

    prices = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-01", "2025-01-02"]
            ),
            "ticker": ["A", "A", "B", "B"],
            "close_price": [100, 110, 100, 100],
        }
    )

    result = IndexCalculator(prices, universe).calculate(
        ["A", "B"], "2025-01-01", "2025-01-02", methodology="market_cap"
    )

    # A weight 75%, B weight 25%; index return = 7.5%
    assert result.index_levels.iloc[0]["index_level"] == pytest.approx(107.5)
