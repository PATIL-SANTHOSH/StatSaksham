from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.admin import WorkforceAnalyticsResponse
from app.services.admin_service import AdminService
from app.api.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Admin & Workforce Intelligence"])

@router.get("/analytics", response_model=WorkforceAnalyticsResponse)
def get_workforce_analytics(
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    service = AdminService(db)
    return service.get_workforce_analytics()
