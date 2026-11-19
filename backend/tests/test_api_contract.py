from fastapi import Query
from fastapi.testclient import TestClient

from app.main import app
from app.core.responses import build_pagination_meta
from app.db.store import get_document_store
from app.core.adapters import InMemoryDocumentStoreStub

client = TestClient(app)


def assert_utc_timestamp(value: str) -> None:
    assert value.endswith("Z")


def test_health_uses_common_envelope_and_utc_timestamp():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"] == {"status": "ok", "database": "ok"}
    assert body["meta"]["request_id"]
    assert_utc_timestamp(body["meta"]["timestamp"])


def test_unknown_route_uses_common_json_404():
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["request_id"]
    assert_utc_timestamp(body["meta"]["timestamp"])


def test_request_validation_uses_common_json_error():
    def validation_probe(required_number: int = Query(..., ge=1)):
        return {"value": required_number}

    app.add_api_route("/__test__/validation", validation_probe, methods=["GET"])
    response = client.get("/__test__/validation", params={"required_number": "nope"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"]["fields"]
    assert_utc_timestamp(body["meta"]["timestamp"])


def test_pagination_contract_uses_one_based_page_and_rounded_page_count():
    meta = build_pagination_meta(page=2, page_size=10, total_items=21)

    assert meta.model_dump() == {
        "page": 2,
        "page_size": 10,
        "total_items": 21,
        "total_pages": 3,
    }


def test_health_returns_common_service_error_when_document_store_is_unavailable():
    class UnavailableStore:
        def ping(self):
            raise ConnectionError("synthetic store failure")

    app.dependency_overrides[get_document_store] = lambda: UnavailableStore()
    try:
        response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.pop(get_document_store, None)

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "DATABASE_UNAVAILABLE"
    assert body["error"]["request_id"]
    assert_utc_timestamp(body["meta"]["timestamp"])


def test_application_is_written_and_visible_in_admin_backend(monkeypatch):
    import app.api.v1.applications as applications_api

    store = InMemoryDocumentStoreStub()
    app.dependency_overrides[get_document_store] = lambda: store
    monkeypatch.setattr(applications_api, "get_settings", lambda: type("Settings", (), {"admin_auth_mode": "token", "admin_api_token": "local-test-secret"})())
    payload = {
        "kind": "FORMAL", "display_name": "合成測試者", "email": "synthetic@example.test", "age": 35,
        "gender": "其他", "stages": ["STAGE_1"], "months": ["2027-04"], "expectations": [],
        "source": "MANUAL", "adult_single_confirmed": True, "privacy_confirmed": True,
        "safety_confirmed": True, "recording_consents": {},
    }
    try:
        created = client.post("/api/v1/applications", json=payload)
        assert created.status_code == 201
        application_id = created.json()["data"]["id"]
        assert store.get("applications", application_id)["display_name"] == "合成測試者"

        forbidden = client.get("/api/v1/admin/applications")
        assert forbidden.status_code == 401
        listed = client.get("/api/v1/admin/applications", headers={"Authorization": "Bearer local-test-secret"})
    finally:
        app.dependency_overrides.pop(get_document_store, None)

    assert listed.status_code == 200
    body = listed.json()
    assert body["data"][0]["id"] == application_id
    assert body["data"][0]["email"] == "synthetic@example.test"
    assert body["meta"]["pagination"]["total_items"] == 1
    assert_utc_timestamp(body["meta"]["timestamp"])


def test_application_requires_all_disclosure_consents():
    payload = {
        "kind": "FORMAL", "display_name": "Synthetic", "email": "synthetic@example.test", "age": 35,
        "gender": "女性", "stages": ["STAGE_1"], "months": ["2027-04"], "expectations": [],
        "source": "MANUAL", "adult_single_confirmed": True, "privacy_confirmed": False,
        "safety_confirmed": True, "recording_consents": {},
    }
    response = client.post("/api/v1/applications", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
