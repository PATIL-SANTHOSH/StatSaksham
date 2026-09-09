# STATSAKSHAM (SIH 2026 | SIH26101)

### AI-Enabled Competency Intelligence and Capacity Building Platform for India's Official Statistical System

**Ministry**: Ministry of Statistics and Programme Implementation (MoSPI)  
**Division**: Data Informatics & Innovation Division (DIID)  
**Tagline**: *"Empowering Statistical Officials Through Intelligent Learning"*  
**Alternative Motto**: *"Assess. Learn. Improve."*

---

## Key Features

1. **Deterministic Competency & Skill Gap Engine**:
   - 1–5 level scale (Beginner to Expert).
   - Role-based requirements tailored by cadre designation, division, and operational assignment.
   - Skill Gap = Required Level - Current Level with priority weighting.
2. **Integration-Ready Catalogue Adapters**:
   - **iGOT Karmayogi**: 51 verified prototype catalogue courses with tags, duration, and difficulty.
   - **NSSTA / TPAC**: 31 specialized training programmes from the National Statistical Systems Training Academy.
   - Multi-signal recommendation ranking with human-readable *"Why this was recommended"* explanations.
3. **RAG-Powered AI Quiz / MCQ Generator**:
   - Upload official PDF, PPTX, TXT documents or paste excerpts.
   - Text extraction, semantic chunking, and vector embedding similarity search.
   - Dual AI layer (Ollama local LLM with robust Heuristic Knowledge Fallback).
4. **Conversational AI Learning Assistant**:
   - Statistical mentor answering queries on SNA 2008, CPI, PLFS, Sampling, Python, R, and career skill pathways.
5. **Workforce Intelligence & Admin Analytics**:
   - Real-time aggregated metrics across 110+ synthetic MoSPI officers.
   - Interactive Recharts for department gap distributions, competency tiers, and training provider effectiveness.

---

## Showcase Demo Accounts

| Employee ID | Name | Role | Department | Password |
|---|---|---|---|---|
| **`OSS1001`** | Ravi Kumar | Statistical Officer (Data Analyst) | National Accounts Division | `demo123` |
| **`OSS1002`** | Priya Sharma | Junior Statistical Officer | Price Statistics Division | `demo123` |
| **`OSS1003`** | Amit Verma | Statistical Officer (Survey Operations) | Field Operations Division | `demo123` |
| **`OSS1004`** | Neha Singh | Research Officer | Data Informatics Division | `demo123` |
| **`OSS1005`** | Arjun Rao | Assistant Director | Economic Statistics Division | `demo123` |
| **`ADMIN001`** | Admin Official | Joint Director (Workforce & Training) | DIID / Capacity Building | `admin123` |

---

## Quick Start Guide

### 1. Backend Setup (FastAPI)
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# (Optional) Seed the database with 110+ employees & 80+ courses
python backend\seed_data.py

# Start FastAPI server (Port 8000)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend Setup (React + Vite)
```powershell
cd frontend
npm run dev
```
Web Application: [http://localhost:5173](http://localhost:5173)

---

## Project Structure
```
SIH_prototype/
├── backend/
│   ├── app/
│   │   ├── api/             # REST Routers (auth, competencies, quiz, ai, admin, etc.)
│   │   ├── core/            # Config, security, database session
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Competency, skill gap, and recommendation engines
│   │   ├── integrations/    # iGOT and NSSTA adapters
│   │   ├── ai/              # Ollama client, RAG engine, quiz generator, assistant
│   │   └── main.py          # FastAPI application entry point
│   ├── data/                # Exported CSV data catalogues
│   ├── seed_data.py         # Database seeder (110+ personnel, 80+ courses)
│   ├── test_backend.py      # Automated backend test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, Sidebar, StatCard, LevelMeter, Badges
│   │   ├── pages/           # Dashboard, Profile, Competencies, Assessment, Quiz, etc.
│   │   ├── context/         # AuthContext with 1-click persona logins
│   │   └── services/        # Axios API client
│   ├── package.json
│   └── tailwind.config.js
├── docs/
│   ├── ARCHITECTURE.md      # Detailed system architecture
│   └── DEMO_GUIDE.md        # 26-Step Master Demonstration Walkthrough
└── docker-compose.yml
```
