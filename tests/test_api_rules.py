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


def get_client_and_main():
    main = load_main()
    app = main.app
    client = TestClient(app)
    return client, main


def test_list_rules_non_empty():
    #this simulates a GET request to /rules
    client, _ = get_client_and_main()

    resp = client.get("/rules")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    for key in ("id", "a", "b", "severity", "description"):
        assert key in first


def test_get_rule_by_id_and_404_for_missing():
    #this tests getting a specific rule by its ID and also checks for 404 on non-existing rule
    client, _ = get_client_and_main()

    list_resp = client.get("/rules")
    assert list_resp.status_code == 200
    rules = list_resp.json()
    existing_id = rules[0]["id"]

    resp = client.get(f"/rules/{existing_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == existing_id

    resp_404 = client.get("/rules/__non_existing_rule__")
    assert resp_404.status_code == 404


def test_create_update_delete_rule_lifecycle():
    #this tests creating, updating, and deleting a rule
    client, _ = get_client_and_main()

    new_rule = {
        "id": "test_rule_xyz",
        "a": "testdruga",
        "b": "testdrugb",
        "severity": "moderate",
        "description": "Test interaction for CI",
    }

    create_resp = client.post("/rules", json=new_rule)
    assert create_resp.status_code == 200
    body = create_resp.json()
    assert body["ok"] is True
    rule_id = body["id"]

    update_resp = client.put(
        f"/rules/{rule_id}",
        params={"severity": "minor", "description": "Updated description"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["ok"] is True

    delete_resp = client.delete(f"/rules/{rule_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["ok"] is True

    delete_404 = client.delete(f"/rules/{rule_id}")
    assert delete_404.status_code == 404


def test_create_rule_rejects_invalid_severity():
    #tests that creating a rule with invalid severity is rejected
    client, _ = get_client_and_main()

    bad_rule = {
        "id": "bad_rule_1",
        "a": "badA",
        "b": "badB",
        "severity": "not_a_real_level",
        "description": "Should fail",
    }

    resp = client.post("/rules", json=bad_rule)
    assert resp.status_code == 400


def test_update_rule_rejects_invalid_severity():
    #tests that updating a rule with invalid severity is rejected
    client, _ = get_client_and_main()

    resp = client.put(
        "/rules/some_id",
        params={"severity": "wrong", "description": "whatever"},
    )
    assert resp.status_code == 400
