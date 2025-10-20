# app/db.py
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DB_PATH = Path(os.getenv("DB_PATH", "/app/app.db"))

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _is_no_table_error(e: sqlite3.Error) -> bool:
    return isinstance(e, sqlite3.OperationalError) and "no such table" in str(e).lower()

def query(sql: str, params: Iterable[Any] = ()) -> List[Dict[str, Any]]:
    try:
        with get_conn() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error as e:
        if _is_no_table_error(e):
            return []
        raise

def query_one(sql: str, params: Iterable[Any] = ()) -> Optional[Dict[str, Any]]:
    try:
        with get_conn() as conn:
            row = conn.execute(sql, tuple(params)).fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        if _is_no_table_error(e):
            return None
        raise
