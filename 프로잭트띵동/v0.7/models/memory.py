from dataclasses import dataclass
from typing import Optional

@dataclass
class Memory:
    id: str
    story_id: str
    type: str # e.g., 'keyword', 'summary', 'event'
    content: str
    importance: int # 1 to 5 scale
    created_at: str
    expires_at: Optional[str] = None
