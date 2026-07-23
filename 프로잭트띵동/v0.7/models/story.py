from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Story:
    id: str
    title: str
    status: str
    timeline: List[str] = field(default_factory=list)
    summary: str = ""
    keywords: List[str] = field(default_factory=list)
    related_stories: List[str] = field(default_factory=list)
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
