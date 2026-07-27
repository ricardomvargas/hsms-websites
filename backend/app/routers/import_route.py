from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models import company_count, sync_sponsors
from app.services.ind_scraper import fetch_sponsors

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/import")
@limiter.limit("3/hour")
def import_sponsors(request: Request):
    sponsors = fetch_sponsors()
    result = sync_sponsors(sponsors)
    return {
        "total_found": len(sponsors),
        "total_in_db": company_count(),
        **result,
    }
