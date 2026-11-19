from types import SimpleNamespace

import pytest

from app.api.v1 import applications as api
from app.core.adapters import InMemoryDocumentStoreStub
from app.core.errors import AppError


def request_context():
    return SimpleNamespace(state=SimpleNamespace(request_id="test-request"))


def payload(**changes):
    values = {
        "kind": "FORMAL",
        "display_name": "合成測試申請者",
        "email": "synthetic@example.test",
        "age": 32,
        "gender": "其他",
        "stages": ["STAGE_1"],
        "months": ["2027-04"],
        "expectations": ["溝通方式"],
        "source": "MANUAL",
        "adult_single_confirmed": True,
        "privacy_confirmed": True,
        "safety_confirmed": True,
        "recording_consents": {},
    }
    values.update(changes)
    return api.ApplicationCreate.model_validate(values)


def test_submit_writes_record_and_crm_lists_it(monkeypatch):
    store = InMemoryDocumentStoreStub()
    monkeypatch.setattr(api, "get_settings", lambda: SimpleNamespace(admin_auth_mode="token", admin_api_token="synthetic-secret"))

    created = api.create_application(payload(), request_context(), store)
    record_id = created["data"]["id"]
    saved = store.get("applications", record_id)
    assert saved["display_name"] == "合成測試申請者"
    assert saved["status"] == "RECEIVED"

    api.require_admin("Bearer synthetic-secret")
    listed = api.list_applications(request_context(), 1, 20, None, None, None, store)
    assert listed["data"][0]["id"] == record_id
    assert listed["meta"]["pagination"]["total_items"] == 1


def test_submit_rejects_missing_consent_without_writing():
    store = InMemoryDocumentStoreStub()
    with pytest.raises(AppError) as error:
        api.create_application(payload(privacy_confirmed=False), request_context(), store)
    assert error.value.status_code == 422
    assert store.list("applications") == []


def test_admin_api_rejects_missing_or_invalid_token(monkeypatch):
    monkeypatch.setattr(api, "get_settings", lambda: SimpleNamespace(admin_auth_mode="token", admin_api_token="synthetic-secret"))
    with pytest.raises(AppError) as missing:
        api.require_admin(None)
    assert missing.value.status_code == 401
    with pytest.raises(AppError) as invalid:
        api.require_admin("Bearer wrong")
    assert invalid.value.status_code == 401


def test_admin_firebase_auth_requires_admin_custom_claim(monkeypatch):
    from app.core import firebase

    monkeypatch.setattr(api, "get_settings", lambda: SimpleNamespace(admin_auth_mode="firebase", admin_firebase_claim="admin"))
    monkeypatch.setattr(firebase, "verify_admin_id_token", lambda _token: {"uid": "operator", "admin": False})
    with pytest.raises(AppError) as denied:
        api.require_admin("Bearer synthetic-firebase-id-token")
    assert denied.value.status_code == 403

    monkeypatch.setattr(firebase, "verify_admin_id_token", lambda _token: {"uid": "operator", "admin": True})
    assert api.require_admin("Bearer synthetic-firebase-id-token") is None
