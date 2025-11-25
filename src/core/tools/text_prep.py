import re
def text_preprocessor(text, normalize_whitespace=True, max_length=None):
    s = text or ""
    if normalize_whitespace: s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(?mi)^(system:|assistant:|user:).*", "", s)
    if max_length and len(s) > max_length: s = s[:max_length]
    return s