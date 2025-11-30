# 🧬 Hypothesi v2.0
**The Autonomous Scientific Review, Evidence Validation & Reliability Assessment System**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688?style=flat-square&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-8E75B2?style=flat-square&logo=google)
![Docker](https://img.shields.io/badge/Deployment-Google%20Cloud%20Run-4285F4?style=flat-square&logo=google-cloud)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> **"Don't just read the abstract. Audit the evidence."**

**Hypothesi v2.0** is an autonomous multi-agent system designed to ingest scientific content, extract claims, verify them against the source text using **RAG (Retrieval Augmented Generation)**, and calculate a deterministic **Reliability Score**.

---

## 🔗 Try the Live Demo 
git inithttps://hypothesi-v2-953280003622.us-central1.run.app/

## 📖 The Problem & Solution

**The Problem:** Modern research output is overwhelming. Researchers and students are drowning in PDFs. Traditional AI summarizers only tell you *what* a paper says—they don't tell you *if it's reliable*. They often hallucinate details or gloss over methodological weaknesses.

**The Solution:** Hypothesi acts as an **Autonomous Auditor**. It doesn't just summarize; it deconstructs the paper into atomic claims and hunts for specific evidence chunks to support or refute them.

---

## 🏗️ Architecture & Technical Approach

### 1. "Code-First" Agents (Why we didn't use frameworks)
Instead of using high-level wrappers (like LangChain or AutoGen), Hypothesi uses explicit, class-based agents engineered from scratch.
*   **Reason:** Scientific verification requires **auditability** and **determinism**.
*   **Benefit:** This enables a **Hybrid Intelligence Engine**. If the LLM (Gemini) is offline or hallucinates invalid JSON, the system automatically switches to **Deterministic Heuristics** (Regex/Vector Search). This ensures the pipeline **Fail-Safes** rather than crashing.

### 2. The Sequential Agent Pipeline
We utilize a linear dependency chain where Agent A's output is Agent B's input.

```mermaid
graph TD
    User[User Input] --> Dispatcher{Auto-Dispatch}
    Dispatcher -->|ArXiv ID| ArXiv[ArXiv API Tool]
    Dispatcher -->|URL/PDF| Web[Web/PDF Tool]
    
    ArXiv & Web --> CleanText
    
    CleanText --> Orch[Orchestrator]
    
    Orch --> A1[Structure Agent]
    A1 --> A2[Claim Extraction Agent]
    A2 --> A3[Evidence Linking Agent]
    
    subgraph "Verification Loop"
    A3 --> RAG[Vector Search]
    RAG --> Check[Support/Contradict]
    end
    
    Check --> A4[Reliability Scoring]
    A4 --> A5[Meta-Reviewer]
    
    A5 --> FinalJSON