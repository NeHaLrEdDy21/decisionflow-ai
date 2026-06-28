"""SQLite persistence for customers, runs, recommendations and memory."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from config import SQLITE_PATH


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT,
                health INTEGER,
                renewal_days INTEGER,
                arr REAL,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                state_json TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                run_id TEXT,
                customer_id TEXT,
                action TEXT,
                priority TEXT,
                confidence INTEGER,
                business_impact TEXT,
                reason TEXT,
                expected_outcome TEXT,
                evidence_json TEXT,
                status TEXT DEFAULT 'pending',
                modified_action TEXT,
                created_at TEXT,
                decided_at TEXT
            );
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                customer_name TEXT,
                kind TEXT,
                action TEXT,
                result TEXT,
                detail_json TEXT,
                created_at TEXT
            );
            """
        )


def upsert_customer(cust: dict[str, Any]) -> str:
    cid = cust.get("id") or cust.get("name", "unknown").lower().replace(" ", "-")
    with _conn() as c:
        c.execute(
            """INSERT INTO customers(id,name,health,renewal_days,arr,created_at)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 name=excluded.name, health=excluded.health,
                 renewal_days=excluded.renewal_days, arr=excluded.arr""",
            (cid, cust.get("name"), cust.get("health"), cust.get("renewal_days"),
             cust.get("arr"), now()),
        )
    return cid


def save_run(customer_id: str, state: dict[str, Any]) -> str:
    rid = str(uuid.uuid4())
    with _conn() as c:
        c.execute(
            "INSERT INTO runs(id,customer_id,state_json,created_at) VALUES(?,?,?,?)",
            (rid, customer_id, json.dumps(state, default=str), now()),
        )
    return rid


def save_recommendations(run_id: str, customer_id: str, recs: list[dict[str, Any]]) -> list[dict]:
    out = []
    with _conn() as c:
        for r in recs:
            rec_id = str(uuid.uuid4())
            c.execute(
                """INSERT INTO recommendations
                   (id,run_id,customer_id,action,priority,confidence,business_impact,
                    reason,expected_outcome,evidence_json,status,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?, 'pending', ?)""",
                (rec_id, run_id, customer_id, r.get("action"), r.get("priority"),
                 r.get("confidence"), r.get("business_impact"), r.get("reason"),
                 r.get("expected_outcome"), json.dumps(r.get("evidence", {})), now()),
            )
            r2 = dict(r)
            r2["id"] = rec_id
            r2["status"] = "pending"
            out.append(r2)
    return out


def get_recommendations(customer_id: str | None = None) -> list[dict]:
    q = "SELECT * FROM recommendations"
    args: tuple = ()
    if customer_id:
        q += " WHERE customer_id=?"
        args = (customer_id,)
    q += " ORDER BY created_at DESC"
    with _conn() as c:
        rows = c.execute(q, args).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["evidence"] = json.loads(d.pop("evidence_json") or "{}")
        result.append(d)
    return result


def decide_recommendation(rec_id: str, status: str, modified_action: str | None = None) -> dict | None:
    with _conn() as c:
        c.execute(
            "UPDATE recommendations SET status=?, modified_action=?, decided_at=? WHERE id=?",
            (status, modified_action, now(), rec_id),
        )
        row = c.execute("SELECT * FROM recommendations WHERE id=?", (rec_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["evidence"] = json.loads(d.pop("evidence_json") or "{}")
    return d


def add_memory(entry: dict[str, Any]) -> str:
    mid = str(uuid.uuid4())
    with _conn() as c:
        c.execute(
            """INSERT INTO memory(id,customer_id,customer_name,kind,action,result,detail_json,created_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (mid, entry.get("customer_id"), entry.get("customer_name"), entry.get("kind"),
             entry.get("action"), entry.get("result"), json.dumps(entry.get("detail", {})), now()),
        )
    return mid


def get_memory(customer_id: str | None = None) -> list[dict]:
    q = "SELECT * FROM memory"
    args: tuple = ()
    if customer_id:
        q += " WHERE customer_id=?"
        args = (customer_id,)
    q += " ORDER BY created_at DESC"
    with _conn() as c:
        rows = c.execute(q, args).fetchall()
    out = []
    for row in rows:
        d = dict(row)
        d["detail"] = json.loads(d.pop("detail_json") or "{}")
        out.append(d)
    return out


def get_customer(customer_id: str) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    return dict(row) if row else None
