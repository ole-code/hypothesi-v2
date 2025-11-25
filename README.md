# 🧬 Hypothesi v2.0

The Autonomous Scientific Review, Evidence Validation & Reliability Assessment System

"Don't just read the abstract. Audit the evidence."

Hypothesi v2.0 is a multi-agent AI system designed to ingest scientific content, extract claims, verify them against the source text using RAG (Retrieval Augmented Generation), and calculate a deterministic Reliability Score.

# 📖 The Problem & Solution
The Problem: Modern research output is overwhelming. Researchers, students, and journalists are drowning in PDFs. Traditional AI summarizers only tell you what a paper says—they don't tell you if it's reliable. They often hallucinate details or gloss over methodological weaknesses.

The Solution: Hypothesi acts as an Autonomous Auditor. It doesn't just summarize; it deconstructs the paper into atomic claims and hunts for specific evidence to support or refute them.

# 👥 Target Personas
The Overwhelmed Academic: Needs to triage hundreds of ArXiv papers to find valid research gaps without wasting hours on papers with weak methodology.
The Science Journalist: Needs to fact-check "breakthrough" claims against the actual data before publishing news to avoid reputational damage.
The R&D Analyst: Needs to verify competitor claims without relying on hallucinated summaries that could cost the business money.

# 🏗️ Architecture & Design Decisions

1. "Code-First" Agents vs. Frameworks
Instead of using high-level wrappers (like LangChain Agent or AutoGen), Hypothesi uses explicit, class-based agents engineered from scratch.
Reason: Scientific review requires auditability and determinism. Generic frameworks often obscure the control loop.
Benefit: This enables a Hybrid Intelligence Engine. If the LLM (Gemini) is offline or hallucinates invalid JSON, the system automatically switches to Deterministic Heuristics (Regex/Vector Search). This ensures the pipeline Fail-Safes rather than crashing.

2. The Sequential Agent Pipeline
We utilize a linear dependency chain where Agent A's output is Agent B's input. This prevents infinite loops and ensures a consistent output format.
code

3. Agents Breakdown
Structure Agent: Identifies the "Scientific Skeleton" (Hypothesis, Methods, Results).
Claim Agent: Isolates atomic, testable scientific assertions (filtering out fluff).
Evidence Agent: Performs RAG using SentenceTransformers to retrieve top-k text chunks and classifies them as SUPPORTS, CONTRADICTS, or INSUFFICIENT.
Reliability Agent: The auditor that calculates the score.
Meta-Reviewer: Synthesizes the final human-readable report and limitations list.

# 🧮 The Scoring Logic
We do not ask the LLM to "rate this paper 1-10." LLM ratings are subjective and prone to sycophancy. Hypothesi uses a Deterministic Algorithm based on the findings of the agents:
+30 Points: Methods section is present and substantial.
+20 Points: Results section is present.
+50 Points (Variable): Percentage of claims explicitly backed by textual evidence (RAG verification).
-20 Points (Penalty): For every specific contradiction found in the text.
This ensures the score reflects structural integrity and consistency, not just how "well-written" the abstract is.

# 📂 Project Structure
This project follows a modular, production-grade directory structure.

hypothesi-v2/
├── main.py                 # FastAPI Entry Point & Routes
├── Dockerfile              # Cloud Run Container Configuration
├── requirements.txt        # Python Dependencies
├── src/
│   ├── agents/             # The Logic Layer (The "Workers")
│   │   ├── ingestion/      # PDF, URL, ArXiv Auto-Dispatcher
│   │   ├── structure.py    # Structure Extraction Agent
│   │   ├── claims.py       # Claim Isolation Agent
│   │   ├── evidence.py     # RAG Verification Agent
│   │   └── reliability.py  # Scoring Math Agent
│   ├── core/               # The Brain
│   │   ├── orchestrator.py # Pipeline Manager
│   │   ├── context/        # Memory, Session & Chunking Engine
│   │   └── observability/  # JSONL Logging & Error Tracking
│   └── static/             # Frontend (HTML + Tailwind CSS)

# ⚡ Quick Start (Local)
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

# Windows:
venv\Scripts\activate

# Mac/Linux:
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

# Run the App
Bash
python main.py
Visit http://localhost:8080 to access the UI.

☁️ Deployment (Google Cloud Run)
This project is containerized and optimized for Serverless deployment.
code
Bash
# 1. Set Project
gcloud config set project YOUR_PROJECT_ID

# 2. Deploy
gcloud run deploy hypothesi-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
Note: Don't forget to set the GEMINI_API_KEY in the Cloud Run "Variables & Secrets" tab.
🛡️ License
This project is open-source under the MIT License.