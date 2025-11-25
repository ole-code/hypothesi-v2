# 🧬 Hypothesi v2.0
**Autonomous Scientific Review, Evidence Validation & Reliability Assessment System**

Hypothesi is a multi-agent AI system designed to ingest scientific content (PDFs, URLs, ArXiv papers), extract claims, verify evidence against the text, and generate a deterministic reliability score.

---

## 🚀 Features
*   **Auto-Ingestion:** Automatically detects PDF, URL, ArXiv ID, or Raw Text.
*   **Multi-Agent Pipeline:**
    *   **Structure Agent:** Extracts hypothesis, methods, and results.
    *   **Claim Agent:** Isolates atomic scientific claims.
    *   **Evidence Agent:** RAG-based retrieval to verify claims (Supports/Contradicts).
    *   **Reliability Agent:** Scores the paper 0-100 based on consistency.
*   **Hybrid Architecture:** Works deterministically (heuristic-only) or with LLM enhancement (Gemini 2.0 Flash).
*   **Observability:** Full JSONL event tracking and token metrics.

## 🛠️ Tech Stack
*   **Framework:** FastAPI + Uvicorn
*   **AI/LLM:** Google Gemini 2.0 Flash (via `google-generativeai`)
*   **Vector Search:** Scikit-Learn (KNN) + SentenceTransformers (`all-MiniLM-L6-v2`)
*   **Ingestion:** PyMuPDF, BeautifulSoup4, ArXiv API
*   **Infrastructure:** Docker + Google Cloud Run (Serverless)