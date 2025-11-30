Here is the full, corrected README.md file. I have fixed the Mermaid syntax error, inserted your specific Cloud Run link, and removed the screenshot placeholders as requested.
You can copy and paste this directly into your repository.
code
Markdown
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

## 🔗 [Try the Live Demo](https://hypothesi-v2-953280003622.us-central1.run.app/)
*(Note: Paste a URL, raw text, or ArXiv ID to trigger the autonomous review)*

---

## 📖 The Problem & Solution

**The Problem:** Modern research output is overwhelming. Researchers and students are drowning in PDFs. Traditional AI summarisers only tell you *what* a paper says—they don't tell you *if it's reliable*. They often hallucinate details or gloss over methodological weaknesses.

**The Solution:** Hypothesi acts as an **Autonomous Auditor**. It doesn't just summarise; it deconstructs the paper into atomic claims and hunts for specific evidence chunks to support or refute them.

---

## 🏗️ Architecture & Technical Approach

### 1. "Code-First" Agents (Why we didn't use frameworks)
Instead of using high-level wrappers (like LangChain or AutoGen), Hypothesi uses explicit, class-based agents engineered from scratch.
*   **Reason:** Scientific verification requires **auditability** and **determinism**.
*   **Benefit:** This enables a **Hybrid Intelligence Engine**. If the LLM (Gemini) is offline or hallucinates invalid JSON, the system automatically switches to **Deterministic Heuristics** (Regex/Vector Search). This ensures the pipeline **Fail-Safes** rather than crashing.

### 2. 🧮 The Scoring Logic (Deterministic)
We do not ask the LLM to "rate this paper 1-10." LLM ratings are subjective. Hypothesi uses a Deterministic Algorithm based on the findings of the agents:
+30 Points: Methods section is present and substantial.
+20 Points: Results section is present.
+50 Points (Variable): Percentage of claims explicitly backed by textual evidence (RAG verification).
-20 Points (Penalty): For every specific contradiction found in the text.
This ensures the score reflects structural integrity and consistency, not just how "well-written" the abstract is.

### 3.📂 Project Structure
This project follows a modular, production-grade directory structure suitable for CI/CD pipelines.
code
Text
hypothesi-v2/
├── main.py                 # FastAPI Entry Point & Routes
├── Dockerfile              # Cloud Run Container Configuration
├── requirements.txt        # Python Dependencies
├── .env                    # Local Secrets (Not uploaded to Prod)
├── src/
│   ├── agents/             # The Logic Layer (The "Workers")
│   │   ├── ingestion/      # PDF, URL, ArXiv Auto-Dispatcher
│   │   ├── structure.py    # Structure Extraction Agent
│   │   ├── claims.py       # Claim Isolation Agent
│   │   ├── evidence.py     # RAG Verification Agent
│   │   ├── reliability.py  # Scoring Math Agent
│   │   └── meta_reviewer.py # Final Report Synthesiser
│   │
│   ├── core/               # The Brain
│   │   ├── orchestrator.py # Pipeline Manager
│   │   ├── context/        # Memory, Session & Chunking Engine
│   │   ├── tools/          # Embeddings, Sanitizers, LLM Wrappers
│   │   └── observability/  # JSONL Logging & Error Tracking
│   │
│   └── static/             # Frontend (HTML + Tailwind CSS)

### 4.⚡ Quick Start (Local Development)
Prerequisites: Python 3.10+, Google AI Studio API Key.
Clone the repository
code
Bash
git clone https://github.com/YOUR_USERNAME/hypothesi-v2.git
cd hypothesi-v2
Set up Environment
code
Bash
python -m venv venv
### Windows:
venv\Scripts\activate
### Mac/Linux:
source venv/bin/activate
Install Dependencies
code
Bash
pip install -r requirements.txt
Configure Secrets
Create a .env file in the root directory:
code
Text
GEMINI_API_KEY=your_key_starts_with_AIza...
HYPOTHESI_RUNTIME_MODE=local
Run the App
code
Bash
python main.py
Visit http://localhost:8080 to access the UI.
☁️ Deployment (Google Cloud Run)
This project is containerised and optimised for Serverless deployment.
code
Bash
### 4.1. Set Project
gcloud config set project YOUR_PROJECT_ID

### 4.2. Deploy
gcloud run deploy hypothesi-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --set-env-vars HYPOTHESI_RUNTIME_MODE=prod
Note: Don't forget to set the GEMINI_API_KEY in the Cloud Run "Variables & Secrets" tab after deployment.
### 4.3.🛡️ License
This project is open-source under the MIT License.
code
Code