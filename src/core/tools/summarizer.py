from src.core.tools.sanitizer import sanitizer
from src.core.observability.error_reporter import capture_and_log_exception

def summarization_tool(llm_callable=None):
    """
    Factory returning a summarizer function.
    """
    if llm_callable is None:
        # Fallback deterministic summarizer
        def dummy_summarize(text, style="short", session_id=None):
            safe = sanitizer(text)
            preview = safe[:200].replace("\n", " ")
            return "TL;DR: " + preview
        return dummy_summarize

    # LLM-powered summarizer
    def summarize(text, style="short", session_id=None):
        safe_text = sanitizer(text)
        prompt = (
            f"Provide a scientific summary ({style}) of the following text:\n"
            f"{safe_text}\n\nSummary:"
        )
        
        try:
            return llm_callable(prompt, session_id=session_id, agent_name="summarizer")
        except Exception as e:
            capture_and_log_exception({"where": "summarizer", "error": str(e)})
            raise

    return summarize