import re
import os
import requests
import tempfile
from urllib.parse import urlparse
import unicodedata

# Import Tools
from src.agents.ingestion.pdf import PdfIngestionTool
from src.agents.ingestion.url import UrlIngestionTool
from src.agents.ingestion.arxiv import ArxivIngestionTool
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor
from src.core.logger import debug
from src.core.observability.error_reporter import capture_and_log_exception

def _download_temp_pdf(url):
    """
    Helper: Downloads a remote PDF to a temporary file.
    Returns the path to the temp file.
    """
    debug(f"Downloading remote PDF: {url}", tag="ingest")
    try:
        response = requests.get(url, timeout=15, stream=True)
        if response.status_code == 200:
            # Create a temp file that closes but doesn't delete immediately
            # so the PDF tool can open it by name
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                return tmp.name
    except Exception as e:
        capture_and_log_exception({"where": "download_pdf", "url": url, "error": str(e)})
    return None

def auto_ingest(source, **kwargs):
    """
    Smart dispatch logic.
    """
    try:
        raw_text = ""

        # --------------------------------------
        # 1. Local PDF File (File object or Path)
        # --------------------------------------
        if hasattr(source, "read") or (isinstance(source, str) and os.path.exists(source) and source.lower().endswith(".pdf")):
            debug("Ingesting Local PDF", tag="ingest")
            return PdfIngestionTool().load_pdf(source)

        # --------------------------------------
        # 2. URL Handling (Web vs PDF vs ArXiv)
        # --------------------------------------
        if isinstance(source, str):
            clean_source = source.strip()
            parsed = urlparse(clean_source)

            # A. ArXiv ID Detection (e.g., 2310.06825)
            if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", clean_source):
                debug("Ingesting ArXiv ID", tag="ingest")
                return ArxivIngestionTool(clean_source)

            # B. Web URLs
            if parsed.scheme in ("http", "https"):
                
                # CASE: Remote PDF URL
                if clean_source.lower().endswith(".pdf"):
                    debug("Ingesting Remote PDF URL", tag="ingest")
                    temp_path = _download_temp_pdf(clean_source)
                    if temp_path:
                        try:
                            # Use the PDF Tool on the downloaded file
                            raw_text = PdfIngestionTool().load_pdf(temp_path)
                        finally:
                            # Cleanup temp file
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        return raw_text
                    else:
                        raise RuntimeError("Failed to download remote PDF.")

                # CASE: Standard Webpage
                debug("Ingesting Webpage", tag="ingest")
                return UrlIngestionTool(clean_source)

        # --------------------------------------
        # 3. Fallback: Raw Text
        # --------------------------------------
        debug("Ingesting Raw Text", tag="ingest")
        # Sanitize and prep
        safe = sanitizer(str(source), max_lines=kwargs.get("max_lines", 5000))
        return text_preprocessor(safe, normalize_whitespace=True, max_length=200000)

    except Exception as e:
        capture_and_log_exception({"where": "auto_ingest", "error": str(e)})
        return {"error": True, "message": f"Ingestion failed: {str(e)}"}