"""Input and data validation for the index calculation engine."""

from __future__ import annotations

from datetime import date
from typing import Sequence
import pandas as pd


class ValidationError(ValueError):
    """Raised when index inputs or price data are invalid."""


def validate_selected_tickers(
    selected_tickers: Sequence[str], available_tickers: Sequence[str]
) -> list[str]:
    """Validate the selection and return tickers without duplicates."""
    tickers = list(selected_tickers)
    if not tickers:
        raise ValidationError("Select at least one stock.")
    if len(set(tickers)) != len(tickers):
        raise ValidationError("Duplicate tickers are not allowed.")
    available = set(available_tickers)
    unknown = sorted(set(tickers) - available)
    if unknown:
        raise ValidationError(f"Selected tickers not found in the universe: {unknown}")
    return tickers


def validate_date_range(
    start_date: str | pd.Timestamp | date,
    end_date: str | pd.Timestamp | date,
    prices: pd.DataFrame,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Validate the requested date range against available price data."""
    if "date" not in prices.columns:
        raise ValidationError("Price data must contain a date column.")
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    if start > end:
        raise ValidationError("Start date must be on or before end date.")
    min_date = pd.Timestamp(prices["date"].min())
    max_date = pd.Timestamp(prices["date"].max())
    if start < min_date or end > max_date:
        raise ValidationError(
            f"Date range must fall within available data: {min_date.date()} to {max_date.date()}."
        )
    return start, end


def validate_price_data(prices: pd.DataFrame, selected_tickers: Sequence[str]) -> None:
    """Validate required price columns and selected ticker observations.

    Missing close prices are permitted here so the calculation engine can apply
    its documented forward-fill policy. Non-positive non-missing prices remain invalid.
    """
    required = {"date", "ticker", "close_price"}
    missing = required - set(prices.columns)
    if missing:
        raise ValidationError(f"Price data is missing columns: {sorted(missing)}")
    selected = prices[prices["ticker"].isin(selected_tickers)].copy()
    if selected.empty:
        raise ValidationError("No price data exists for the selected tickers.")
    if (selected["close_price"].dropna() <= 0).any():
        raise ValidationError("Selected price data contains non-positive prices.")
    if selected.duplicated(["ticker", "date"]).any():
        raise ValidationError("Duplicate ticker-date price observations detected.")


def validate_dividend_data(dividends: pd.DataFrame, selected_tickers: Sequence[str]) -> None:
    """Validate synthetic dividend observations used by the Total Return Index."""
    required = {"date", "ticker", "dividend"}
    missing = required - set(dividends.columns)
    if missing:
        raise ValidationError(f"Dividend data is missing columns: {sorted(missing)}")
    selected = dividends[dividends["ticker"].isin(selected_tickers)].copy()
    if selected.duplicated(["ticker", "date"]).any():
        raise ValidationError("Duplicate ticker-date dividend observations detected.")
    if selected["dividend"].isna().any():
        raise ValidationError("Dividend observations cannot be missing.")
    if (selected["dividend"] < 0).any():
        raise ValidationError("Dividend values cannot be negative.")
