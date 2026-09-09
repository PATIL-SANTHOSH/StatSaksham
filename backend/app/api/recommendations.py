from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.recommendation import RecommendationListResponse
from app.services.recommendation_service import RecommendationService
from app.api.deps import get_current_user

router = APIRouter(tags=["Recommendations"])

@router.get("/employees/{employee_id}/recommendations", response_model=RecommendationListResponse)
def get_recommendations(
    employee_id: str,
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = RecommendationService(db)
    try:
        return service.generate_recommendations(employee_id.upper(), force_refresh=refresh)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/employees/{employee_id}/recommendations/refresh", response_model=RecommendationListResponse)
def refresh_recommendations(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = RecommendationService(db)
    try:
        return service.generate_recommendations(employee_id.upper(), force_refresh=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
