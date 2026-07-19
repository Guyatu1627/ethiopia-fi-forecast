"""EDA helpers for Ethiopia financial inclusion data."""

from __future__ import annotations

import pandas as pd


def summarize_dataset(data: pd.DataFrame) -> dict[str, pd.Series]:
    """Summarize counts by key categorical fields."""
    out: dict[str, pd.Series] = {
        "record_type": data["record_type"].value_counts(dropna=False),
    }
    if "pillar" in data.columns:
        out["pillar"] = data["pillar"].value_counts(dropna=False)
    if "source_type" in data.columns:
        out["source_type"] = data["source_type"].value_counts(dropna=False)
    if "confidence" in data.columns:
        out["confidence"] = data["confidence"].value_counts(dropna=False)
    if "category" in data.columns:
        events = data[data["record_type"] == "event"]
        out["event_category"] = events["category"].value_counts(dropna=False)
    return out


def temporal_coverage(observations: pd.DataFrame) -> pd.DataFrame:
    """Year x indicator coverage matrix (1 if observed)."""
    obs = observations.copy()
    obs["observation_date"] = pd.to_datetime(obs["observation_date"], errors="coerce")
    obs["year"] = obs["observation_date"].dt.year
    coverage = (
        obs.dropna(subset=["year", "indicator_code"])
        .groupby(["indicator_code", "year"])
        .size()
        .unstack(fill_value=0)
    )
    return (coverage > 0).astype(int)


def growth_rates(series: pd.DataFrame, value_col: str = "value_numeric") -> pd.DataFrame:
    """Compute period-to-period growth (pp and CAGR-style annualized)."""
    s = series.sort_values("observation_date").copy()
    s["observation_date"] = pd.to_datetime(s["observation_date"])
    s["year"] = s["observation_date"].dt.year
    s["prev_value"] = s[value_col].shift(1)
    s["prev_year"] = s["year"].shift(1)
    s["delta_pp"] = s[value_col] - s["prev_value"]
    s["years"] = s["year"] - s["prev_year"]
    s["annualized_pp"] = s["delta_pp"] / s["years"]
    return s[["year", value_col, "prev_year", "prev_value", "delta_pp", "years", "annualized_pp"]].dropna()


def sparse_indicators(observations: pd.DataFrame, max_points: int = 2) -> pd.Series:
    """Indicators with sparse coverage."""
    counts = observations["indicator_code"].value_counts()
    return counts[counts <= max_points]


def indicator_correlations(observations: pd.DataFrame, codes: list[str] | None = None) -> pd.DataFrame:
    """Pearson correlations on yearly means of selected indicators."""
    obs = observations.copy()
    obs["observation_date"] = pd.to_datetime(obs["observation_date"], errors="coerce")
    obs["year"] = obs["observation_date"].dt.year
    if codes:
        obs = obs[obs["indicator_code"].isin(codes)]
    wide = (
        obs.groupby(["year", "indicator_code"])["value_numeric"]
        .mean()
        .unstack()
    )
    return wide.corr()
