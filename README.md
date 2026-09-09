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

## Quick Start Guide (For Team Members & Fresh Clones)

### 1. Clone the Repository
```bash
git clone https://github.com/PATIL-SANTHOSH/StatSaksham.git
cd StatSaksham
```

### 2. Backend Setup (FastAPI + Python)
```powershell
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI backend (Auto-seeds database on first launch!)
.\start_backend.ps1
# OR manually:
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Frontend Setup (React + Vite + Tailwind)
```powershell
# In a new terminal window:
cd frontend
npm install
npm run dev
# OR from root directory:
.\start_frontend.ps1
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
