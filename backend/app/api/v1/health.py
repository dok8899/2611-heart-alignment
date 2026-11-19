from fastapi import APIRouter, Depends, Request

from app.core.error_codes import ErrorCode
from app.core.errors import AppError
from app.core.ports import DocumentStore
from app.core.responses import success_response
from app.db.store import get_document_store

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(request: Request, store: DocumentStore = Depends(get_document_store)):
    try:
        store.ping()
    except Exception as exc:
        raise AppError(
            code=ErrorCode.DATABASE_UNAVAILABLE,
            message="Document store is unavailable.",
            status_code=503,
        ) from exc
    return success_response(request, {"status": "ok", "database": "ok"})
