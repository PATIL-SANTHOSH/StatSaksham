from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.session import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeResponse, EmployeeListResponse, EmployeeUpdate
from app.api.deps import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("", response_model=EmployeeListResponse)
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    job_role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Employee)

    if department and department.lower() != "all":
        query = query.filter(Employee.department.ilike(f"%{department}%"))

    if job_role and job_role.lower() != "all":
        query = query.filter(Employee.job_role.ilike(f"%{job_role}%"))

    if search:
        s = f"%{search}%"
        query = query.filter(
            (Employee.name.ilike(s)) |
            (Employee.employee_id.ilike(s)) |
            (Employee.email.ilike(s)) |
            (Employee.current_assignment.ilike(s))
        )

    total = query.count()
    items = query.order_by(Employee.employee_id).offset((page - 1) * page_size).limit(page_size).all()

    return EmployeeListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id.upper()).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return emp

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id.upper()).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

    if payload.current_assignment is not None:
        emp.current_assignment = payload.current_assignment
    if payload.education is not None:
        emp.education = payload.education
    if payload.previous_trainings is not None:
        emp.previous_trainings = payload.previous_trainings
    if payload.competency_domain is not None:
        emp.competency_domain = payload.competency_domain

    db.commit()
    db.refresh(emp)
    return emp
