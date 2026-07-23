from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Profile:
    name: str = "사용자"
    age: Optional[int] = None
    character: List[str] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    family_members: List[str] = field(default_factory=list)
    sleep_patterns: str = "Unknown"
