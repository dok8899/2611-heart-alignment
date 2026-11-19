import os
from typing import Any

from app.core.adapters import InMemoryDocumentStoreStub
from app.core.config import get_settings
from app.core.ports import DocumentStore


class FirestoreDocumentStore(DocumentStore):
    """Google Cloud Firestore adapter; accepts a client for emulator-based tests."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        snapshot = self._client.collection(collection).document(document_id).get(timeout=5)
        return snapshot.to_dict() if snapshot.exists else None

    def set(
        self,
        collection: str,
        document_id: str,
        document: dict[str, Any],
        *,
        merge: bool = False,
    ) -> None:
        self._client.collection(collection).document(document_id).set(document, merge=merge)

    def delete(self, collection: str, document_id: str) -> None:
        self._client.collection(collection).document(document_id).delete()

    def list(self, collection: str, *, limit: int = 100) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        snapshots = self._client.collection(collection).limit(limit).stream(timeout=5)
        return [{"id": snapshot.id, **(snapshot.to_dict() or {})} for snapshot in snapshots]

    def ping(self) -> None:
        # Read-only metadata check; no health document is written.
        self._client.collection("_system_health").document("api").get(timeout=3)


def build_document_store(
    backend: str,
    *,
    project: str,
    database: str,
    emulator_host: str | None = None,
    firestore_client: Any | None = None,
) -> DocumentStore:
    if backend == "memory":
        return InMemoryDocumentStoreStub()
    if backend == "firestore":
        if firestore_client is None:
            if emulator_host:
                # The Google client reads this process environment variable directly;
                # mirror the validated Pydantic setting loaded from .env.
                os.environ["FIRESTORE_EMULATOR_HOST"] = emulator_host
            from firebase_admin import firestore
            from app.core.firebase import get_firebase_app

            firebase_app = get_firebase_app(project)
            firestore_client = firestore.client(app=firebase_app, database_id=database)
        return FirestoreDocumentStore(firestore_client)
    raise ValueError(f"Unsupported DATA_STORE_BACKEND: {backend}")


settings = get_settings()
document_store = build_document_store(
    settings.data_store_backend,
    project=settings.google_cloud_project,
    database=settings.firestore_database,
    emulator_host=settings.firestore_emulator_host,
)


def get_document_store() -> DocumentStore:
    return document_store
