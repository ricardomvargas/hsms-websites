import logging

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.models import company_count, sync_sponsors
from app.services.ind_scraper import fetch_sponsors

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/import")
@limiter.limit(settings.import_rate_limit)
def import_sponsors(request: Request):
    sponsors = fetch_sponsors()
    result = sync_sponsors(sponsors)
    logger.info(
        "Import finished: %d sponsors fetched, %d in db, %s",
        len(sponsors),
        company_count(),
        result,
    )
    return {
        "total_found": len(sponsors),
        "total_in_db": company_count(),
        **result,
    }
