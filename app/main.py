import os
import time
import uuid
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from app.logging_config import setup_logging
from app.rate_limit import check_rate_limit
from app.ai_service import generate_reply

load_dotenv()
setup_logging()
logger = logging.getLogger("burak")

app = FastAPI(
    title=os.getenv("APP_NAME", "Burak AI Backend"),
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

class ChatRequest(BaseModel):
    message: str


@app.middleware("http")
async def request_id_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()

    logger.info(f"[{request_id}] -> {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"[{request_id}] !! ERROR: {e}")
        raise

    duration_ms = int((time.time() - start) * 1000)
    logger.info(f"[{request_id}] <- {response.status_code} ({duration_ms}ms)")
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=429,
        content={"error": "runtime", "message": str(exc)},
    )


@app.exception_handler(Exception)
async def any_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": str(exc)},
    )


# Root endpoint
@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "health": "/health"
    }


# Health check
@app.get("/health")
def health():
    return {"status": "ok"}


# Redirect /docs -> /docs/
@app.get("/docs", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs/")


# Main chat endpoint
@app.post("/chat")
def chat(
    request: Request,
    data: ChatRequest,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)
    return generate_reply(data.message, api_key=x_api_key)
