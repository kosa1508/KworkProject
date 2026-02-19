from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.DEBUG)

from src.api.cases import router as router_cases
from src.api.auth import router as router_auth
from src.api.items import router as router_items
from src.api.payments import router as router_payments
from src.config import settings
from src.core.csrf import csrf_middleware, csrf_protection

app = FastAPI(
    title="Case Opening API",
    description="API для открытия кейсов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-CSRF-Token"  # Добавляем CSRF заголовок
    ],
    expose_headers=["X-CSRF-Token"],  # Клиент может читать этот заголовок
)

# Добавляем CSRF middleware (должен быть после CORS)
app.middleware("http")(csrf_middleware)

# Обработчик CSRF ошибок
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code == 403 and "CSRF" in str(exc.detail):
        return JSONResponse(
            status_code=403,
            content=exc.detail if isinstance(exc.detail, dict) else {
                "error": "CSRF Error",
                "message": str(exc.detail),
                "solution": "Please include X-CSRF-Token header with valid token"
            }
        )
    # Для других ошибок
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail} if not isinstance(exc.detail, dict) else exc.detail
    )

app.include_router(router_cases)
app.include_router(router_auth)
app.include_router(router_items)
app.include_router(router_payments)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)