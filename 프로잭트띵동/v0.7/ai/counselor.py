from ai.engine import GroqEngine
from prompts import build_counselor_prompt


class Counselor:
    """기분 점수 기반 간단 상담 세션."""

    def __init__(self, mood: int):
        self.mood = mood
        self.engine = GroqEngine()
        self.messages = [
            {"role": "system", "content": build_counselor_prompt(mood)}
        ]

    def opening_message(self) -> str:
        if self.mood <= 30:
            return f"오늘 기분 점수가 {self.mood}점이네요. 힘든 일이 있었나요?"
        if self.mood >= 70:
            return f"오늘 {self.mood}점이네요! 좋은 하루인 것 같아요. 이야기해 볼래요?"
        return f"오늘 기분은 {self.mood}점이군요. 무슨 일이 있었는지 들려줄래요?"

    def chat(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        reply = self.engine.chat(self.messages)
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def refresh_system_prompt(self):
        self.messages[0] = {
            "role": "system",
            "content": build_counselor_prompt(self.mood),
        }
