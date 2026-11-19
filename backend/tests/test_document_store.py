from app.core.adapters import InMemoryDocumentStoreStub, InMemoryFileStorageStub, StubAuthenticator, StubIdentityResolver
from app.core.config import REPOSITORY_ROOT, Settings
from app.core.ports import AuthClaims
from app.db.store import FirestoreDocumentStore, build_document_store
from app.seed import seed_synthetic_data


class FakeSnapshot:
    def __init__(self, document_id: str, data: dict | None):
        self.id = document_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class FakeDocumentReference:
    def __init__(self, client, collection: str, document_id: str):
        self.client = client
        self.collection_name = collection
        self.document_id = document_id

    def get(self, **_kwargs):
        value = self.client.data.get(self.collection_name, {}).get(self.document_id)
        return FakeSnapshot(self.document_id, value)

    def set(self, document: dict, merge: bool = False):
        bucket = self.client.data.setdefault(self.collection_name, {})
        if merge and self.document_id in bucket:
            bucket[self.document_id].update(document)
        else:
            bucket[self.document_id] = dict(document)

    def delete(self):
        self.client.data.get(self.collection_name, {}).pop(self.document_id, None)


class FakeCollectionReference:
    def __init__(self, client, name: str):
        self.client = client
        self.name = name
        self._limit = 100

    def document(self, document_id: str):
        return FakeDocumentReference(self.client, self.name, document_id)

    def limit(self, value: int):
        self._limit = value
        return self

    def stream(self, **_kwargs):
        data = self.client.data.get(self.name, {})
        return [FakeSnapshot(key, value) for key, value in list(data.items())[: self._limit]]


class FakeFirestoreClient:
    def __init__(self):
        self.data: dict[str, dict[str, dict]] = {}

    def collection(self, name: str):
        return FakeCollectionReference(self, name)


def test_env_example_defaults_to_local_stub_without_credentials():
    settings = Settings(_env_file=REPOSITORY_ROOT / ".env.example")

    assert settings.data_store_backend == "memory"
    assert settings.google_cloud_project == "heart-alignment-local"
    assert settings.firestore_database == "(default)"
    assert settings.firestore_emulator_host is None
    assert settings.api_prefix == "/api/v1"
    assert settings.cors_origins == ["http://localhost:5173"]


def test_memory_document_store_round_trip_and_merge():
    store = InMemoryDocumentStoreStub()
    store.set("synthetic", "one", {"name": "Sample", "active": True})
    store.set("synthetic", "one", {"active": False, "note": "fake"}, merge=True)

    assert store.get("synthetic", "one") == {"name": "Sample", "active": False, "note": "fake"}
    assert store.list("synthetic") == [{"id": "one", "name": "Sample", "active": False, "note": "fake"}]
    store.ping()
    store.delete("synthetic", "one")
    assert store.get("synthetic", "one") is None


def test_firestore_adapter_crud_and_ping_using_fake_client():
    client = FakeFirestoreClient()
    store = build_document_store(
        "firestore",
        project="synthetic-project",
        database="(default)",
        firestore_client=client,
    )
    assert isinstance(store, FirestoreDocumentStore)
    store.set("sample_collection", "sample-id", {"label": "synthetic"})

    assert store.get("sample_collection", "sample-id") == {"label": "synthetic"}
    assert store.list("sample_collection") == [{"id": "sample-id", "label": "synthetic"}]
    store.ping()
    store.delete("sample_collection", "sample-id")
    assert store.get("sample_collection", "sample-id") is None


def test_store_factory_selects_stub_and_rejects_unknown_backend():
    store = build_document_store("memory", project="local", database="(default)")
    assert isinstance(store, InMemoryDocumentStoreStub)

    try:
        build_document_store("unknown", project="local", database="(default)")
    except ValueError as exc:
        assert "Unsupported DATA_STORE_BACKEND" in str(exc)
    else:
        raise AssertionError("Unknown store backend must be rejected.")


def test_firestore_factory_uses_firebase_admin_client_and_emulator(monkeypatch):
    import os
    import sys
    from types import ModuleType

    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    calls = {}
    fake_app = object()

    firebase_admin = ModuleType("firebase_admin")
    firebase_admin.get_app = lambda _name: (_ for _ in ()).throw(ValueError("not initialized"))
    firebase_admin.initialize_app = lambda **kwargs: calls.setdefault("app", kwargs) or fake_app
    firestore = ModuleType("firebase_admin.firestore")

    def fake_client(**kwargs):
        calls.update(kwargs)
        return FakeFirestoreClient()

    firestore.client = fake_client
    firebase_admin.firestore = firestore
    monkeypatch.setitem(sys.modules, "firebase_admin", firebase_admin)
    monkeypatch.setitem(sys.modules, "firebase_admin.firestore", firestore)
    store = build_document_store(
        "firestore",
        project="synthetic-project",
        database="(default)",
        emulator_host="127.0.0.1:8080",
    )

    assert isinstance(store, FirestoreDocumentStore)
    assert calls["app"] == {"options": {"projectId": "synthetic-project"}, "name": "heart-alignment-api"}
    assert calls["app"] is not None
    assert calls["database_id"] == "(default)"
    assert os.environ["FIRESTORE_EMULATOR_HOST"] == "127.0.0.1:8080"


def test_firestore_admin_sdk_client_constructs_with_emulator_configuration(monkeypatch):
    import sys
    from types import ModuleType

    fake_app = object()
    fake_store = FakeFirestoreClient()
    firebase_admin = ModuleType("firebase_admin")
    firebase_admin.get_app = lambda _name: fake_app
    firestore = ModuleType("firebase_admin.firestore")
    firestore.client = lambda **_kwargs: fake_store
    firebase_admin.firestore = firestore
    monkeypatch.setitem(sys.modules, "firebase_admin", firebase_admin)
    monkeypatch.setitem(sys.modules, "firebase_admin.firestore", firestore)
    store = build_document_store(
        "firestore",
        project="synthetic-project",
        database="(default)",
        emulator_host="127.0.0.1:8080",
    )

    assert isinstance(store, FirestoreDocumentStore)


def test_synthetic_seed_is_idempotent():
    store = InMemoryDocumentStoreStub()
    seed_synthetic_data(store)
    seed_synthetic_data(store)

    records = store.list("phase1_demo_records")
    assert len(records) == 1
    assert records[0]["label"] == "Phase 1 synthetic sample"
    assert "no personal information" in records[0]["note"]


def test_stub_authentication_and_identity_resolution():
    claims = StubAuthenticator().authenticate("dev-stub")
    identity = StubIdentityResolver().resolve(claims)
    assert identity.subject == "synthetic-user-001"
    assert identity.provider == "development-stub"
    assert AuthClaims(subject="test", issuer="test").email is None


def test_in_memory_file_storage_stub_round_trip():
    from io import BytesIO

    storage = InMemoryFileStorageStub()
    storage.put("synthetic/file", BytesIO(b"synthetic"), "text/plain")
    body, content_type = storage.open("synthetic/file")
    assert body.read() == b"synthetic"
    assert content_type == "text/plain"
    assert storage.create_read_url("synthetic/file", expires_in_seconds=60).startswith("memory://")
    storage.delete("synthetic/file")
