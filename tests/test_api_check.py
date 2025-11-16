# tests/test_api_check.py

import importlib.util
import pathlib
import sys
from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
main_path = ROOT / "main.py"

spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
sys.modules["main"] = main
spec.loader.exec_module(main)

app = main.app
client = TestClient(app) #this allows to run tests using FastAPI without starting the server

def test_check_known_interaction():
    #this test simulates a POST request to /check
    resp = client.post(
        "/check",
        json={"drug_a": "ibuprofen", "drug_b": "aspirin"},
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["found"] is True
    assert data["severity"] in {"contraindicated", "major", "moderate", "minor"}
    assert isinstance(data["description"], str)
    assert data["description"] != ""
    assert data.get("suggest_add") in (None, False)


def test_check_unknown_interaction():
    resp = client.post(
        "/check",
        json={"drug_a": "medX_not_real", "drug_b": "medY_not_real"},
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["found"] is False
    assert data.get("severity") is None
    assert data.get("description") is None
    assert data["suggest_add"] is True
    assert isinstance(data["how_to_add"], dict)
    assert data["how_to_add"]["endpoint"] == "POST /rules"
