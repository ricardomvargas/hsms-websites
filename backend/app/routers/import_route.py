from fastapi import APIRouter

from app.models import company_count, sync_sponsors
from app.services.ind_scraper import fetch_sponsors

router = APIRouter()


@router.post("/import")
def import_sponsors():
    sponsors = fetch_sponsors()
    result = sync_sponsors(sponsors)
    return {
        "total_found": len(sponsors),
        "total_in_db": company_count(),
        **result,
    }
