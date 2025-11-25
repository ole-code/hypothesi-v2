import re
import os
import html
import tempfile
import unicodedata
from urllib.parse import urlparse
from src.core.logger import debug
from src.core.observability.error_reporter import capture_and_log_exception
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor

# Import PDF Tool for fallback
from src.agents.ingestion.pdf import PdfIngestionTool

def UrlIngestionTool(url, timeout=15, max_bytes=10*1024*1024, allowlist=None):
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("requests/bs4 missing")

    try:
        debug(f"Fetching URL: {url}", tag="url")
        
        # 1. Initial Request (Stream=True to check headers first)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        
        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}")

        # 2. Check Content-Type (The Critical Fix)
        content_type = resp.headers.get("Content-Type", "").lower()
        
        # --- CASE A: It's actually a PDF ---
        if "application/pdf" in content_type:
            debug("Detected PDF Content-Type. Switching to PDF Tool.", tag="url")
            
            # Save stream to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                downloaded_bytes = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                    downloaded_bytes += len(chunk)
                    if downloaded_bytes > max_bytes:
                        tmp.close()
                        os.remove(tmp.name)
                        raise RuntimeError("PDF too large")
                temp_path = tmp.name
            
            try:
                # Delegate to the PDF logic
                pdf_loader = PdfIngestionTool()
                return pdf_loader.load_pdf(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # --- CASE B: Standard HTML ---
        # Verify size limit for HTML
        content = b""
        for chunk in resp.iter_content(8192):
            content += chunk
            if len(content) > max_bytes: raise RuntimeError("HTML too large")
        
        soup = BeautifulSoup(content.decode(errors="ignore"), "html.parser")
        
        # Remove noise
        for t in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg"]):
            t.decompose()
        
        # Extract text
        raw = soup.get_text("\n")
        raw = unicodedata.normalize("NFKC", html.unescape(raw))
        
        # Post-process
        safe = sanitizer(raw, max_lines=5000)
        return text_preprocessor(safe, max_length=200000)

    except Exception as e:
        capture_and_log_exception({"where": "url_ingest", "url": url, "error": str(e)})
        # Return clean error string rather than crashing, so pipeline can handle it
        return ""