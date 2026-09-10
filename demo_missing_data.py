import pandas as pd

from src.index_calculator import IndexCalculator


# Small synthetic universe
universe = pd.DataFrame(
    {
        "ticker": ["A", "B"],
        "company_name": ["Alpha Corp", "Beta Corp"],
        "sector": ["Technology", "Finance"],
        "float_market_cap": [1000, 1000],
    }
)


# Price data with one intentionally missing value
prices = pd.DataFrame(
    {
        "date": pd.to_datetime(
            [
                "2025-01-01",
                "2025-01-02",
                "2025-01-03",
                "2025-01-01",
                "2025-01-02",
                "2025-01-03",
            ]
        ),
        "ticker": ["A", "A", "A", "B", "B", "B"],
        "close_price": [100, None, 110, 100, 100, 100],
    }
)


print("\nORIGINAL PRICE DATA:")
print(prices)

print("\nMissing value detected for Stock A on 2025-01-02.")
print("The IndexCalculator will forward-fill the previous valid price.\n")


calculator = IndexCalculator(
    prices=prices,
    universe=universe,
    base_level=100,
)


result = calculator.calculate(
    selected_tickers=["A", "B"],
    start_date="2025-01-01",
    end_date="2025-01-03",
    methodology="equal",
)


print("STOCK RETURNS:")
print(result.stock_returns)

print("\nINDEX LEVELS:")
print(result.index_levels)

print("\nEXPLANATION:")
print(
    "Stock A's missing price on 2025-01-02 was forward-filled "
    "using its previous price of 100."
)
print(
    "Therefore, Stock A's return on that date was 0%."
)
print(
    "The index calculation continued without corrupting the main dataset."
)