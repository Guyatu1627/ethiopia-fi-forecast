# Ethiopia Financial Inclusion Forecast

Forecasting system for Ethiopia's **Access** (account ownership) and **Usage** (digital payment adoption) using a unified observation/event/impact schema, event-impact modeling, scenario forecasts for 2025–2027, and an interactive Streamlit dashboard.

**GitHub:** https://github.com/Guyatu1627/ethiopia-fi-forecast

## Project structure

```
ethiopia-fi-forecast/
├── data/raw/                 # Starter + enriched CSVs, reference codes
├── data/processed/           # Analysis-ready exports
├── notebooks/                # Tasks 1–4 notebooks
├── src/                      # Loaders, EDA, impact model, forecasts
├── dashboard/app.py          # Streamlit dashboard (Task 5)
├── models/                   # Association matrix + forecast tables
├── reports/                  # Insights, methodology, interim/final reports
├── tests/
├── data_enrichment_log.md
└── requirements.txt
```

## Setup

```bash
python -m pip install -r requirements.txt
```

Optional: regenerate processed CSVs from the builder (CSVs in `data/raw/` are the source of truth for analysis):

```bash
python -m src.data_processing
```

## Run the dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard pages: **Overview**, **Trends**, **Forecasts**, **Inclusion Projections** (4+ interactive charts, downloads, scenario selector).

## Notebooks

| Notebook | Task |
|----------|------|
| `notebooks/01_task1_exploration_enrichment.ipynb` | Schema + enrichment checks |
| `notebooks/02_task2_eda.ipynb` | EDA + visualizations |
| `notebooks/03_task3_impact_modeling.ipynb` | Association matrix + validation |
| `notebooks/04_task4_forecasting.ipynb` | 2025–2027 scenarios |

```bash
jupyter notebook notebooks/
```

## Git workflow (challenge branches)

```bash
git checkout -b task-1   # enrichment
git checkout -b task-2   # EDA
git checkout -b task-3   # impact modeling
git checkout -b task-4   # forecasting
git checkout -b task-5   # dashboard
```

Before pushing each branch:

```bash
git fetch origin
git merge origin/main
git push -u origin <branch>
```

Open a Pull Request into `main` after each task.

## Reports

- Interim: `reports/interim_report.md`
- Final (blog style): `reports/final_report.md`
- Enrichment log: `data_enrichment_log.md`

## Tests

```bash
pytest -q
```
