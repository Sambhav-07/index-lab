from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def _check(df,cols,name):
    missing=set(cols)-set(df.columns)
    if missing: raise ValueError(f'{name} missing columns: {sorted(missing)}')
def load_universe():
    path=ROOT/'data/processed/universe.csv'
    if not path.exists(): raise FileNotFoundError(path)
    df=pd.read_csv(path); _check(df,['ticker','company_name','sector','float_market_cap'],'universe.csv'); return df
def load_prices():
    path=ROOT/'data/processed/prices.csv'
    if not path.exists(): raise FileNotFoundError('Run src/data_generator.py first.')
    df=pd.read_csv(path,parse_dates=['date']); _check(df,['date','ticker','close_price'],'prices.csv'); return df
