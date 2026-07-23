from models.session import Session
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.session = Session()

    def start_session(self):
        self.session.started_time = datetime.now().isoformat()
        self.session.conversation_count = 0

    def increment_count(self):
        self.session.conversation_count += 1

    def set_active_story(self, story_id: str):
        self.session.current_story_id = story_id

    def set_ai(self, ai_name: str):
        self.session.current_ai = ai_name

    def current_state(self) -> Session:
        return self.session
