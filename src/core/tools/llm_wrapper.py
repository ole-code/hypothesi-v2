from src.core.secrets.manager import get_runtime_secrets
from src.core.tools.text_prep import text_preprocessor
from src.core.observability.error_reporter import capture_and_log_exception

def llm_wrapper(model_id: str = "gemini-2.0-flash"):
    cache = {"model": None}
    def call(prompt, **kwargs):
        api_key = get_runtime_secrets().require("GEMINI_API_KEY")
        if not cache["model"]:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            cache["model"] = genai.GenerativeModel(model_id)
        
        safe = text_preprocessor(prompt, max_length=90000)
        try:
            return cache["model"].generate_content(safe).text
        except Exception as e:
            capture_and_log_exception({"where": "llm_call", "error": str(e)})
            raise
    return call