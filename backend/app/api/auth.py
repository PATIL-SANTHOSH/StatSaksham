from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.session import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.models.employee import Employee
from app.schemas.auth import LoginRequest, Token, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    employee_id = req.employee_id.strip().upper()
    user = db.query(User).filter(User.employee_id == employee_id).first()
    
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Employee ID or Password. (Try OSS1001 / demo123 or ADMIN001 / admin123)"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled")

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Get employee details
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    emp_name = emp.name if emp else "User"
    desig = emp.designation if emp else user.role
    dept = emp.department if emp else "MoSPI"

    token = create_access_token(subject=user.employee_id, role=user.role)
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        employee_id=user.employee_id,
        name=emp_name,
        designation=desig,
        department=dept
    )

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == current_user.employee_id).first()
    return {
        "user_id": current_user.id,
        "employee_id": current_user.employee_id,
        "role": current_user.role,
        "last_login": current_user.last_login,
        "employee": emp
    }
