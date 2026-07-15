import sqlite3
from typing import Optional

from app.database import get_connection


def insert_company(name, kvk_number):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO companies (name, kvk_number) VALUES (?, ?)",
            (name, kvk_number),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_companies():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM companies ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_company(company_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM companies WHERE id = ?", (company_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_companies_paginated(page: int, per_page: int):
    conn = get_connection()
    offset = (page - 1) * per_page
    rows = conn.execute(
        "SELECT * FROM companies ORDER BY name LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    conn.close()
    return [dict(row) for row in rows], total


def search_companies(query: str):
    conn = get_connection()
    pattern = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM companies WHERE name LIKE ? ORDER BY name",
        (pattern,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_companies_paginated(query: str, page: int, per_page: int):
    conn = get_connection()
    pattern = f"%{query}%"
    offset = (page - 1) * per_page
    rows = conn.execute(
        "SELECT * FROM companies WHERE name LIKE ? ORDER BY name LIMIT ? OFFSET ?",
        (pattern, per_page, offset),
    ).fetchall()
    total = conn.execute(
        "SELECT COUNT(*) FROM companies WHERE name LIKE ?", (pattern,)
    ).fetchone()[0]
    conn.close()
    return [dict(row) for row in rows], total


def company_count():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    conn.close()
    return count


def get_companies_without_website():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM companies WHERE website_url IS NULL ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_companies_by_ids(ids: list[int]):
    conn = get_connection()
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"SELECT * FROM companies WHERE id IN ({placeholders}) ORDER BY name",
        ids,
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def set_company_website_by_kvk(kvk_number: str, url: Optional[str]):
    conn = get_connection()
    conn.execute(
        "UPDATE companies SET website_url = ? WHERE kvk_number = ?",
        (url, kvk_number),
    )
    conn.commit()
    conn.close()


def set_company_website(company_id: int, url: Optional[str]):
    conn = get_connection()
    conn.execute(
        "UPDATE companies SET website_url = ? WHERE id = ?", (url, company_id)
    )
    conn.commit()
    conn.close()


def sync_sponsors(sponsors):
    conn = get_connection()

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

    conn.commit()
    conn.close()

    return {
        "inserted": len(to_insert),
        "updated": len(to_update_name),
        "removed": len(to_remove),
    }
