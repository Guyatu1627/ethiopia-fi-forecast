"""Export model artifacts used by reports and the dashboard."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_unified_data, load_impact_sheet
from src.impact_model import (
    join_events_impacts,
    impact_summary,
    build_association_matrix,
    cumulative_event_effects,
    validate_telebirr_mm_impact,
)
from src.forecast import build_forecast_bundle


def main() -> None:
    models = ROOT / "models"
    figs = ROOT / "reports" / "figures"
    models.mkdir(exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    data = load_unified_data()
    impacts = load_impact_sheet()
    obs = data[data["record_type"] == "observation"].copy()
    joined = join_events_impacts(data, impacts)

    summary = impact_summary(joined)
    summary.to_csv(models / "event_impact_summary.csv", index=False)

    matrix = build_association_matrix(joined)
    matrix.to_csv(models / "association_matrix.csv")

    years = list(range(2011, 2028))
    access_eff, _ = cumulative_event_effects(joined, "ACC_OWNERSHIP", years)
    usage_eff, _ = cumulative_event_effects(
        joined, "USG_DIGITAL_PAYMENT", years, form="linear_ramp"
    )
    access_eff.to_csv(models / "access_event_path.csv", index=False)
    usage_eff.to_csv(models / "usage_event_path.csv", index=False)

    bundle = build_forecast_bundle(obs, access_eff, usage_eff, [2025, 2026, 2027])
    bundle["summary"].to_csv(models / "forecast_summary.csv", index=False)
    bundle["access_scenarios"].to_csv(models / "access_scenarios.csv", index=False)
    bundle["usage_scenarios"].to_csv(models / "usage_scenarios.csv", index=False)

    import json

    (models / "validation_telebirr.json").write_text(
        json.dumps(validate_telebirr_mm_impact(joined), indent=2), encoding="utf-8"
    )
    print("Exported model artifacts to", models)
    print(bundle["summary"])


if __name__ == "__main__":
    main()
