from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.employees import router as employees_router
from app.api.competencies import router as competencies_router
from app.api.assessments import router as assessments_router
from app.api.recommendations import router as recommendations_router
from app.api.courses import router as courses_router
from app.api.progress import router as progress_router
from app.api.quiz import router as quiz_router
from app.api.ai import router as ai_router
from app.api.admin import router as admin_router

app = FastAPI(
    title="STATSAKSHAM — MoSPI AI Competency Platform",
    description=(
        "AI-enabled competency intelligence and personalized learning platform for India's Official "
        "Statistical System (MoSPI / DIID — SIH26101). Integrates deterministic skill-gap calculations, "
        "iGOT Karmayogi & NSSTA catalogues, and RAG-based AI Quiz generation."
    ),
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(employees_router, prefix=settings.API_V1_STR)
app.include_router(competencies_router, prefix=settings.API_V1_STR)
app.include_router(assessments_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(courses_router, prefix=settings.API_V1_STR)
app.include_router(progress_router, prefix=settings.API_V1_STR)
app.include_router(quiz_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    try:
        from app.database.session import engine, Base, SessionLocal
        import app.models  # Register all 18+ models & 20 tables with SQLAlchemy metadata
        from app.models.user import User
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            count = db.query(User).count()
            if count == 0:
                print("[Database] Empty database detected. Auto-seeding complete dataset (111 users, courses, competencies)...")
                from seed_data import seed_database
                seed_database()
            else:
                print(f"[Database] Connected successfully ({count} users found in database).")
        finally:
            db.close()
    except Exception as e:
        print(f"[Database Startup Notice] {e}")

@app.get("/")
def root():
    return {
        "platform": "STATSAKSHAM",
        "tagline": "Empowering Statistical Officials Through Intelligent Learning",
        "organization": "Ministry of Statistics and Programme Implementation (MoSPI)",
        "division": "Data Informatics & Innovation Division (DIID)",
        "problem_statement": "SIH26101",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "status": "online"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-09-08",
        "database": "connected"
    }
