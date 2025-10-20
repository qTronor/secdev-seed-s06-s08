# app/main.py
from pathlib import Path
import logging
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
from starlette.responses import PlainTextResponse

import os, logging

from .models import LoginRequest
from .db import query, query_one

EVIDENCE_DIR = Path(os.getenv("EVIDENCE_DIR", Path(__file__).resolve().parents[1] / "EVIDENCE" / "S06"))
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(EVIDENCE_DIR / "app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("app")

app = FastAPI(title="secdev-seed-s06-s08")
templates = Jinja2Templates(directory="app/templates")

# (опционально) CORS, если нужно в тестах
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Глобальные обработчики ошибок ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error: %s", exc)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid input", "errors": exc.errors()},
    )

@app.exception_handler(sqlite3.Error)
async def sqlite_exception_handler(request: Request, exc: sqlite3.Error):
    logger.exception("Database error")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error"},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# --- Эндпоинты ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request, msg: str | None = None):
    return templates.TemplateResponse("index.html", {"request": request, "message": msg or "Hello!"})

@app.get("/echo", response_class=HTMLResponse)
def echo(request: Request, msg: str | None = None):
    # Никаких unsafe-фильтров — Jinja2 заэкранирует вывод
    return templates.TemplateResponse("index.html", {"request": request, "message": msg or ""})

@app.get("/search")
def search(
    q: str | None = Query(default=None, min_length=1, max_length=100)
):
    # Параметризованный LIKE + мягкая нормализация
    if q:
        q_norm = q.strip()
        sql = "SELECT id, name, description FROM items WHERE name LIKE ? ESCAPE '\\' LIMIT 50"
        params = [f"%{q_norm}%"]
    else:
        sql = "SELECT id, name, description FROM items LIMIT 10"
        params = []
    items = query(sql, params)
    return JSONResponse(content={"items": items})

@app.post("/login")
def login(payload: LoginRequest):
    # ПАРАМЕТРИЗОВАННЫЙ запрос (никаких f-строк!)
    sql = "SELECT id, username FROM users WHERE username = ? AND password = ?"
    row = query_one(sql, (payload.username, payload.password))
    if not row:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"status": "ok", "user": row["username"], "token": "dummy"}
