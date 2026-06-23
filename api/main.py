import os
import sqlite3
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app_root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(title="Pathfinder", root_path=app_root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_connection():
    db_path = os.getenv("DB_PATH", "pathfinder.db")
    return sqlite3.connect(db_path)


def migrate_schema(conn):
    cursor = conn.cursor()
    existing = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='routing_rules'"
    ).fetchone()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS routing_rules_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_name TEXT,
            match_type TEXT,
            pattern TEXT,
            min_duration_sec INTEGER DEFAULT NULL,
            max_duration_sec INTEGER DEFAULT NULL,
            destination_1 TEXT,
            destination_2 TEXT DEFAULT NULL,
            promo_possible INTEGER DEFAULT 0
        )
        """
    )

    if existing:
        columns = {
            row["name"]
            for row in cursor.execute("PRAGMA table_info(routing_rules)").fetchall()
        }
        cursor.execute(
            """
            INSERT INTO routing_rules_new (
                id,
                program_name,
                match_type,
                pattern,
                min_duration_sec,
                max_duration_sec,
                destination_1,
                destination_2,
                promo_possible
            )
            SELECT
                id,
                NULL,
                match_type,
                pattern,
                min_duration_sec,
                max_duration_sec,
                destination_1,
                destination_2,
                0
            FROM routing_rules
            """
        )
        if "program_name" in columns or "promo_possible" in columns:
            cursor.execute("DELETE FROM routing_rules_new")
            cursor.execute(
                """
                INSERT INTO routing_rules_new (
                    id,
                    program_name,
                    match_type,
                    pattern,
                    min_duration_sec,
                    max_duration_sec,
                    destination_1,
                    destination_2,
                    promo_possible
                )
                SELECT
                    id,
                    program_name,
                    match_type,
                    pattern,
                    min_duration_sec,
                    max_duration_sec,
                    destination_1,
                    destination_2,
                    COALESCE(promo_possible, 0)
                FROM routing_rules
                """
            )

        cursor.execute("DROP TABLE routing_rules")

    cursor.execute("ALTER TABLE routing_rules_new RENAME TO routing_rules")


def initialize_database():
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    migrate_schema(conn)
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def health_check():
    return {"app": "Pathfinder", "status": "ok"}


class RouteLookup(BaseModel):
    title: str
    alt_id: str
    filename: str
    duration_sec: Optional[int] = None


class RulePayload(BaseModel):
    program_name: str
    match_type: Optional[str] = None
    pattern: Optional[str] = None
    min_duration_sec: Optional[int] = None
    max_duration_sec: Optional[int] = None
    destination_1: Optional[str] = None
    destination_2: Optional[str] = None
    promo_possible: int = 0


def normalize_nullable(value):
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def serialize_rule(rule):
    return {
        "id": rule["id"],
        "program_name": rule["program_name"],
        "match_type": rule["match_type"],
        "pattern": rule["pattern"],
        "min_duration_sec": rule["min_duration_sec"],
        "max_duration_sec": rule["max_duration_sec"],
        "destination_1": rule["destination_1"],
        "destination_2": rule["destination_2"],
        "promo_possible": rule["promo_possible"],
    }


@app.get("/rules")
def list_rules(
    program_name: Optional[str] = None,
    match_type: Optional[str] = None,
    q: Optional[str] = None,
):
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    where_parts = []
    params = []

    search_name = program_name if program_name else q

    if search_name:
        where_parts.append("program_name LIKE ?")
        params.append(f"%{search_name}%")
    if match_type:
        where_parts.append("match_type = ?")
        params.append(match_type)

    where_sql = ""
    if where_parts:
        where_sql = " WHERE " + " AND ".join(where_parts)

    query = (
        "SELECT * FROM routing_rules"
        + where_sql
        + " ORDER BY program_name ASC NULLS LAST, id ASC"
    )

    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return [serialize_rule(row) for row in rows]


@app.get("/rules/{rule_id}")
def get_rule(rule_id: int):
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM routing_rules WHERE id = ?", (rule_id,)).fetchone()
    conn.close()
    return serialize_rule(row) if row else {"message": "not found"}


@app.post("/rules", status_code=201)
def create_rule(payload: RulePayload):
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.execute(
        """
        INSERT INTO routing_rules (
            program_name,
            match_type,
            pattern,
            min_duration_sec,
            max_duration_sec,
            destination_1,
            destination_2,
            promo_possible
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING *
        """,
        (
            normalize_nullable(payload.program_name),
            normalize_nullable(payload.match_type),
            normalize_nullable(payload.pattern),
            payload.min_duration_sec,
            payload.max_duration_sec,
            normalize_nullable(payload.destination_1),
            normalize_nullable(payload.destination_2),
            1 if payload.promo_possible else 0,
        ),
    ).fetchone()
    conn.commit()
    conn.close()
    return serialize_rule(row)


@app.put("/rules/{rule_id}")
def update_rule(rule_id: int, payload: RulePayload):
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.execute(
        """
        UPDATE routing_rules
        SET
            program_name = ?,
            match_type = ?,
            pattern = ?,
            min_duration_sec = ?,
            max_duration_sec = ?,
            destination_1 = ?,
            destination_2 = ?,
            promo_possible = ?
        WHERE id = ?
        RETURNING *
        """,
        (
            normalize_nullable(payload.program_name),
            normalize_nullable(payload.match_type),
            normalize_nullable(payload.pattern),
            payload.min_duration_sec,
            payload.max_duration_sec,
            normalize_nullable(payload.destination_1),
            normalize_nullable(payload.destination_2),
            1 if payload.promo_possible else 0,
            rule_id,
        ),
    ).fetchone()
    conn.commit()
    conn.close()
    return serialize_rule(row) if row else {"message": "not found"}


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routing_rules WHERE id = ?", (rule_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return {"deleted": deleted}


@app.post("/route")
def route_item(entry: RouteLookup):
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    rule = cursor.execute(
        """
        SELECT *
        FROM routing_rules
        WHERE (
            (match_type = 'title' AND pattern IS NOT NULL AND ? LIKE pattern) OR
            (match_type = 'alt_id' AND pattern IS NOT NULL AND ? LIKE pattern) OR
            (match_type = 'filename' AND pattern IS NOT NULL AND ? LIKE pattern)
        )
        AND (? IS NULL OR min_duration_sec IS NULL OR ? >= min_duration_sec)
        AND (? IS NULL OR max_duration_sec IS NULL OR ? <= max_duration_sec)
        ORDER BY id ASC
        LIMIT 1
        """,
        (
            entry.title,
            entry.alt_id,
            entry.filename,
            entry.duration_sec,
            entry.duration_sec,
            entry.duration_sec,
            entry.duration_sec,
        ),
    ).fetchone()
    conn.close()

    if rule is None:
        return {"matched": False, "rule": None}

    return {"matched": True, "rule": serialize_rule(rule)}
