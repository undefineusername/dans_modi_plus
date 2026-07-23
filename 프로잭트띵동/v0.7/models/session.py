from dataclasses import dataclass
from typing import Optional

@dataclass
class Session:
    current_ai: str = "counselor"   # counselor, lifestyle, solution
    current_story_id: Optional[str] = None
    current_goal: str = "comfort"
    mood_score: int = 50
    conversation_count: int = 0
    started_time: Optional[str] = None
