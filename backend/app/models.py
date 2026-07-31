import logging
import sqlite3
from typing import Optional

from app.database import get_connection

logger = logging.getLogger(__name__)


def insert_company(name, kvk_number):
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO companies (name, kvk_number) VALUES (?, ?)",
                (name, kvk_number),
            )
        return True
    except sqlite3.IntegrityError:
        logger.info("Company %s (kvk %s) already exists, skipped", name, kvk_number)
        return False


def get_companies():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM companies ORDER BY name").fetchall()
    return [dict(row) for row in rows]


def get_company(company_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM companies WHERE id = ?", (company_id,)
        ).fetchone()
    return dict(row) if row else None


def get_companies_paginated(page: int, per_page: int):
    with get_connection() as conn:
        offset = (page - 1) * per_page
        rows = conn.execute(
            "SELECT * FROM companies ORDER BY name LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    return [dict(row) for row in rows], total


def search_companies(query: str):
    with get_connection() as conn:
        pattern = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM companies WHERE name LIKE ? ORDER BY name",
            (pattern,),
        ).fetchall()
    return [dict(row) for row in rows]


def search_companies_paginated(query: str, page: int, per_page: int):
    with get_connection() as conn:
        pattern = f"%{query}%"
        offset = (page - 1) * per_page
        rows = conn.execute(
            "SELECT * FROM companies WHERE name LIKE ? ORDER BY name LIMIT ? OFFSET ?",
            (pattern, per_page, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM companies WHERE name LIKE ?", (pattern,)
        ).fetchone()[0]
    return [dict(row) for row in rows], total


def company_count():
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    return count


def get_companies_without_website_paginated(page: int, per_page: int):
    with get_connection() as conn:
        offset = (page - 1) * per_page
        rows = conn.execute(
            "SELECT * FROM companies WHERE website_url IS NULL "
            "ORDER BY name LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM companies WHERE website_url IS NULL"
        ).fetchone()[0]
    return [dict(row) for row in rows], total


def get_companies_by_ids(ids: list[int]):
    with get_connection() as conn:
        placeholders = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT * FROM companies WHERE id IN ({placeholders}) ORDER BY name",
            ids,
        ).fetchall()
    return [dict(row) for row in rows]


def set_company_website_by_kvk(kvk_number: str, url: Optional[str]):
    with get_connection() as conn:
        conn.execute(
            "UPDATE companies SET website_url = ? WHERE kvk_number = ?",
            (url, kvk_number),
        )


def set_company_website(company_id: int, url: Optional[str]):
    with get_connection() as conn:
        conn.execute(
            "UPDATE companies SET website_url = ? WHERE id = ?", (url, company_id)
        )


def sync_sponsors(sponsors):
    with get_connection() as conn:
        existing_rows = conn.execute(
            "SELECT kvk_number, name, website_url FROM companies"
        ).fetchall()
        existing = {row["kvk_number"]: row for row in existing_rows}
        incoming = {s["kvk_number"]: s["name"] for s in sponsors}

        to_insert = []
        to_update_name = []
        to_remove = []

        for kvk, name in incoming.items():
            if kvk not in existing:
                to_insert.append((name, kvk))
            elif existing[kvk]["name"] != name:
                to_update_name.append((name, kvk))

        for kvk in existing:
            if kvk not in incoming:
                to_remove.append(kvk)

        if to_insert:
            conn.executemany(
                "INSERT INTO companies (name, kvk_number) VALUES (?, ?)", to_insert
            )

        for name, kvk in to_update_name:
            conn.execute(
                "UPDATE companies SET name = ? WHERE kvk_number = ?", (name, kvk)
            )

        for kvk in to_remove:
            conn.execute("DELETE FROM companies WHERE kvk_number = ?", (kvk,))

    logger.info(
        "Sync complete: %d inserted, %d updated, %d removed",
        len(to_insert),
        len(to_update_name),
        len(to_remove),
    )

    return {
        "inserted": len(to_insert),
        "updated": len(to_update_name),
        "removed": len(to_remove),
    }
