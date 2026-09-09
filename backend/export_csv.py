import os
import sys
import csv

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.employee import Employee
from app.models.competency import Competency
from app.models.course import IGOTCourse, NSSTAProgramme

def export_csv_data():
    db = SessionLocal()
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    # 1. Employees CSV
    employees = db.query(Employee).all()
    emp_path = os.path.join(data_dir, "employees.csv")
    with open(emp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["employee_id", "name", "email", "department", "department_code", "designation", "job_role", "current_assignment", "education", "years_of_experience", "joining_date", "previous_trainings", "competency_domain", "role"])
        for e in employees:
            writer.writerow([e.employee_id, e.name, e.email, e.department, e.department_code, e.designation, e.job_role, e.current_assignment, e.education, e.years_of_experience, e.joining_date, e.previous_trainings, e.competency_domain, e.role])

    # 2. Competencies CSV
    competencies = db.query(Competency).all()
    comp_path = os.path.join(data_dir, "competencies.csv")
    with open(comp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "name", "category", "domain", "description", "max_level"])
        for c in competencies:
            writer.writerow([c.code, c.name, c.category, c.domain, c.description, c.max_level])

    # 3. iGOT Courses CSV
    igot_courses = db.query(IGOTCourse).all()
    igot_path = os.path.join(data_dir, "igot_courses.csv")
    with open(igot_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["course_id", "title", "provider", "description", "duration_hours", "competency_tags", "category", "difficulty", "course_url", "source", "active"])
        for c in igot_courses:
            writer.writerow([c.course_id, c.title, c.provider, c.description, c.duration_hours, c.competency_tags, c.category, c.difficulty, c.course_url, c.source, c.active])

    # 4. NSSTA Programmes CSV
    nssta_progs = db.query(NSSTAProgramme).all()
    nssta_path = os.path.join(data_dir, "nssta_programmes.csv")
    with open(nssta_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["training_id", "title", "provider", "description", "duration_days", "duration_hours", "competency_tags", "category", "level", "target_audience", "programme_url", "source", "active"])
        for p in nssta_progs:
            writer.writerow([p.training_id, p.title, p.provider, p.description, p.duration_days, p.duration_hours, p.competency_tags, p.category, p.level, p.target_audience, p.programme_url, p.source, p.active])

    db.close()
    print(f"[OK] Exported CSVs to {data_dir}")

if __name__ == "__main__":
    export_csv_data()
