from src.data_loader import load_unified_data, load_impact_sheet, load_reference_codes


def test_load_unified_data():
    df = load_unified_data()
    assert not df.empty
    assert "record_type" in df.columns
    assert set(df["record_type"].unique()) >= {"observation", "event", "target"}


def test_load_impact_sheet():
    df = load_impact_sheet()
    assert not df.empty
    assert "parent_id" in df.columns


def test_load_reference_codes():
    df = load_reference_codes()
    assert not df.empty
    assert "code" in df.columns
