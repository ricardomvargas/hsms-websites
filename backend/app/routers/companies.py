from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.models import (
    get_companies_by_ids,
    get_companies_paginated,
    get_companies_without_website,
    get_company,
    search_companies_paginated,
    set_company_website,
    set_company_website_by_kvk,
)
from app.services.website_lookup import find_websites

router = APIRouter()


class WebsiteUpdate(BaseModel):
    website_url: Optional[str] = None


class FetchWebsitesBody(BaseModel):
    company_ids: list[int]


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/companies")
def list_companies(
    page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100)
):
    items, total = get_companies_paginated(page, per_page)
    return {"items": items, "total": total, "page": page, "per_page": per_page}


@router.get("/companies/search")
def list_companies_search(
    q: str = Query("", min_length=0),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    if not q.strip():
        return {"items": [], "total": 0, "page": page, "per_page": per_page}
    items, total = search_companies_paginated(q.strip(), page, per_page)
    return {"items": items, "total": total, "page": page, "per_page": per_page}


@router.get("/companies/without-website")
def list_companies_without_website():
    return get_companies_without_website()


@router.get("/companies/{company_id}")
def get_company_by_id(company_id: int):
    company = get_company(company_id)
    if not company:
        return {"error": "Company not found"}, 404
    return company


@router.put("/companies/{company_id}/website")
def update_website(company_id: int, body: WebsiteUpdate):
    company = get_company(company_id)
    if not company:
        return {"error": "Company not found"}, 404
    set_company_website(company_id, body.website_url)
    return get_company(company_id)


@router.post("/companies/fetch-websites")
def fetch_company_websites(body: FetchWebsitesBody):
    companies = get_companies_by_ids(body.company_ids[:20])
    kvk_list = [
        {"kvk_number": c["kvk_number"], "name": c["name"]}
        for c in companies
        if c["kvk_number"]
    ]
    results = find_websites(kvk_list)

    updated = 0
    for kvk, website in results.items():
        set_company_website_by_kvk(kvk, website)
        updated += 1

    return {"total": len(kvk_list), "updated": updated, "results": results}
