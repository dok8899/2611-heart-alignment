from dataclasses import dataclass
from typing import Any, BinaryIO, Protocol


@dataclass(frozen=True)
class AuthClaims:
    subject: str
    issuer: str
    email: str | None = None


@dataclass(frozen=True)
class UserIdentity:
    subject: str
    provider: str
    email: str | None = None


class Authenticator(Protocol):
    def authenticate(self, credential: str) -> AuthClaims: ...


class IdentityResolver(Protocol):
    def resolve(self, claims: AuthClaims) -> UserIdentity: ...


class DocumentStore(Protocol):
    """Portable collection/document storage contract for local and cloud adapters."""

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None: ...

    def set(
        self,
        collection: str,
        document_id: str,
        document: dict[str, Any],
        *,
        merge: bool = False,
    ) -> None: ...

    def delete(self, collection: str, document_id: str) -> None: ...

    def list(self, collection: str, *, limit: int = 100) -> list[dict[str, Any]]: ...

    def ping(self) -> None: ...


class FileStorage(Protocol):
    def put(self, key: str, content: BinaryIO, content_type: str) -> str: ...

    def delete(self, key: str) -> None: ...

    def create_read_url(self, key: str, *, expires_in_seconds: int) -> str: ...
