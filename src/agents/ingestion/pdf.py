import os
import unicodedata
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor

try: import fitz; HAVE_PYMUPDF=True
except: HAVE_PYMUPDF=False
try: import PyPDF2; HAVE_PYPDF2=True
except: HAVE_PYPDF2=False

class PdfIngestionTool:
    def load_pdf(self, path, max_length=200000):
        if not os.path.exists(path): raise FileNotFoundError(path)
        raw = ""
        if HAVE_PYMUPDF:
            try:
                doc = fitz.open(path)
                raw = "\n".join([page.get_text() for page in doc])
            except: pass
        if not raw and HAVE_PYPDF2:
            try:
                reader = PyPDF2.PdfReader(path)
                raw = "\n".join([p.extract_text() for p in reader.pages])
            except: pass
        
        if not raw: raise RuntimeError("PDF read failed")
        raw = unicodedata.normalize("NFKC", raw)
        return text_preprocessor(sanitizer(raw, max_lines=5000), max_length=max_length)