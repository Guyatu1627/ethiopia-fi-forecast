"""Event impact modeling for Ethiopia financial inclusion indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd


MAGNITUDE_TO_PP = {"high": 8.0, "medium": 4.0, "low": 1.5}


def join_events_impacts(events: pd.DataFrame, impacts: pd.DataFrame) -> pd.DataFrame:
    """Join impact_links to events via parent_id."""
    event_cols = [
        "record_id",
        "indicator",
        "category",
        "observation_date",
        "notes",
        "source_name",
    ]
    ev = events[events["record_type"] == "event"][event_cols].rename(
        columns={
            "record_id": "event_id",
            "indicator": "event_name",
            "observation_date": "event_date",
            "notes": "event_notes",
            "source_name": "event_source",
        }
    )
    merged = impacts.merge(ev, left_on="parent_id", right_on="event_id", how="left")
    return merged


def impact_summary(joined: pd.DataFrame) -> pd.DataFrame:
    """Compact summary: event -> indicator effects."""
    cols = [
        "event_id",
        "event_name",
        "category",
        "event_date",
        "pillar",
        "related_indicator",
        "impact_direction",
        "impact_magnitude",
        "impact_estimate",
        "lag_months",
        "evidence_basis",
        "comparable_country",
        "confidence",
    ]
    available = [c for c in cols if c in joined.columns]
    out = joined[available].copy()
    if "related_indicator" not in out.columns and "indicator_code" in joined.columns:
        out["related_indicator"] = joined["indicator_code"]
    return out.sort_values(["event_date", "event_id"], na_position="last")


def _effect_value(row: pd.Series) -> float:
    est = row.get("impact_estimate")
    if pd.notna(est):
        return float(est)
    mag = str(row.get("impact_magnitude", "medium")).lower()
    base = MAGNITUDE_TO_PP.get(mag, 4.0)
    direction = str(row.get("impact_direction", "increase")).lower()
    if direction in {"decrease", "negative", "neg"}:
        return -abs(base)
    return abs(base)


def build_association_matrix(joined: pd.DataFrame) -> pd.DataFrame:
    """Rows = events, columns = indicators, values = estimated effect size."""
    rows = []
    for _, row in joined.iterrows():
        indicator = row.get("related_indicator") or row.get("indicator_code")
        event_label = row.get("event_name") or row.get("event_id") or row.get("parent_id")
        if pd.isna(indicator) or pd.isna(event_label):
            continue
        rows.append(
            {
                "event": event_label,
                "event_id": row.get("event_id") or row.get("parent_id"),
                "indicator": indicator,
                "effect": _effect_value(row),
            }
        )
    if not rows:
        return pd.DataFrame()
    long = pd.DataFrame(rows)
    matrix = long.pivot_table(index="event", columns="indicator", values="effect", aggfunc="sum", fill_value=0.0)
    return matrix.sort_index()


def event_effect_path(
    event_date: pd.Timestamp,
    magnitude: float,
    lag_months: float,
    years: list[int],
    form: str = "step_after_lag",
) -> pd.Series:
    """
    Map a single event shock onto calendar years.

    form='step_after_lag': full effect from year containing (event_date + lag)
    form='linear_ramp': linear ramp from event year to lag horizon, then flat
    """
    event_date = pd.Timestamp(event_date)
    lag_months = float(lag_months) if pd.notna(lag_months) else 0.0
    effect_start = event_date + pd.DateOffset(months=int(lag_months))
    out = {}
    for y in years:
        year_end = pd.Timestamp(f"{y}-12-31")
        if form == "linear_ramp":
            if year_end < event_date:
                out[y] = 0.0
            elif year_end >= effect_start:
                out[y] = magnitude
            else:
                total_days = max((effect_start - event_date).days, 1)
                elapsed = (year_end - event_date).days
                out[y] = magnitude * min(max(elapsed / total_days, 0.0), 1.0)
        else:
            out[y] = magnitude if year_end >= effect_start else 0.0
    return pd.Series(out, name="effect")


def cumulative_event_effects(
    joined: pd.DataFrame,
    indicator: str,
    years: list[int],
    form: str = "step_after_lag",
    scale: float = 1.0,
) -> pd.DataFrame:
    """Sum scaled event effects on one indicator across years."""
    subset = joined.copy()
    ind_col = "related_indicator" if "related_indicator" in subset.columns else "indicator_code"
    subset = subset[subset[ind_col] == indicator]
    total = pd.Series(0.0, index=years)
    contributions = []
    for _, row in subset.iterrows():
        mag = _effect_value(row) * scale
        path = event_effect_path(row["event_date"], mag, row.get("lag_months", 0), years, form=form)
        total = total.add(path, fill_value=0.0)
        contributions.append(
            {
                "event_id": row.get("event_id") or row.get("parent_id"),
                "event_name": row.get("event_name"),
                "magnitude": mag,
                **{str(y): path.get(y, 0.0) for y in years},
            }
        )
    return pd.DataFrame({"year": years, "event_effect_pp": [total.get(y, 0.0) for y in years]}), pd.DataFrame(
        contributions
    )


def validate_telebirr_mm_impact(joined: pd.DataFrame) -> dict:
    """
    Check Telebirr impact estimate vs observed MM account growth.
    Observed: ACC_MM_ACCOUNT 4.7% (2021) -> 9.45% (2024) = +4.75 pp.
    """
    observed_delta = 9.45 - 4.7
    event_id = joined["event_id"] if "event_id" in joined.columns else joined["parent_id"]
    name = joined["event_name"] if "event_name" in joined.columns else pd.Series("", index=joined.index)
    telebirr = joined[
        (event_id == "EVT_0001")
        | name.astype(str).str.contains("Telebirr", case=False, na=False)
    ]
    ind_col = "related_indicator" if "related_indicator" in joined.columns else "indicator_code"
    mm_links = telebirr[telebirr[ind_col].isin(["ACC_MM_ACCOUNT", "USG_TELEBIRR_USERS"])]
    predicted = float(mm_links.apply(_effect_value, axis=1).sum()) if len(mm_links) else np.nan

    access_links = joined[joined[ind_col] == "ACC_OWNERSHIP"]
    access_pred = float(access_links.apply(_effect_value, axis=1).sum()) if len(access_links) else np.nan
    access_obs = 3.0

    return {
        "mm_observed_delta_pp": observed_delta,
        "mm_related_predicted_sum": predicted,
        "access_observed_delta_2021_2024_pp": access_obs,
        "access_impact_links_sum_pp": access_pred,
        "interpretation": (
            "Registered mobile-money users grew much faster than survey-reported "
            "ownership/usage. Impact magnitudes on registered users should not be "
            "naively applied 1:1 to Findex Access rates."
        ),
        "refined_access_scale": (access_obs / access_pred) if access_pred and access_pred != 0 else None,
    }
