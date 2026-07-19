"""Streamlit dashboard for Ethiopia financial inclusion forecasts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import load_impact_sheet, load_unified_data
from src.forecast import build_forecast_bundle
from src.impact_model import (
    build_association_matrix,
    cumulative_event_effects,
    join_events_impacts,
)


st.set_page_config(page_title="Ethiopia FI Forecast", layout="wide")


@st.cache_data
def load_all():
    data = load_unified_data()
    impacts = load_impact_sheet()
    obs = data[data["record_type"] == "observation"].copy()
    obs["observation_date"] = pd.to_datetime(obs["observation_date"])
    events = data[data["record_type"] == "event"].copy()
    events["observation_date"] = pd.to_datetime(events["observation_date"])
    joined = join_events_impacts(data, impacts)
    years = list(range(2011, 2028))
    access_eff, _ = cumulative_event_effects(joined, "ACC_OWNERSHIP", years)
    usage_eff, _ = cumulative_event_effects(
        joined, "USG_DIGITAL_PAYMENT", years, form="linear_ramp"
    )
    bundle = build_forecast_bundle(obs, access_eff, usage_eff, [2025, 2026, 2027])
    matrix = build_association_matrix(joined)
    return data, impacts, obs, events, joined, bundle, matrix


data, impacts, obs, events, joined, bundle, matrix = load_all()

page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Trends", "Forecasts", "Inclusion Projections", "About"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Ethiopia FI Forecast** — Selam Analytics challenge dashboard")


def latest(code: str) -> float | None:
    s = obs[obs["indicator_code"] == code].sort_values("observation_date")
    if s.empty:
        return None
    return float(s["value_numeric"].iloc[-1])


if page == "Overview":
    st.title("Ethiopia Financial Inclusion — Overview")
    st.write(
        "Track Access (account ownership) and Usage (digital payments), "
        "event impacts, and 2025–2027 forecasts for consortium stakeholders."
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Account Ownership (Access)", f"{latest('ACC_OWNERSHIP'):.1f}%")
    c2.metric("Digital Payment Usage", f"{latest('USG_DIGITAL_PAYMENT'):.1f}%")
    c3.metric("Mobile Money Account Rate", f"{latest('ACC_MM_ACCOUNT'):.2f}%")
    crossover = latest("USG_CROSSOVER")
    c4.metric("P2P/ATM Crossover Ratio", f"{crossover:.2f}" if crossover else "n/a")

    access = obs[obs["indicator_code"] == "ACC_OWNERSHIP"].sort_values("observation_date")
    if len(access) >= 2:
        growth = float(access["value_numeric"].iloc[-1] - access["value_numeric"].iloc[-2])
        years = (
            access["observation_date"].dt.year.iloc[-1]
            - access["observation_date"].dt.year.iloc[-2]
        )
        st.info(
            f"Latest Access growth: **{growth:+.1f} pp** over {years} years "
            f"({growth/years:+.2f} pp/year)."
        )

    st.subheader("Event catalog snapshot")
    st.dataframe(
        events[["record_id", "category", "indicator", "observation_date"]].sort_values(
            "observation_date"
        ),
        use_container_width=True,
    )

elif page == "Trends":
    st.title("Trends")
    codes = sorted(obs["indicator_code"].dropna().unique())
    default = [c for c in ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT", "ACC_MM_ACCOUNT"] if c in codes]
    selected = st.multiselect("Indicators", codes, default=default)
    min_d, max_d = obs["observation_date"].min(), obs["observation_date"].max()
    date_range = st.slider(
        "Date range",
        min_value=min_d.to_pydatetime(),
        max_value=max_d.to_pydatetime(),
        value=(min_d.to_pydatetime(), max_d.to_pydatetime()),
    )
    plot_df = obs[
        (obs["indicator_code"].isin(selected))
        & (obs["observation_date"] >= pd.Timestamp(date_range[0]))
        & (obs["observation_date"] <= pd.Timestamp(date_range[1]))
    ]
    fig = px.line(
        plot_df,
        x="observation_date",
        y="value_numeric",
        color="indicator_code",
        markers=True,
        title="Interactive indicator time series",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Channel comparison (P2P vs ATM counts)")
    ch = obs[obs["indicator_code"].isin(["USG_P2P_COUNT", "USG_ATM_COUNT"])]
    if not ch.empty:
        fig2 = px.bar(
            ch,
            x="observation_date",
            y="value_numeric",
            color="indicator_code",
            barmode="group",
            title="P2P vs ATM transaction counts",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.download_button(
        "Download filtered observations (CSV)",
        plot_df.to_csv(index=False),
        file_name="filtered_observations.csv",
        mime="text/csv",
    )

elif page == "Forecasts":
    st.title("Forecasts (2025–2027)")
    model_choice = st.selectbox(
        "Model view",
        ["Event-augmented (recommended)", "Trend only", "Scenarios"],
    )
    summary = bundle["summary"]
    if model_choice == "Trend only":
        access_df = bundle["access_trend"].rename(columns={"point": "Access"})
        usage_df = bundle["usage_trend"].rename(columns={"point": "Usage"})
        chart = access_df[["year", "Access"]].merge(
            usage_df[["year", "Usage"]], on="year"
        )
        fig = px.line(chart, x="year", y=["Access", "Usage"], markers=True, title="Trend forecasts")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(chart)
    elif model_choice == "Scenarios":
        scen = st.radio("Pillar", ["Access", "Usage"], horizontal=True)
        key = "access_scenarios" if scen == "Access" else "usage_scenarios"
        sdf = bundle[key]
        fig = px.line(
            sdf,
            x="year",
            y="value",
            color="scenario",
            markers=True,
            title=f"{scen} scenarios",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(sdf)
    else:
        fig = px.line(
            summary,
            x="year",
            y=["access_base", "usage_base"],
            markers=True,
            title="Event-augmented base forecasts",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(summary)
        st.caption("Intervals shown in summary columns *_lower / *_upper.")

    st.subheader("Association matrix (event → indicator)")
    if not matrix.empty:
        st.dataframe(matrix.style.format("{:.1f}"), use_container_width=True)

    st.download_button(
        "Download forecast summary (CSV)",
        summary.to_csv(index=False),
        file_name="forecast_summary.csv",
        mime="text/csv",
    )

elif page == "Inclusion Projections":
    st.title("Inclusion Projections")
    st.write(
        "Progress toward national inclusion ambitions and answers to consortium questions."
    )
    scenario = st.selectbox("Scenario", ["pessimistic", "base", "optimistic"], index=1)
    access_sc = bundle["access_scenarios"]
    usage_sc = bundle["usage_scenarios"]
    a = access_sc[access_sc["scenario"] == scenario]
    u = usage_sc[usage_sc["scenario"] == scenario]

    target = 60.0
    fig = px.line(a, x="year", y="value", markers=True, title=f"Access vs {target:.0f}% reference target")
    fig.add_hline(y=target, line_dash="dash", annotation_text=f"{target:.0f}% reference")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Access projection")
        st.dataframe(a)
    with c2:
        st.subheader("Usage projection")
        st.dataframe(u)

    st.markdown("### Consortium questions")
    st.markdown(
        """
- **What drives inclusion?** Mobile money product launches, agent/KYC facilitation, connectivity, digital ID, and merchant acceptance — but **survey Access** responds much more slowly than registered-user counts.
- **How do events affect outcomes?** See impact links / association matrix: Telebirr and M-Pesa lift Usage more reliably than national Access; interoperability and QR expansion amplify payment intensity.
- **2025–2027 outlook?** Usage continues rising under base/optimistic paths; Access gains remain gradual unless rural and gender gaps close. Wide intervals reflect sparse Findex history.
"""
    )

else:
    st.title("About")
    st.markdown(
        """
This dashboard supports the 10 Academy Week 11 challenge: forecasting Ethiopia's
financial inclusion Access and Usage indicators.

**Run locally**

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

**Data:** `data/raw/` and `data/processed/`  
**Enrichment log:** `data_enrichment_log.md`  
**Notebooks:** `notebooks/`
"""
    )
    st.download_button(
        "Download full observations (CSV)",
        obs.to_csv(index=False),
        file_name="ethiopia_fi_observations.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download impact links (CSV)",
        impacts.to_csv(index=False),
        file_name="impact_links.csv",
        mime="text/csv",
    )
