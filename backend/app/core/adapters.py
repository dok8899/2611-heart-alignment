from copy import deepcopy
from io import BytesIO
from threading import RLock
from typing import Any, BinaryIO

from app.core.ports import AuthClaims, Authenticator, DocumentStore, IdentityResolver, UserIdentity


class StubAuthenticator(Authenticator):
    """Development-only authenticator. Replace with LINE Login adapter later."""

    def authenticate(self, credential: str) -> AuthClaims:
        if credential != "dev-stub":
            raise ValueError("Stub credentials must be 'dev-stub'.")
        return AuthClaims(subject="synthetic-user-001", issuer="development-stub")


class StubIdentityResolver(IdentityResolver):
    def resolve(self, claims: AuthClaims) -> UserIdentity:
        return UserIdentity(
            subject=claims.subject,
            provider=claims.issuer,
            email=claims.email,
        )


class InMemoryDocumentStoreStub(DocumentStore):
    """Local Firestore-shaped stub. Data is synthetic and resets on process restart."""

    def __init__(self) -> None:
        self._collections: dict[str, dict[str, dict[str, Any]]] = {}
        self._lock = RLock()

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        with self._lock:
            value = self._collections.get(collection, {}).get(document_id)
            return deepcopy(value) if value is not None else None

    def set(
        self,
        collection: str,
        document_id: str,
        document: dict[str, Any],
        *,
        merge: bool = False,
    ) -> None:
        with self._lock:
            bucket = self._collections.setdefault(collection, {})
            if merge and document_id in bucket:
                bucket[document_id].update(deepcopy(document))
            else:
                bucket[document_id] = deepcopy(document)

    def delete(self, collection: str, document_id: str) -> None:
        with self._lock:
            self._collections.get(collection, {}).pop(document_id, None)

    def list(self, collection: str, *, limit: int = 100) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        with self._lock:
            bucket = self._collections.get(collection, {})
            return [
                {"id": document_id, **deepcopy(document)}
                for document_id, document in list(bucket.items())[:limit]
            ]

    def ping(self) -> None:
        return None


class InMemoryFileStorageStub:
    """Non-persistent local adapter for interface-level development only."""

    def __init__(self) -> None:
        self._objects: dict[str, tuple[bytes, str]] = {}

    def put(self, key: str, content: BinaryIO, content_type: str) -> str:
        self._objects[key] = (content.read(), content_type)
        return key

    def delete(self, key: str) -> None:
        self._objects.pop(key, None)

    def create_read_url(self, key: str, *, expires_in_seconds: int) -> str:
        if key not in self._objects:
            raise FileNotFoundError(key)
        return f"memory://{key}?expires_in={expires_in_seconds}"

    def open(self, key: str) -> tuple[BytesIO, str]:
        payload, content_type = self._objects[key]
        return BytesIO(payload), content_type
