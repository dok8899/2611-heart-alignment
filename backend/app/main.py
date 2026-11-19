import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.health import router as health_router
from app.api.v1.applications import router as applications_router
from app.api.v1.chat import router as chat_router
from app.core.config import get_settings
from app.core.error_codes import ErrorCode
from app.core.errors import AppError
from app.core.responses import error_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title="心靈契合 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Idempotency-Key"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    supplied_id = request.headers.get("X-Request-ID")
    request.state.request_id = supplied_id or str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(request, code=exc.code, message=exc.message, details=exc.details),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    fields = [
        {"path": list(error["loc"]), "code": error["type"], "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_response(
            request,
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed.",
            details={"fields": fields},
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    code = ErrorCode.NOT_FOUND if exc.status_code == 404 else ErrorCode.HTTP_ERROR
    message = "API route not found." if exc.status_code == 404 else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(request, code=code, message=message),
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled request error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=error_response(
            request,
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred.",
        ),
    )


app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(applications_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)
