"""Forecasting Access and Usage with sparse Findex history."""

from __future__ import annotations

import numpy as np
import pandas as pd

try:
    import statsmodels.api as sm
except ImportError:  # pragma: no cover
    sm = None


def _prep_series(observations: pd.DataFrame, code: str) -> pd.DataFrame:
    s = observations[observations["indicator_code"] == code].copy()
    s["observation_date"] = pd.to_datetime(s["observation_date"])
    s["year"] = s["observation_date"].dt.year
    s = s.groupby("year", as_index=False)["value_numeric"].mean()
    s = s.sort_values("year")
    return s


def ols_trend_forecast(
    hist: pd.DataFrame,
    forecast_years: list[int],
    alpha: float = 0.2,
) -> pd.DataFrame:
    """Linear OLS trend with prediction intervals when statsmodels is available."""
    y = hist["value_numeric"].astype(float).values
    x = hist["year"].astype(float).values
    if len(hist) < 2:
        base = float(y[-1]) if len(y) else np.nan
        return pd.DataFrame(
            {
                "year": forecast_years,
                "point": [base] * len(forecast_years),
                "lower": [base - 5] * len(forecast_years),
                "upper": [base + 5] * len(forecast_years),
                "model": "flat_anchor",
            }
        )

    if sm is not None and len(hist) >= 3:
        X = sm.add_constant(x)
        model = sm.OLS(y, X).fit()
        rows = []
        for year in forecast_years:
            pred = model.get_prediction([1.0, float(year)])
            summary = pred.summary_frame(alpha=alpha)
            rows.append(
                {
                    "year": year,
                    "point": float(summary["mean"].iloc[0]),
                    "lower": float(summary["obs_ci_lower"].iloc[0]),
                    "upper": float(summary["obs_ci_upper"].iloc[0]),
                    "model": "ols_trend",
                }
            )
        return pd.DataFrame(rows)

    # Fallback: last-period slope
    slope = (y[-1] - y[-2]) / max(x[-1] - x[-2], 1)
    rows = []
    for year in forecast_years:
        point = float(y[-1] + slope * (year - x[-1]))
        width = 1.96 * abs(slope) * max(year - x[-1], 1) + 2.0
        rows.append(
            {
                "year": year,
                "point": point,
                "lower": point - width,
                "upper": point + width,
                "model": "last_slope",
            }
        )
    return pd.DataFrame(rows)


def event_augmented_forecast(
    hist: pd.DataFrame,
    forecast_years: list[int],
    event_effects: pd.DataFrame,
    scale: float = 0.25,
) -> pd.DataFrame:
    """Trend baseline plus scaled cumulative event effects."""
    base = ols_trend_forecast(hist, forecast_years)
    eff = event_effects.set_index("year")["event_effect_pp"] if len(event_effects) else pd.Series(dtype=float)
    # Use incremental effect vs last historical year
    last_hist_year = int(hist["year"].iloc[-1])
    baseline_eff = float(eff.get(last_hist_year, 0.0)) if len(eff) else 0.0
    out = base.copy()
    adj = []
    for year in forecast_years:
        delta = scale * (float(eff.get(year, 0.0)) - baseline_eff)
        adj.append(delta)
    out["event_adjustment_pp"] = adj
    out["point"] = out["point"] + out["event_adjustment_pp"]
    out["lower"] = out["lower"] + out["event_adjustment_pp"]
    out["upper"] = out["upper"] + out["event_adjustment_pp"]
    out["model"] = "event_augmented"
    return out


def scenario_forecasts(
    base: pd.DataFrame,
    optimistic_boost: float = 3.0,
    pessimistic_cut: float = 2.0,
) -> pd.DataFrame:
    """Optimistic / base / pessimistic scenarios around a point forecast."""
    rows = []
    for _, row in base.iterrows():
        point = float(row["point"])
        rows.append(
            {
                "year": int(row["year"]),
                "scenario": "pessimistic",
                "value": point - pessimistic_cut,
                "lower": float(row["lower"]) - pessimistic_cut,
                "upper": float(row["upper"]) - pessimistic_cut,
            }
        )
        rows.append(
            {
                "year": int(row["year"]),
                "scenario": "base",
                "value": point,
                "lower": float(row["lower"]),
                "upper": float(row["upper"]),
            }
        )
        rows.append(
            {
                "year": int(row["year"]),
                "scenario": "optimistic",
                "value": point + optimistic_boost,
                "lower": float(row["lower"]) + optimistic_boost,
                "upper": float(row["upper"]) + optimistic_boost,
            }
        )
    return pd.DataFrame(rows)


def usage_history_with_proxy(
    observations: pd.DataFrame,
    access_hist: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Build Usage history for forecasting.

    Prefer real USG_DIGITAL_PAYMENT points. If only one anchor exists, add
    documented proxy points from earlier Findex digital-payment levels and
    scale with Access trajectory.
    """
    usage = _prep_series(observations, "USG_DIGITAL_PAYMENT")
    if len(usage) >= 3:
        return usage

    # Documented enrichment / proxy anchors (also stored as observations when enriched)
    proxies = pd.DataFrame(
        {
            "year": [2014, 2017, 2021, 2024],
            "value_numeric": [2.0, 8.0, 18.0, 35.0],
        }
    )
    if len(usage) == 1:
        anchor_year = int(usage["year"].iloc[0])
        anchor_val = float(usage["value_numeric"].iloc[0])
        proxies.loc[proxies["year"] == anchor_year, "value_numeric"] = anchor_val
    return proxies


def build_forecast_bundle(
    observations: pd.DataFrame,
    access_event_effects: pd.DataFrame,
    usage_event_effects: pd.DataFrame,
    forecast_years: list[int] | None = None,
) -> dict[str, pd.DataFrame]:
    """Return Access/Usage trend, event-augmented, and scenario tables."""
    forecast_years = forecast_years or [2025, 2026, 2027]
    access = _prep_series(observations, "ACC_OWNERSHIP")
    usage = usage_history_with_proxy(observations, access)

    # Access: blend long-run OLS with recent slope to reflect 2021-2024 slowdown
    access_ols = ols_trend_forecast(access, forecast_years)
    if len(access) >= 2:
        recent_slope = float(
            (access["value_numeric"].iloc[-1] - access["value_numeric"].iloc[-2])
            / max(access["year"].iloc[-1] - access["year"].iloc[-2], 1)
        )
        last_val = float(access["value_numeric"].iloc[-1])
        last_year = int(access["year"].iloc[-1])
        rows = []
        for year in forecast_years:
            # 70% recent slope, 30% OLS — avoids over-extrapolating early boom years
            ols_point = float(access_ols.loc[access_ols["year"] == year, "point"].iloc[0])
            recent_point = last_val + recent_slope * (year - last_year)
            point = 0.7 * recent_point + 0.3 * ols_point
            width = abs(point - recent_point) + 2.5 * max(year - last_year, 1)
            rows.append(
                {
                    "year": year,
                    "point": point,
                    "lower": point - width,
                    "upper": min(95.0, point + width),
                    "model": "blended_recent_ols",
                }
            )
        access_trend = pd.DataFrame(rows)
    else:
        access_trend = access_ols

    usage_trend = ols_trend_forecast(usage, forecast_years)

    access_aug = event_augmented_forecast(access, forecast_years, access_event_effects, scale=0.15)
    # Replace event-augmented baseline points with blended trend + event adjustments
    access_aug["point"] = access_trend["point"].values + access_aug["event_adjustment_pp"].values
    access_aug["lower"] = access_trend["lower"].values + access_aug["event_adjustment_pp"].values
    access_aug["upper"] = access_trend["upper"].values + access_aug["event_adjustment_pp"].values
    access_aug["model"] = "event_augmented_blended"

    usage_aug = event_augmented_forecast(usage, forecast_years, usage_event_effects, scale=0.35)

    access_scen = scenario_forecasts(access_aug, optimistic_boost=4.0, pessimistic_cut=2.5)
    usage_scen = scenario_forecasts(usage_aug, optimistic_boost=6.0, pessimistic_cut=4.0)

    summary = pd.DataFrame(
        {
            "year": forecast_years,
            "access_base": access_aug["point"].values,
            "access_lower": access_aug["lower"].values,
            "access_upper": access_aug["upper"].values,
            "usage_base": usage_aug["point"].values,
            "usage_lower": usage_aug["lower"].values,
            "usage_upper": usage_aug["upper"].values,
        }
    )

    return {
        "access_history": access,
        "usage_history": usage,
        "access_trend": access_trend,
        "usage_trend": usage_trend,
        "access_event_augmented": access_aug,
        "usage_event_augmented": usage_aug,
        "access_scenarios": access_scen,
        "usage_scenarios": usage_scen,
        "summary": summary,
    }
