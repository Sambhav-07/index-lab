# Index Lab

## Custom Equity Index Builder

Index Lab is a web-based analytical application that allows users to construct and analyse a custom dummy equity index. Users can select stocks from a predefined universe, choose a weighting methodology, select a date range, and generate a Price Return Index.

The application demonstrates index calculation, data validation, weighting methodologies, modular software architecture, and analytical visualization.

---

## Features

The application allows users to:

- View a predefined universe of 30 dummy stocks.
- Select one or more stocks for index construction.
- Select a date range from the available price data.
- Choose from multiple weighting methodologies:
  - Equal Weighting
  - Float Market Capitalisation Weighting
  - Custom Weighting
- Generate a Price Return Index.
- View index performance over time.
- View index level and cumulative return.
- Analyse sector allocation and index composition.
- Validate user inputs and weighting constraints.
- View methodology and calculation assumptions.

---

# Project Architecture

The project follows a modular architecture that separates the user interface, analytical services, calculation logic, validation, and data.

```text
Streamlit User Interface
        │
        ▼
    Index Service
        │
        ▼
  Index Calculator
        │
 ┌──────┴──────┐
 ▼             ▼
Weighting    Validation
        │
        ▼
   Data Layer
        │
        ▼
Synthetic CSV Data
```

## Project Structure

```text
index-lab/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│
├── src/
│   ├── data_generator.py
│   ├── data_loader.py
│   ├── weighting.py
│   ├── validator.py
│   ├── index_calculator.py
│   ├── index_service.py
│   ├── metrics.py
│   └── methodology.py
│
└── tests/
```

---

# Data

The application uses synthetic but realistic equity data.

## Stock Universe

The universe contains 30 dummy stocks with:

- Ticker
- Company Name
- Sector
- Float Market Capitalisation

Float market capitalisation is used for market-cap weighted index construction.

## Price Data

Daily close prices are generated for each stock over a consistent historical period.

The price dataset contains:

- Date
- Ticker
- Close Price

The synthetic data is generated using a fixed random seed to ensure reproducibility.

---

# Weighting Methodologies

## 1. Equal Weighting

Each selected stock receives the same weight:

```text
Weight = 1 / Number of Selected Stocks
```

For example, if five stocks are selected:

```text
Each stock weight = 20%
```

---

## 2. Float Market Capitalisation Weighting

Weights are proportional to each company's float market capitalisation:

```text
Weight_i = Float Market Cap_i / Total Float Market Cap
```

Larger companies therefore receive a higher weight in the index.

---

## 3. Custom Weighting

Users can assign their own weights to selected stocks.

The application validates that:

- No weight is negative.
- All selected stocks have valid weights.
- Total weights equal 100%.

---

# Price Return Index Methodology

Index Lab calculates a Price Return Index.

The index does not include:

- Dividends
- Dividend reinvestment
- Taxes
- Transaction costs

The index reflects changes in stock prices only.

---

# Stock Returns

Daily stock returns are calculated as:

```text
r_i(t) = P_i(t) / P_i(t-1) - 1
```

Where:

- `P_i(t)` = current stock price
- `P_i(t-1)` = previous day's stock price

---

# Index Return

The index daily return is calculated using constituent weights:

```text
r_index(t) = Σ (w_i × r_i(t))
```

Where:

- `w_i` = constituent weight
- `r_i(t)` = constituent return

---

# Index Level Calculation

The index begins with a base value of 100.

The index level evolves according to:

```text
Level(t) = Level(t-1) × (1 + r_index(t))
```

This creates the Price Return Index series over time.

---

# Validation

The application performs validation before calculating the index.

Validation checks include:

- At least one stock must be selected.
- Selected tickers must exist in the universe.
- Duplicate ticker selections are prevented.
- The selected date range must be valid.
- Start date cannot be after the end date.
- Required data columns must exist.
- Prices must be positive.
- Duplicate price observations are checked.
- Market capitalisation values must be valid.
- Custom weights cannot be negative.
- Custom weights must sum to 100%.

---

# Missing Data Handling

The application validates the availability of price data for selected constituents.

If missing or invalid data is detected, the application provides validation warnings or errors rather than silently producing an unreliable index calculation.

This approach was chosen to ensure that index calculations are transparent and reproducible.

---

# User Interface

The application is built using Streamlit.

Streamlit was selected because it allows Python analytical applications to be exposed through a web browser while maintaining direct integration with the backend calculation engine.

The interface provides:

- Index configuration controls
- Stock selection
- Date selection
- Weighting methodology selection
- Performance visualization
- Index metrics
- Sector allocation analysis
- Methodology documentation

---

# How to Run Locally

## 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

Move into the project folder:

```bash
cd index-lab
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate the Virtual Environment

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Run Tests

```bash
pytest
```

---

## 6. Run the Application

```bash
streamlit run app.py
```

The application will open in a browser.

---

# Testing

The project includes unit tests covering key analytical components.

Tests include:

- Equal weighting
- Market-cap weighting
- Custom weighting
- Weight validation
- Index calculations

Run tests using:

```bash
pytest
```

---

# Limitations

This project is designed as a simplified analytical index construction exercise.

Current limitations include:

- Synthetic rather than live market data.
- No dividend adjustments.
- No corporate action processing.
- No index rebalancing methodology.
- No transaction costs.
- No liquidity constraints.
- No constituent eligibility rules beyond basic validation.
- No production database.
- No automated data ingestion pipeline.

---

# Future Improvements

Potential future improvements include:

- Integration with real market data APIs.
- Scheduled index rebalancing.
- Corporate action adjustments.
- Dividend-adjusted Total Return Index calculations.
- Index divisor methodology.
- Liquidity and investability screens.
- Historical rebalancing analysis.
- Performance benchmarking against market indices.
- Risk metrics such as volatility and drawdown.
- Database-backed data storage.
- User authentication and saved index configurations.

---

# Technologies Used

- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Pytest

---

# Design Philosophy

The project was designed with separation of concerns in mind.

- The Streamlit application handles presentation and user interaction.
- The Index Service coordinates the analytical workflow.
- The Index Calculator calculates returns and index levels.
- Weighting modules calculate constituent weights.
- Validation modules check user inputs and data quality.
- The data layer manages the stock universe and price data.

This structure makes the application easier to test, maintain, and extend.

---

# Disclaimer

All stocks, companies, prices, and market capitalisation values used in this project are synthetic and are intended solely for analytical and educational purposes.
