from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PARAM=ROOT/'data/raw/stock_parameters.csv'; UNIV=ROOT/'data/processed/universe.csv'; OUT=ROOT/'data/processed/prices.csv'
START='2021-01-01'; END='2025-12-31'; TD=252; SEED=42
MARKET_DRIFT=0.07; MARKET_VOL=0.10; SECTOR_VOL=0.05; GAMMA=0.50

def load_inputs():
    u=pd.read_csv(UNIV); p=pd.read_csv(PARAM)
    if len(u)!=30 or u.ticker.nunique()!=30: raise ValueError('Universe must contain exactly 30 unique tickers.')
    if set(u.ticker)!=set(p.ticker): raise ValueError('Universe and parameters do not match.')
    return u,p

def idio_vol(target,beta):
    residual=target**2-(beta*MARKET_VOL)**2-(GAMMA*SECTOR_VOL)**2
    return np.sqrt(max(residual,1e-8))

def generate():
    u,p=load_inputs(); dates=pd.date_range(START,END,freq='B'); rng=np.random.default_rng(SEED)
    n=len(dates); merged=u.merge(p,on='ticker',validate='one_to_one')
    market=rng.normal(MARKET_DRIFT/TD,MARKET_VOL/np.sqrt(TD),n)
    sector={s:rng.normal(0,SECTOR_VOL/np.sqrt(TD),n) for s in merged.sector.unique()}
    frames=[]
    for r in merged.itertuples(index=False):
        shock=rng.normal(0,idio_vol(r.annual_volatility,r.beta)/np.sqrt(TD),n)
        logret=r.annual_drift/TD+r.beta*market+GAMMA*sector[r.sector]+shock
        price=np.empty(n); price[0]=r.starting_price; price[1:]=price[0]*np.exp(np.cumsum(logret[1:]))
        frames.append(pd.DataFrame({'date':dates,'ticker':r.ticker,'close_price':np.round(price,2)}))
    prices=pd.concat(frames).sort_values(['ticker','date']).reset_index(drop=True)
    validate(prices,p,dates); prices.assign(date=prices.date.dt.strftime('%Y-%m-%d')).to_csv(OUT,index=False)
    return prices,dates

def validate(prices,p,dates):
    if len(prices)!=len(p)*len(dates): raise ValueError('Unexpected record count.')
    if prices.duplicated(['ticker','date']).any(): raise ValueError('Duplicate ticker-date combinations.')
    if prices.isna().any().any(): raise ValueError('Missing values detected.')
    if (prices.close_price<=0).any(): raise ValueError('Non-positive prices detected.')
    first=prices.groupby('ticker').first().close_price
    starts=p.set_index('ticker').starting_price
    if not np.allclose(first.loc[starts.index],starts,atol=.01): raise ValueError('Starting prices do not match parameters.')

def main():
    prices,dates=generate()
    print('Synthetic price generation completed successfully.')
    print(f'Tickers: {prices.ticker.nunique()}')
    print(f'Trading days: {len(dates)}')
    print(f'Records: {len(prices)}')
    print(f'Start date: {prices.date.min().date()}')
    print(f'End date: {prices.date.max().date()}')
    print(f'Minimum price: {prices.close_price.min():.2f}')
    print(f'Maximum price: {prices.close_price.max():.2f}')
if __name__=='__main__': main()
