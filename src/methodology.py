"""Streamlit rendering functions for project methodology documentation."""
from __future__ import annotations
import streamlit as st


def render_methodology() -> None:
    st.header("Methodology")
    st.caption("All companies, prices, float market capitalizations, and dividend observations are synthetic.")
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
        st.latex(r"R_{i,t}^{PR}=\frac{P_{i,t}}{P_{i,t-1}}-1")
        st.markdown("Price Return uses only price changes. Example: ₹100 to ₹105 produces 5%.")
    with st.expander("Total Return Calculation"):
        st.latex(r"R_{i,t}^{TR}=\frac{P_{i,t}+D_{i,t}}{P_{i,t-1}}-1")
        st.markdown("Total Return adds the dividend paid on date t and assumes the dividend is reinvested on that date. Dividend observations are **synthetic demonstration data only** and are not real company distributions.")
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
        st.markdown("The same weighted-return aggregation is used for Price Return and Total Return constituent returns.")
    with st.expander("Index Level and Cumulative Return"):
        st.latex(r"Index\ Level_t=Index\ Level_{t-1}(1+R_{index,t})")
        st.latex(r"Cumulative\ Return=\frac{Index\ Level_T}{Index\ Level_0}-1")
        st.markdown("The base index level is **100**. Cumulative return measures compounded performance over the selected period; it is distinct from the Total Return methodology, which determines whether dividends are included.")
    st.subheader("Return Types and Fixed Weights")
    st.info("Price Return excludes dividends. Total Return includes the synthetic dividend observations and assumes reinvestment. Both versions use fixed constituent weights during the selected historical period; there is no periodic rebalancing or constituent reconstitution.")
    with st.expander("Model Assumptions"):
        st.markdown("""1. All companies are fictional.
2. All prices, float market capitalizations, and dividend observations are synthetic.
3. Prices are generated from correlated market, sector, and idiosyncratic factors.
4. Data covers 2021-01-01 to 2025-12-31 using business days.
5. Random seed = 42.
6. Missing prices are forward-filled when a previous valid price exists; leading missing prices raise an error.
7. The index uses fixed constituent weights.
8. Total Return assumes dividends are reinvested on the dividend date.
9. Corporate actions, taxes, transaction costs, periodic rebalancing, and reconstitution are not modeled.
10. Float market capitalization values are static.""")
    st.subheader("Methodology Flow")
    st.markdown("**Synthetic Stock Universe → Correlated Market + Sector + Idiosyncratic Factors → Daily Stock Prices → Daily Stock Returns → Price/Total Return Treatment → Weighting Methodology → Weighted Index Return → Daily Index Compounding → Index Performance**")
