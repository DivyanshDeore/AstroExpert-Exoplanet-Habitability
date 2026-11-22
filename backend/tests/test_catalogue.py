import json
from pathlib import Path

def test_bundled_catalogue_is_full_nasa_snapshot():
    data_dir = Path(__file__).parents[1] / "app" / "data"
    payload = json.loads((data_dir / "exoplanets.json").read_text(encoding="utf-8"))
    assert payload["table"] == "PSCompPars"
    assert payload["source_row_count"] == 6470
    assert payload["source_column_count"] == 703
    assert len(payload["records"]) == 6470
    assert len({row["name"] for row in payload["records"]}) == 6470
    assert all(row["name"] for row in payload["records"])
    assert (data_dir / "nasa_pscomppars_full.csv").exists()

def test_unknown_measurements_remain_null():
    data_dir = Path(__file__).parents[1] / "app" / "data"
    payload = json.loads((data_dir / "exoplanets.json").read_text(encoding="utf-8"))
    assert any(row["radius_earth"] is None for row in payload["records"])
    assert any(row["semi_major_axis_au"] is None for row in payload["records"])
