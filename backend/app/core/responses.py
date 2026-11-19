from typing import Any

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.time import format_utc


class PaginationMeta(BaseModel):
    model_config = ConfigDict(frozen=True)

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


def build_pagination_meta(*, page: int, page_size: int, total_items: int) -> PaginationMeta:
    if page < 1 or page_size < 1 or total_items < 0:
        raise ValueError("Pagination values must be positive, with total_items non-negative.")
    total_pages = (total_items + page_size - 1) // page_size
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )


def success_response(
    request: Request,
    data: Any,
    *,
    pagination: PaginationMeta | dict[str, int] | None = None,
) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "request_id": getattr(request.state, "request_id", "unknown"),
        "timestamp": format_utc(),
    }
    if pagination is not None:
        meta["pagination"] = (
            pagination.model_dump() if isinstance(pagination, PaginationMeta) else pagination
        )
    return {"data": data, "meta": meta}


def error_response(
    request: Request,
    *,
    code: str,
    message: str,
    details: Any = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": getattr(request.state, "request_id", "unknown"),
    }
    if details is not None:
        error["details"] = details
    return {"error": error, "meta": {"timestamp": format_utc()}}
