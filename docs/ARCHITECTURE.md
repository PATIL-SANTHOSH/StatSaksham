# STATSAKSHAM — Technical Architecture Documentation

**Problem Statement**: SIH26101  
**Organization**: Ministry of Statistics and Programme Implementation (MoSPI)  
**Department**: Data Informatics & Innovation Division (DIID)  
**Tagline**: *"Empowering Statistical Officials Through Intelligent Learning"*

---

## 1. System Overview

StatSaksham is an AI-powered competency intelligence and personalized capacity building platform designed specifically for government officials across India's Official Statistical System.

Unlike generic Learning Management Systems (LMS), StatSaksham operates on a continuous competency intelligence loop:

```
EMPLOYEE PROFILE
       ↓
COMPETENCY REQUIREMENTS (Role-based)
       ↓
ASSESSMENT
       ↓
CURRENT COMPETENCY (1–5 Scale)
       ↓
SKILL GAP ANALYSIS (Deterministic)
       ↓
PERSONALIZED RECOMMENDATIONS (Multi-signal)
       ↓
iGOT COURSES + NSSTA/TPAC PROGRAMMES (Adapters)
       ↓
LEARNING PROGRESS
       ↓
AI-GENERATED QUIZ / MCQ (RAG Pipeline)
       ↓
EVALUATION RESULTS
       ↓
COMPETENCY UPDATE
       ↓
GAP RECALCULATION
       ↓
UPDATED LEARNING PATH
```

---

## 2. Core Architecture Components

### A. Database & Data Models
- Relational schema implemented via SQLAlchemy (PostgreSQL / SQLite portable).
- 110+ Synthetic MoSPI employee personas across 8 major divisions (NAD, PSD, FOD, SDRD, SSD, ESD, DIID, CPD).
- 28 Competencies across 4 categories: Statistical, Technical, Digital Governance, Behavioural/Managerial.
- 51 iGOT Karmayogi verified prototype catalogue courses.
- 31 NSSTA / TPAC specialized training programmes.

### B. Rule & Competency Engine (Deterministic)
- **Competency Scale**: 1 (Beginner) to 5 (Expert).
- **Skill Gap Formula**:
  $$\text{Skill Gap} = \max(0, \text{Required Competency Level} - \text{Current Competency Level})$$
- **Gap Classification**:
  - $0 \to \text{No Gap (Benchmark Met)}$
  - $1 \to \text{Low Gap}$
  - $2 \to \text{Medium Gap}$
  - $\ge 3 \to \text{High Priority Gap}$
- **Priority Calculation**: Combines gap size, role importance weight (1–5), operational assignment matching, and division focus.

### C. Integration-Ready Learning Adapters
- `BaseLearningProvider`: Abstract base class for extensible provider connectors.
- `IGOTAdapter`: Connects to iGOT Karmayogi course metadata.
- `NSSTAAdapter`: Connects to NSSTA / TPAC training programmes.
- Ready for zero-rewrite transition to live REST / GraphQL APIs when official government credentials are provided.

### D. RAG & AI Layer (Dual Architecture)
- **Primary AI**: Local Ollama server hosting `qwen3.5:9b`, `llama3.1:8b`, and `nomic-embed-text`.
- **Intelligent Fallback AI**: Heuristic domain NLP engine ensuring 100% platform availability if Ollama is paused or unreachable.
- **RAG Pipeline**:
  1. Document ingestion (PDF via `pypdf`, PPTX via `python-pptx`, TXT, DOCX).
  2. Semantic chunking (600 characters with 100 character overlap).
  3. Embedding generation (`nomic-embed-text` / cosine vector index).
  4. Vector similarity search for question generation and grounded tutor Q&A.
  5. LLM prompt synthesis for 5–20 role-aligned MCQs with explanations and citations.

---

## 3. Technology Stack

- **Frontend**: React, Vite, Tailwind CSS, React Router DOM, Axios, Recharts, Lucide React.
- **Backend**: Python 3.14, FastAPI, SQLAlchemy, Pydantic Settings, PyJWT, BCrypt.
- **AI & RAG**: Ollama, `pypdf`, `python-pptx`, NumPy.
- **Database**: PostgreSQL / SQLite zero-config portable store.
