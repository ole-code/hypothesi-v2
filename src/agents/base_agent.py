import time
from src.core.observability.helpers import agent_start, agent_end
from src.core.observability.error_reporter import capture_and_log_exception

class BaseAgent:
    """
    Base class for all agents to ensure consistent logging and error handling.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    def _log_start(self, session_id, extra=None):
        agent_start(session_id, self.agent_name, extra)

    def _log_end(self, session_id, extra=None):
        agent_end(session_id, self.agent_name, extra)

    def _handle_error(self, error, where):
        return capture_and_log_exception({
            "where": where,
            "agent": self.agent_name,
            "error": str(error)
        })