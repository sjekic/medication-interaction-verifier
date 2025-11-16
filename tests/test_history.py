import importlib.util
import json
import pathlib
import sys
from fastapi.testclient import TestClient

def load_main():
    """Dynamically load main.py as the 'main' module."""
    root = pathlib.Path(__file__).resolve().parents[1]
    main_path = root / "main.py"

    spec = importlib.util.spec_from_file_location("main", main_path)
    main = importlib.util.module_from_spec(spec)
    sys.modules["main"] = main
    spec.loader.exec_module(main)
    return main


def test_ensure_history_creates_file(tmp_path):
    #this creates a temporary path for testing that overrides the real history path
    main = load_main()
    main.HISTORY_PATH = tmp_path / "history.json"
    assert not main.HISTORY_PATH.exists()

    main.ensure_history_file()

    assert main.HISTORY_PATH.exists()
    data = json.loads(main.HISTORY_PATH.read_text(encoding="utf-8"))
    assert data == []


def test_get_history_uses_limit(tmp_path):
    main = load_main()

    main.HISTORY_PATH = tmp_path / "history.json"
    main.ensure_history_file()

    entries = [
        {"drug_a": "a", "drug_b": "b", "found": False, "severity": None, "timestamp": 1},
        {"drug_a": "c", "drug_b": "d", "found": True, "severity": "major", "timestamp": 2},
    ]
    main.HISTORY_PATH.write_text(json.dumps(entries), encoding="utf-8")

    result = main.get_history(limit=1)

    assert len(result) == 1
    assert result[0]["drug_a"] == "c"
    assert result[0]["drug_b"] == "d"
    
    #this checks if only the last entry is returned when the limit is set to 1