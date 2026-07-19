from pathlib import Path
import pandas as pd

from .data_processing import build_event_records, build_impact_links, build_unified_dataset

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def _first_existing(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


def _read_table(path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, parse_dates=["observation_date"])
    return pd.read_excel(path, sheet_name=sheet_name, parse_dates=["observation_date"])


def load_unified_data(path: Path | str | None = None) -> pd.DataFrame:
    """Load main unified dataset. Prefer enriched CSV over legacy workbook."""
    if path is not None:
        return _read_table(Path(path), sheet_name="ethiopia_fi_unified_data")

    candidate = _first_existing(
        [
            PROCESSED_DIR / "ethiopia_fi_unified_data.csv",
            RAW_DIR / "ethiopia_fi_unified_data.csv",
            RAW_DIR / "ethiopia_fi_unified_data.xlsx",
        ]
    )
    if candidate is not None:
        return _read_table(candidate, sheet_name="ethiopia_fi_unified_data")

    df = pd.concat(
        [build_unified_dataset(), build_event_records()],
        ignore_index=True,
        sort=False,
    )
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DIR / "ethiopia_fi_unified_data.csv", index=False)
    return df


def load_impact_sheet(path: Path | str | None = None) -> pd.DataFrame:
    """Load impact links. Prefer enriched CSV over legacy workbook sheet."""
    if path is not None:
        return _read_table(Path(path), sheet_name="Impact_sheet")

    candidate = _first_existing(
        [
            PROCESSED_DIR / "impact_links.csv",
            RAW_DIR / "impact_links.csv",
            RAW_DIR / "ethiopia_fi_unified_data.xlsx",
        ]
    )
    if candidate is not None:
        sheet = "Impact_sheet" if candidate.suffix.lower() == ".xlsx" else None
        return _read_table(candidate, sheet_name=sheet)

    df = build_impact_links()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DIR / "impact_links.csv", index=False)
    return df


def load_reference_codes(path: Path | str | None = None) -> pd.DataFrame:
    if path is not None:
        p = Path(path)
        if p.suffix.lower() == ".csv":
            return pd.read_csv(p)
        return pd.read_excel(p, sheet_name="reference_codes")

    candidate = _first_existing(
        [
            RAW_DIR / "reference_codes.csv",
            RAW_DIR / "reference_codes.xlsx",
        ]
    )
    if candidate is not None:
        if candidate.suffix.lower() == ".csv":
            return pd.read_csv(candidate)
        return pd.read_excel(candidate, sheet_name="reference_codes")

    return pd.DataFrame(
        {
            "field": ["record_type", "pillar", "indicator_code"],
            "code": ["observation", "ACCESS", "ACC_OWNERSHIP"],
            "description": ["Actual measured value", "Access pillar", "Account ownership indicator"],
            "applies_to": ["All", "All", "All"],
        }
    )


def save_processed_csv(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    main_df.to_csv(PROCESSED_DIR / "ethiopia_fi_unified_data.csv", index=False)
    impact_df.to_csv(PROCESSED_DIR / "impact_links.csv", index=False)
