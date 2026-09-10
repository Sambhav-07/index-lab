# Index Lab — Custom Equity Index Builder

Index Lab is a Streamlit-based analytical application for constructing and analysing a custom **30-stock synthetic equity index**. It demonstrates constituent selection, fixed weighting methodologies, daily return aggregation, index-level calculation, validation, missing-price handling, and both **Price Return** and **Total Return** index conventions.

> **Important:** All companies, prices, float market capitalisations, and dividend observations are fictional/synthetic and are used only for demonstration.

## Features

- Select constituents from a predefined 30-stock synthetic universe.
- Choose a historical date range.
- Choose one of three fixed weighting methodologies:
  - Equal Weight
  - Float Market Capitalisation Weight
  - Custom Weight
- Choose a return convention:
  - Price Return
  - Total Return
  - Compare Price vs Total Return
- View index level and cumulative return.
- Compare the effect of synthetic dividends on index performance.
- View constituent weights and sector allocation.
- Inspect synthetic price and dividend data.
- Validate ticker selections, dates, prices, dividends, and custom weights.
- Demonstrate isolated missing-price handling through forward-filling.
- Run automated unit tests with pytest.

## Architecture

```text
Streamlit UI (app.py)
        |
        v
Index Service
        |
        v
Index Calculator
   |            |
   v            v
Weighting    Validation
   |
   v
Price / Total Return Engine
        |
        v
Synthetic CSV Data
```

The application separates presentation, service orchestration, calculation logic, validation, weighting, metrics, and data loading so that the index engine can be tested independently of Streamlit.

## Project Structure

```text
index-lab/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── demo_dividends.csv
│   ├── processed/
│   │   ├── prices.csv
│   │   └── universe.csv
│   └── raw/
│       └── stock_parameters.csv
├── src/
│   ├── data_generator.py
│   ├── data_loader.py
│   ├── index_calculator.py
│   ├── index_service.py
│   ├── methodology.py
│   ├── metrics.py
│   ├── validator.py
│   └── weighting.py
└── tests/
    ├── test_index_calculator.py
    └── test_weighting.py
```

## Synthetic Data Model

Daily stock log returns are generated from correlated market, sector, and idiosyncratic factors:

```text
r_i,t = μ_i + β_i × r_market,t + λ × r_sector,t + ε_i,t
```

The idiosyncratic volatility is calibrated as:

```text
σ_idio = sqrt(σ_target² - (β × σ_market)² - (λ × σ_sector)²)
```

Prices are generated using exponential compounding:

```text
P_t = P_(t-1) × exp(r_t)
```

The data covers business days from **2021-01-01 to 2025-12-31** and uses random seed **42** for reproducibility.

## Weighting Methodologies

### Equal Weight

Each selected constituent receives:

```text
w_i = 1 / N
```

### Float Market Capitalisation Weight

```text
w_i = Float Market Cap_i / Σ Float Market Cap_j
```

The float market capitalisations are synthetic and static. The resulting constituent weights are fixed during the selected historical period.

### Custom Weight

The user assigns constituent weights manually. Weights must be non-negative and sum to 100%.

## Price Return Index

The Price Return convention captures price changes only and excludes dividends.

Daily constituent return:

```text
R_i,t(PR) = P_i,t / P_i,t-1 - 1
```

Daily index return:

```text
R_index,t = Σ(w_i × R_i,t)
```

Index level:

```text
Index Level_t = Index Level_(t-1) × (1 + R_index,t)
```

The base index level is **100**.

## Total Return Index

The application also provides a demonstration Total Return convention. It uses the separate `data/demo_dividends.csv` dataset, which contains **synthetic dividend observations**.

Daily constituent total return:

```text
R_i,t(TR) = (P_i,t + D_i,t) / P_i,t-1 - 1
```

where `D_i,t` is the synthetic dividend paid on date `t`. The implementation assumes the dividend is reinvested on the dividend date.

The index aggregates constituent total returns using the same fixed constituent weights:

```text
R_index,t(TR) = Σ(w_i × R_i,t(TR))
```

The resulting Total Return Index is compounded from the same base level of 100.

### Price Return vs Total Return

The Streamlit application provides a **Compare Price vs Total Return** option. It calculates both versions using identical constituents, dates, and weighting methodology, then displays their index levels and cumulative returns side-by-side.

This makes the effect of dividend income visible rather than merely describing the calculation in documentation.

## Cumulative Return

Cumulative return is a performance measure, not a separate return convention:

```text
Cumulative Return = Index Level_T / Index Level_0 - 1
```

For a Price Return Index, this is cumulative price performance. For a Total Return Index, it is cumulative performance including the modeled dividends.

## Missing Price Handling

Missing close prices are allowed through the initial validation layer so that the calculation engine can apply its explicit substitution policy.

- An isolated missing observation is **forward-filled using the most recent valid price**.
- This produces a 0% constituent return for that missing-price date.
- Leading missing observations cannot be forward-filled and therefore raise an error.
- Non-positive prices and duplicate ticker-date observations remain invalid.

The repository includes `demo_missing_data.py` to demonstrate this behaviour without modifying the production synthetic price dataset.

## Validation

The calculation engine validates:

- At least one constituent is selected.
- Selected tickers exist in the universe.
- Duplicate ticker selections are rejected.
- Start date is not after end date.
- Requested dates are within the available dataset.
- Required price columns exist.
- Non-positive prices are rejected.
- Duplicate ticker-date price observations are rejected.
- Dividend columns, duplicate observations, missing dividend values, and negative dividends are validated.
- Custom weights are non-negative and total 100%.

## Streamlit Application

The sidebar controls the complete index construction workflow:

1. Select constituents.
2. Select the historical period.
3. Select the weighting methodology.
4. Select Price Return, Total Return, or comparison mode.
5. Generate the index.

The Overview tab displays:

- Index level
- Cumulative return
- Performance chart
- Constituent weights
- Sector allocation
- Price Return vs Total Return comparison when selected

The Data tab displays the synthetic universe and dividend observations. The Methodology tab documents the formulas and assumptions used by the application.

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

Run the test suite:

```bash
pytest -q
```

Regenerate the synthetic price dataset if required:

```bash
python src/data_generator.py
```

## Design Scope and Assumptions

This project is a transparent demonstration of index-engineering concepts rather than a production benchmark methodology. It does **not** model real-world corporate actions, taxes, transaction costs, constituent reconstitution, periodic rebalancing, or real company dividends.

The Total Return feature is intentionally implemented with clearly labelled synthetic dividend data so the calculation and Streamlit demonstration can be evaluated without representing fictional observations as real market data.
