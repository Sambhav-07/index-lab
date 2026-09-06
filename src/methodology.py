"""Streamlit rendering functions for project methodology documentation."""
from __future__ import annotations
import streamlit as st


def render_methodology() -> None:
    st.header("Methodology")
    st.caption("All companies, prices, and float market capitalizations are synthetic.")
    with st.expander("Synthetic Data Generation", expanded=True):
        st.markdown("Prices cover **2021-01-01 to 2025-12-31** on business days. A fixed random seed of **42** makes the generated dataset reproducible.")
        st.markdown("Daily stock log returns are generated with a correlated factor model:")
        st.latex(r"r_{i,t}=\mu_i+\beta_i r_{market,t}+\lambda r_{sector,t}+\epsilon_{i,t}")
        st.markdown("The market factor uses a 7% annual drift and 10% annual volatility, converted to daily values using approximately 252 trading days. Stocks in the same sector share a sector factor, while idiosyncratic shocks create company-specific variation.")
    with st.expander("Volatility Calibration"):
        st.latex(r"\sigma_{idio}=\sqrt{\sigma_{target}^2-(\beta\sigma_{market})^2-(\lambda\sigma_{sector})^2}")
        st.markdown("Idiosyncratic volatility is the residual after market and sector contributions, preventing volatility from being double-counted. A small numerical floor is used if residual variance is extremely close to zero.")
    with st.expander("Price Generation"):
        st.latex(r"P_t=P_{t-1}\times\exp(r_t)")
        st.markdown("Exponential compounding is consistent with log-return modeling and keeps prices positive. Each series is anchored to its synthetic starting price.")
    with st.expander("Stock Return Calculation"):
        st.latex(r"R_{i,t}=\frac{P_{i,t}}{P_{i,t-1}}-1")
        st.markdown("Example: a price moving from ₹100 to ₹105 produces a simple daily return of **105 / 100 − 1 = 5%**.")
    with st.expander("Equal Weighting"):
        st.latex(r"w_i=\frac{1}{N}")
        st.markdown("Every selected stock receives the same fixed weight. This is simple and reduces concentration, but does not reflect company size.")
    with st.expander("Float Market Capitalization Weighting"):
        st.latex(r"w_i=\frac{Float\ Market\ Cap_i}{\sum_j Float\ Market\ Cap_j}")
        st.markdown("Larger synthetic companies receive larger weights. Float market caps are synthetic, static, and used only to demonstrate this methodology; weights are fixed over the selected period.")
    with st.expander("Custom Weighting"):
        st.latex(r"\sum_i w_i=1")
        st.markdown("The user manually assigns constituent weights. The application validates totals of 100% (or 1.0 internally).")
    with st.expander("Index Return Calculation"):
        st.latex(r"R_{index,t}=\sum_i w_iR_{i,t}")
        st.markdown("Example: 60% in a stock returning 5% and 40% in a stock returning 2% gives an index return of **3.8%**.")
    with st.expander("Index Level Calculation"):
        st.latex(r"Index\ Level_t=Index\ Level_{t-1}(1+R_{index,t})")
        st.markdown("The base index level is **100**. If the daily index return is 3.8%, the next level is **100 × 1.038 = 103.8**.")
    st.subheader("Price Return Index and Fixed Weights")
    st.warning("THIS INDEX IS A PRICE RETURN INDEX.")
    st.markdown("The index reflects price changes only. Dividends, dividend reinvestment, corporate action adjustments, taxes, and transaction costs are excluded. Selected constituent weights remain fixed during the historical period; there is no periodic rebalancing or constituent reconstitution.")
    with st.expander("Model Assumptions"):
        st.markdown("""1. All companies are fictional.
2. All prices and float market capitalizations are synthetic.
3. Prices are generated from correlated market, sector, and idiosyncratic factors.
4. Data covers 2021-01-01 to 2025-12-31 using business days.
5. Random seed = 42.
6. Missing prices are not intentionally included.
7. The index is a fixed-weight Price Return Index.
8. Dividends, periodic rebalancing, reconstitution, and corporate actions are not modeled.
9. Float market capitalization values are static.""")
    st.subheader("Methodology Flow")
    st.markdown("**Synthetic Stock Universe → Correlated Market + Sector + Idiosyncratic Factors → Daily Stock Prices → Daily Stock Returns → Weighting Methodology → Weighted Index Return → Daily Index Compounding → Index Performance**")
