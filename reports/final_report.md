# Forecasting Financial Inclusion in Ethiopia

*Final report (blog-post format) — 10 Academy Week 11 Challenge*

## Executive summary
Ethiopia’s digital finance market expanded rapidly—Telebirr, M-Pesa, and interoperable P2P rails—yet Global Findex **account ownership** only rose from **46% (2021) to 49% (2024)**. Using a unified observation/event/impact schema, we enrich the starter data, estimate event effects, and forecast **Access** and **Usage** for **2025–2027** with scenario ranges. The central finding: **registered mobile-money growth is not the same as survey-measured inclusion**; Usage has more near-term upside than Access unless rural and active-use gaps close.

## Data and methodology
- **Schema:** observations (measured), events (neutral categories), targets, and `impact_link` rows connecting events→indicators via `parent_id`.
- **Enrichment:** Usage history, gender/urban-rural splits, registered–survey gap, regulatory/merchant events (`data_enrichment_log.md`).
- **EDA:** coverage heatmaps, growth rates, event overlays, correlations (`notebooks/02_task2_eda.ipynb`).
- **Impact model:** association matrix + lagged additive shocks; validation against Telebirr-era deltas (`notebooks/03_task3_impact_modeling.ipynb`).
- **Forecasts:** OLS/trend + event-augmented paths; optimistic/base/pessimistic scenarios with intervals (`notebooks/04_task4_forecasting.ipynb`).
- **Dashboard:** Streamlit app with Overview, Trends, Forecasts, Inclusion Projections (`dashboard/app.py`).

## Key insights from exploratory analysis
1. Access slowdown (+3pp) despite massive MM registration.
2. Registered ≠ active/survey-included.
3. Usage climbing toward one-third of adults making/receiving digital payments.
4. Gender and rural gaps remain structural constraints.
5. P2P/ATM crossover shows payment-channel shift ahead of ownership catch-up.

## Event impact model — results
Association matrix (`models/association_matrix.csv`) highlights product launches and interoperability as primary Usage drivers. Access impacts were **scaled down** after validation against the 2021–2024 Findex slowdown. Assumptions and uncertainties are documented in `reports/impact_methodology.md`.

## Forecasts for Access and Usage
Base event-augmented forecasts (see `models/forecast_summary.csv`) project:
- **Access:** continued but gradual gains from 49%, with wide bands.
- **Usage:** stronger upward trajectory from 35%, especially under optimistic interoperability/merchant scenarios.

Uncertainty is large by design—five Access survey points cannot identify a high-precision path.

## Dashboard
Run locally:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Pages cover KPI cards (including P2P/ATM crossover), interactive trends with download, forecast model toggles, and scenario progress toward a 60% reference inclusion level.

## Limitations and future work
Richer high-frequency admin data, Findex microdata for regional panels, and causal designs (synthetic control / event studies with comparable countries) would tighten intervals. Converting registered users to **90-day active** survey-equivalent metrics is the highest-value measurement upgrade.

---
*Built for Selam Analytics’ consortium engagement — Week 11 challenge deliverable.*
