from datetime import datetime
from hmac import compare_digest
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import get_settings
from app.core.error_codes import ErrorCode
from app.core.errors import AppError
from app.core.ports import DocumentStore
from app.core.responses import build_pagination_meta, success_response
from app.core.time import format_utc
from app.db.store import get_document_store

router = APIRouter(tags=["applications"])


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    kind: Literal["FORMAL", "INTENT", "COMMUNITY", "CASTING"] = "FORMAL"
    display_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    age: int = Field(ge=18, le=100)
    gender: Literal["女性", "男性", "其他"]
    stages: list[str] = Field(min_length=1, max_length=4)
    months: list[str] = Field(min_length=1, max_length=12)
    occupation: str | None = Field(default=None, max_length=120)
    education: str | None = Field(default=None, max_length=2000)
    motivation: str | None = Field(default=None, max_length=3000)
    introduction: str | None = Field(default=None, max_length=3000)
    expectations: list[str] = Field(default_factory=list, max_length=30)
    source: Literal["AI", "MANUAL"] = "MANUAL"
    adult_single_confirmed: bool
    privacy_confirmed: bool
    safety_confirmed: bool
    recording_consents: dict[str, bool] = Field(default_factory=dict)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value.count("@") != 1 or "." not in value.rsplit("@", 1)[-1]:
            raise ValueError("請輸入有效 Email")
        return value

    @field_validator("months")
    @classmethod
    def validate_months(cls, values: list[str]) -> list[str]:
        if len(set(values)) != len(values):
            raise ValueError("月份不可重複")
        for value in values:
            datetime.strptime(value, "%Y-%m")
        return values

    @field_validator("stages")
    @classmethod
    def validate_stages(cls, values: list[str]) -> list[str]:
        allowed = {"STAGE_1", "STAGE_2", "STAGE_3"}
        if not values or any(value not in allowed for value in values) or len(set(values)) != len(values):
            raise ValueError("活動階段無效或重複")
        return values


@router.post("/applications", status_code=201)
def create_application(
    payload: ApplicationCreate,
    request: Request,
    store: DocumentStore = Depends(get_document_store),
):
    if not (payload.adult_single_confirmed and payload.privacy_confirmed and payload.safety_confirmed):
        raise AppError(
            code=ErrorCode.VALIDATION_ERROR,
            message="請先完成成年單身聲明、個資告知與安全公約同意。",
            status_code=422,
        )

    application_id = str(uuid4())
    submitted_at = format_utc()
    record = payload.model_dump(mode="json")
    record.update(
        {
            "status": "RECEIVED",
            "submitted_at": submitted_at,
            "updated_at": submitted_at,
            "retention_basis": "activity_end_plus_3_years",
        }
    )
    try:
        store.set("applications", application_id, record)
    except Exception as exc:
        raise AppError(
            code=ErrorCode.DATABASE_UNAVAILABLE,
            message="申請暫時無法保存，請稍後重試。",
            status_code=503,
        ) from exc
    return success_response(request, {"id": application_id, "status": record["status"], "submitted_at": submitted_at})


def require_admin(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if settings.admin_auth_mode == "firebase":
        if not supplied:
            raise AppError(code=ErrorCode.UNAUTHORIZED, message="需要 Firebase 管理員登入。", status_code=401)
        try:
            from app.core.firebase import verify_admin_id_token

            claims = verify_admin_id_token(supplied)
        except Exception as exc:
            raise AppError(code=ErrorCode.UNAUTHORIZED, message="Firebase ID token 無效或已過期。", status_code=401) from exc
        if not claims.get(settings.admin_firebase_claim):
            raise AppError(code=ErrorCode.FORBIDDEN, message="此 Firebase 帳號沒有 CRM 管理權限。", status_code=403)
        return

    expected = settings.admin_api_token
    if not expected:
        raise AppError(
            code=ErrorCode.ADMIN_ACCESS_NOT_CONFIGURED,
            message="後台尚未設定 ADMIN_API_TOKEN。",
            status_code=503,
        )
    if not compare_digest(supplied, expected):
        raise AppError(code=ErrorCode.UNAUTHORIZED, message="後台驗證失敗。", status_code=401)


@router.get("/admin/applications", dependencies=[Depends(require_admin)])
def list_applications(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    kind: str | None = Query(default=None),
    status: str | None = Query(default=None),
    query: str | None = Query(default=None, max_length=100),
    store: DocumentStore = Depends(get_document_store),
):
    try:
        records = store.list("applications", limit=1000)
    except Exception as exc:
        raise AppError(
            code=ErrorCode.DATABASE_UNAVAILABLE,
            message="目前無法讀取申請資料。",
            status_code=503,
        ) from exc
    records.sort(key=lambda item: item.get("submitted_at", ""), reverse=True)
    if kind:
        records = [record for record in records if record.get("kind") == kind]
    if status:
        records = [record for record in records if record.get("status") == status]
    if query:
        needle = query.casefold()
        records = [
            record for record in records
            if needle in str(record.get("display_name", "")).casefold()
            or needle in str(record.get("email", "")).casefold()
            or needle in str(record.get("phone", "")).casefold()
        ]
    total = len(records)
    start = (page - 1) * page_size
    return success_response(
        request,
        records[start : start + page_size],
        pagination=build_pagination_meta(page=page, page_size=page_size, total_items=total),
    )
