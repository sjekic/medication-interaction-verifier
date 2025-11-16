import importlib.util
import pathlib
import sys
from fastapi.testclient import TestClient


def load_main():
    root = pathlib.Path(__file__).resolve().parents[1]
    main_path = root / "main.py"
    
    spec = importlib.util.spec_from_file_location("main", main_path)
    main = importlib.util.module_from_spec(spec)
    sys.modules["main"] = main
    spec.loader.exec_module(main)
    return main

def test_health_endpoint():
    main = load_main()
    client = TestClient(main.app)
    
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["db"] in ("ok", "error")
    assert "version" in data
    
def test_metrics_exposed():
    main = load_main()
    client = TestClient(main.app)
    
    resp = client.get("/metrics")
    assert resp.status_code == 200
    text = resp.text
    assert "help" in text.lower() or "http" in text.lower()