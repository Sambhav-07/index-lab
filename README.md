# Custom Equity Index Builder

Stage 1 creates a reproducible synthetic 30-stock universe and correlated daily price data.

All companies and data are fictional. `float_market_cap` is synthetic static data used solely for demonstrating market-cap weighting.

## Model

`log return = stock drift + beta × market factor + sector loading × sector factor + idiosyncratic shock`

The idiosyncratic volatility is calibrated as:

`idio_vol = sqrt(target_vol² - (beta × market_vol)² - (sector_loading × sector_vol)²)`

Random seed: 42.

## Run

```bash
pip install -r requirements.txt
python src/data_generator.py
```
