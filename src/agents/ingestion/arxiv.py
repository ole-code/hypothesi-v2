import re
import xml.etree.ElementTree as ET
import unicodedata
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor

def ArxivIngestionTool(id_val, max_results=1):
    import requests
    url = f"http://export.arxiv.org/api/query?search_query=id:{id_val}&max_results={max_results}"
    resp = requests.get(url)
    root = ET.fromstring(resp.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    texts = []
    for entry in root.findall("atom:entry", ns):
        summary = entry.find("atom:summary", ns).text
        texts.append(summary)
    
    raw = unicodedata.normalize("NFKC", "\n\n".join(texts))
    return text_preprocessor(sanitizer(raw))