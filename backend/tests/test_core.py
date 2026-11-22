from app.engine.calculations import stellar_flux, relative_density, simplified_hz
from app.engine.inference_engine import run_rules
import pytest

def test_flux():
    assert stellar_flux(0.5, 0.7) == pytest.approx(1.02040816)

def test_density():
    assert relative_density(1, 1) == 1

def test_hz():
    assert simplified_hz(1) == {"inner_au": 0.95, "outer_au": 1.67}

def test_rule_chain():
    rules = [
        {"id":"1","title":"first","conditions":["a"],"conclusion":"b","explanation":"A gives B"},
        {"id":"2","title":"second","conditions":["b"],"conclusion":"c","explanation":"B gives C"}
    ]
    result = run_rules({"a"}, rules)
    assert "c" in result["facts"]
    assert len(result["fired_rules"]) == 2
