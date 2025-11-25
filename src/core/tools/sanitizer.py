import unicodedata
def sanitizer(text, max_lines=300):
    if not isinstance(text, str): return ""
    text = unicodedata.normalize("NFKC", text)
    return "\n".join(text.splitlines()[:max_lines])