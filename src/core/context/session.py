import uuid
from datetime import datetime

class Session:
    def __init__(self, user_id="anon"):
        self.session_id = str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.state = {}