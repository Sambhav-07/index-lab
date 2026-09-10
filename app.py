"""Index Lab — Custom Equity Index Builder Streamlit application."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.index_service import IndexService
from src.methodology import render_methodology

st.set_page_config(
    page_title="Index Lab",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_service() -> IndexService:
    return IndexService()


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --lab-bg: #1d1e20;
            --lab-panel: #202123;
            --lab-panel-2: #252628;
            --lab-border: #45484d;
            --lab-text: #eceff1;
            --lab-muted: #9ba1a8;
            --lab-red: #d61f3a;
            --lab-green: #72bd28;
        }
        .stApp { background: var(--lab-bg); color: var(--lab-text); }
        header[data-testid="stHeader"] { background: rgba(29,30,32,0.96); }
        #MainMenu, footer { visibility: hidden; }
        .block-container { max-width: 1560px; padding-top: 0.7rem; padding-bottom: 2rem; }

        /* Sidebar */
        section[data-testid="stSidebar"] { background: #17181a; border-right: 1px solid #303236; }
        section[data-testid="stSidebar"] > div { padding-top: 1rem; }
        section[data-testid="stSidebar"] h2 { letter-spacing: .08em; font-size: .85rem; }

        /* Typography */
        h1, h2, h3, p, label, .stMarkdown { color: var(--lab-text); }
        .indexlab-brand {
            font-size: 2.75rem; font-weight: 800; letter-spacing: -0.06em;
            color: var(--lab-red); line-height: 1; margin: 0.5rem 0 0.2rem 0;
        }
        .indexlab-subtitle { color: var(--lab-muted); font-size: .92rem; letter-spacing: .05em; }
        .indexlab-rule { border-bottom: 1px solid #35373b; margin: 0.8rem 0 1.15rem 0; }
        .eyebrow { color: var(--lab-muted); text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; font-weight: 700; }

        /* Top navigation */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2.6rem; border-bottom: 1px solid #37393d; padding-left: .1rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 54px; background: transparent; color: #8f959c;
            border: none; font-weight: 700; letter-spacing: .04em; font-size: 1rem;
            padding: 0 .15rem;
        }
        .stTabs [aria-selected="true"] { color: var(--lab-red) !important; }
        .stTabs [data-baseweb="tab-highlight"] { background-color: var(--lab-red) !important; height: 3px; }

        /* Metrics */
        [data-testid="stMetric"] {
            background: #191a1c; border-bottom: 1px solid #323438;
            padding: 1.15rem .3rem 1rem .3rem;
        }
        [data-testid="stMetricLabel"] { color: var(--lab-muted); text-transform: uppercase; letter-spacing: .08em; }
        [data-testid="stMetricValue"] { color: var(--lab-text); font-size: 1.7rem; }

        /* Inputs */
        [data-baseweb="select"] > div,
        [data-testid="stDateInput"] input,
        [data-testid="stTextInput"] input {
            background: #1f2022 !important; border-color: #5b5e63 !important;
            color: var(--lab-text) !important;
        }
        .stButton button {
            background: var(--lab-red); color: white; border: none;
            font-weight: 700; letter-spacing: .05em;
        }
        .stButton button:hover { background: #b81830; color: white; }

        /* Dataframes */
        [data-testid="stDataFrame"] { border: 1px solid #36383c; }

        /* Expanders */
        [data-testid="stExpander"] { background: #1f2022; border: 1px solid #3b3e43; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_performance_chart(levels: pd.DataFrame, comparison: pd.DataFrame | None = None) -> go.Figure:
    fig = go.Figure()
    if comparison is None:
        fig.add_trace(
            go.Scatter(
                x=levels["date"], y=levels["index_level"], mode="lines",
                line={"color": "#e6e8eb", "width": 2.5},
                fill="tozeroy", fillcolor="rgba(230,232,235,0.08)",
                hovertemplate="<b>%{x|%A, %b %d, %Y}</b><br>Index Lab: %{y:,.2f}<extra></extra>",
                name="Index Lab",
            )
        )
    if comparison is not None:
        fig.add_trace(go.Scatter(
            x=comparison["date"], y=comparison["price_level"], mode="lines",
            line={"color": "#e6e8eb", "width": 2}, name="Price Return",
            hovertemplate="<b>%{x|%A, %b %d, %Y}</b><br>Price Return: %{y:,.2f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=comparison["date"], y=comparison["total_level"], mode="lines",
            line={"color": "#d61f3a", "width": 2.5}, name="Total Return",
            hovertemplate="<b>%{x|%A, %b %d, %Y}</b><br>Total Return: %{y:,.2f}<extra></extra>",
        ))
    fig.update_layout(
        height=500,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        paper_bgcolor="#202123",
        plot_bgcolor="#202123",
        font={"color": "#d8dbe0"},
        hovermode="x",
        showlegend=comparison is not None,
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis={"showgrid": False, "zeroline": False, "linecolor": "#55585d", "tickfont": {"color": "#9ca1a8"}},
        yaxis={"gridcolor": "#34363a", "zeroline": False, "linecolor": "#55585d", "tickfont": {"color": "#9ca1a8"}, "tickformat": ",.0f"},
    )
    return fig


inject_css()
service = get_service()
universe = service.universe
min_date, max_date = service.available_date_range()

if "build" not in st.session_state:
    st.session_state.build = None

label_map = {
    row.ticker: f"{row.ticker} — {row.company_name} ({row.sector})"
    for row in universe.itertuples()
}
default_tickers = [
    ticker
    for ticker in ["NVT", "ADS", "PNC", "MDS", "RTA", "GEC", "GFD", "PEO", "UTL"]
    if ticker in label_map
]

# Brand header
st.markdown('<div class="indexlab-brand">Index Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="indexlab-subtitle">CUSTOM EQUITY INDEX BUILDER &nbsp; • &nbsp; SYNTHETIC MARKET DATA</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="indexlab-rule"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="eyebrow">Index Configuration</div>', unsafe_allow_html=True)
    st.markdown("### Build Your Index")

    selected = st.multiselect(
        "Constituent Selection",
        service.available_tickers(),
        default=default_tickers,
        format_func=lambda ticker: label_map[ticker],
    )

    st.markdown("#### Historical Period")
    start_date = st.date_input(
        "Start Date",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
    end_date = st.date_input(
        "End Date",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    method_label = st.selectbox(
        "Weighting Methodology",
        ["Equal Weight", "Float Market Cap Weight", "Custom Weight"],
    )
    method = {
        "Equal Weight": "equal",
        "Float Market Cap Weight": "market_cap",
        "Custom Weight": "custom",
    }[method_label]

    return_label = st.selectbox(
        "Return Type",
        ["Price Return", "Total Return", "Compare Price vs Total Return"],
        help="Price Return excludes dividends. Total Return includes synthetic dividends assumed to be reinvested.",
    )
    return_type = {"Price Return": "price", "Total Return": "total"}.get(return_label)

    custom_values = None
    if method == "custom" and selected:
        default_weight = 100.0 / len(selected)
        editor_df = universe.set_index("ticker").loc[selected, ["company_name"]].reset_index()
        editor_df["Weight (%)"] = default_weight
        edited = st.data_editor(
            editor_df,
            disabled=["ticker", "company_name"],
            hide_index=True,
            key="weight_editor",
            use_container_width=True,
        )
        total = float(edited["Weight (%)"].fillna(0).sum())
        st.caption(f"Current Total Weight: {total:.2f}%")
        if not 99.99 <= total <= 100.01:
            st.error("Custom weights must total 100% before generation.")
        custom_values = edited.set_index("ticker")["Weight (%)"].to_dict()

    st.markdown("---")
    generate = st.button("GENERATE INDEX", type="primary", use_container_width=True)

if generate:
    try:
        if not selected:
            raise ValueError("Select at least one stock.")
        if pd.Timestamp(start_date) > pd.Timestamp(end_date):
            raise ValueError("Start date must be on or before end date.")
        if method == "custom" and custom_values is not None:
            if not 99.99 <= sum(custom_values.values()) <= 100.01:
                raise ValueError("Custom weights must total 100%.")

        if return_label == "Compare Price vs Total Return":
            price_build, total_build = service.build_comparison(
                selected, start_date, end_date, method, custom_values
            )
            st.session_state.build = {"mode": "comparison", "price": price_build, "total": total_build}
        else:
            st.session_state.build = service.build_index(
                selected, start_date, end_date, method, custom_values, return_type
            )
    except Exception as exc:
        st.error(f"Unable to generate index: {exc}")

(tab_overview, tab_data, tab_methodology, tab_products, tab_research) = st.tabs(
    [
        "Overview",
        "Data",
        "Methodology",
        "Index-Linked Products",
        "News & Research",
    ]
)

with tab_overview:
    build = st.session_state.build
    if build is None:
        st.markdown("### Build a custom equity index")
        st.info(
            "Select constituents, define the historical period, choose a weighting methodology and return type, "
            "then click **GENERATE INDEX**."
        )
    elif isinstance(build, dict):
        price_build = build["price"]
        total_build = build["total"]
        price_metrics = price_build.metrics
        total_metrics = total_build.metrics
        price_levels = price_build.result.index_levels.copy()
        total_levels = total_build.result.index_levels.copy()
        comparison = price_levels[["date", "index_level"]].rename(columns={"index_level": "price_level"}).merge(
            total_levels[["date", "index_level"]].rename(columns={"index_level": "total_level"}), on="date", how="inner"
        )
        latest_date = pd.Timestamp(total_metrics["end_date"]).strftime("%b %d, %Y")
        st.markdown('<div class="eyebrow">Price Return vs Total Return</div>', unsafe_allow_html=True)
        st.markdown("### Index Lab Performance Comparison")
        left, right = st.columns([1, 4], gap="large")
        with left:
            st.caption(f"As of {latest_date}")
            st.metric("Price Return", f"{price_metrics['end_index_level']:,.2f}")
            st.metric("Total Return", f"{total_metrics['end_index_level']:,.2f}")
            st.metric("TR Dividend Impact", f"{total_metrics['cumulative_return'] - price_metrics['cumulative_return']:.2%}")
            st.caption(f"{total_metrics['number_of_constituents']} CONSTITUENTS")
            st.caption({"equal": "EQUAL WEIGHT", "market_cap": "FLOAT MARKET CAP", "custom": "CUSTOM"}[total_metrics["methodology"]])
        with right:
            st.markdown('<div class="eyebrow">Graph View</div>', unsafe_allow_html=True)
            st.plotly_chart(build_performance_chart(total_levels, comparison), use_container_width=True)
        st.markdown("### Return Comparison")
        compare_df = pd.DataFrame({
            "Metric": ["Start Level", "End Level", "Cumulative Return"],
            "Price Return": [price_metrics["start_index_level"], price_metrics["end_index_level"], price_metrics["cumulative_return"]],
            "Total Return": [total_metrics["start_index_level"], total_metrics["end_index_level"], total_metrics["cumulative_return"]],
        })
        compare_display = compare_df.copy()
        compare_display.loc[0:1, ["Price Return", "Total Return"]] = compare_display.loc[0:1, ["Price Return", "Total Return"]].map(lambda x: f"{x:,.2f}")
        compare_display.loc[2, ["Price Return", "Total Return"]] = compare_display.loc[2, ["Price Return", "Total Return"]].map(lambda x: f"{x:.2%}")
        st.dataframe(compare_display, hide_index=True, use_container_width=True)
        st.info("Total Return uses synthetic dividend observations and assumes dividends are reinvested. The dividend data is for demonstration only.")
        table = total_build.constituent_table.copy()
        display_table = table.copy()
        display_table["weight_percent"] = display_table["weight_percent"].map(lambda value: f"{value:.2f}%")
        st.markdown("### Constituent Weights")
        st.dataframe(display_table, hide_index=True, use_container_width=True)
    else:
        metrics = build.metrics
        levels = build.result.index_levels.copy()
        levels["date"] = pd.to_datetime(levels["date"])
        latest = float(metrics["end_index_level"])
        cumulative = float(metrics["cumulative_return"])
        latest_date = pd.Timestamp(metrics["end_date"]).strftime("%b %d, %Y")
        return_title = "Total Return Index" if metrics["return_type"] == "total" else "Price Return Index"
        st.markdown(f'<div class="eyebrow">{return_title}</div>', unsafe_allow_html=True)
        st.markdown("### Index Lab Performance")
        left, right = st.columns([1, 4], gap="large")
        with left:
            st.caption(f"As of {latest_date}")
            st.metric("Index Level", f"{latest:,.2f}")
            st.metric("Cumulative Return", f"{cumulative:.2%}")
            st.caption(f"{metrics['number_of_constituents']} CONSTITUENTS")
            st.caption({"equal": "EQUAL WEIGHT", "market_cap": "FLOAT MARKET CAP", "custom": "CUSTOM"}[metrics["methodology"]])
            if metrics["return_type"] == "total":
                st.caption("SYNTHETIC DIVIDENDS · REINVESTED")
        with right:
            st.markdown('<div class="eyebrow">Graph View</div>', unsafe_allow_html=True)
            st.plotly_chart(build_performance_chart(levels), use_container_width=True)
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Start Level", f"{metrics['start_index_level']:,.2f}")
        c2.metric("End Level", f"{metrics['end_index_level']:,.2f}")
        c3.metric("Constituents", int(metrics["number_of_constituents"]))
        c4.metric("Return Type", "Total Return" if metrics["return_type"] == "total" else "Price Return")
        if metrics["return_type"] == "total":
            st.info("Synthetic dividend data is included and assumed reinvested. It is not real-world company dividend data.")
        st.markdown("### Constituent Weights")
        table = build.constituent_table.copy()
        display_table = table.copy()
        display_table["weight_percent"] = display_table["weight_percent"].map(lambda value: f"{value:.2f}%")
        st.dataframe(display_table, hide_index=True, use_container_width=True)
        sector = table.groupby("sector", as_index=False)["weight"].sum()
        sector["weight_percent"] = sector["weight"] * 100
        chart_col, composition_col = st.columns([1.15, 1], gap="large")
        with chart_col:
            st.markdown("### Sector Allocation")
            pie = px.pie(sector, names="sector", values="weight", hole=0.58)
            pie.update_traces(textposition="inside", textinfo="percent+label")
            pie.update_layout(paper_bgcolor="#1d1e20", plot_bgcolor="#1d1e20", font={"color": "#d8dbe0"}, margin={"l": 0, "r": 0, "t": 10, "b": 10}, showlegend=False)
            st.plotly_chart(pie, use_container_width=True)
        with composition_col:
            st.markdown("### Index Composition")
            largest = table.iloc[0]
            sector_top = sector.loc[sector["weight"].idxmax()]
            st.metric("Selected Float Market Cap", f"{table['float_market_cap'].sum():,.0f}")
            st.metric("Largest Constituent", f"{largest['ticker']} · {largest['weight_percent']:.2f}%")
            st.metric("Largest Sector", f"{sector_top['sector']} · {sector_top['weight_percent']:.1f}%")
            st.metric("Number of Sectors", int(table["sector"].nunique()))

with tab_data:
    st.markdown('<div class="eyebrow">Synthetic Data Universe</div>', unsafe_allow_html=True)
    st.markdown("### Index Constituents")
    st.caption("All companies, prices and float market capitalizations in this application are synthetic.")
    st.dataframe(universe, hide_index=True, use_container_width=True)
    st.markdown("### Synthetic Dividend Observations")
    st.caption("Used only for the Total Return demonstration; these are fictional dividend amounts.")
    st.dataframe(service.dividends.head(100), hide_index=True, use_container_width=True)

with tab_methodology:
    render_methodology()

with tab_products:
    st.markdown('<div class="eyebrow">Index-Linked Products</div>', unsafe_allow_html=True)
    st.markdown("### Future Product Layer")
    st.info(
        "This section is intentionally reserved for future extensions such as model portfolios, "
        "ETFs, structured products or benchmark-linked analytics."
    )

with tab_research:
    st.markdown('<div class="eyebrow">News & Research</div>', unsafe_allow_html=True)
    st.markdown("### Research Notes")
    st.write(
        "Index Lab currently focuses on transparent index construction. "
        "Methodology assumptions and calculation details are documented in the Methodology tab."
    )
