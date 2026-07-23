from typing import List, Dict

class ConversationHistory:
    def __init__(self, max_length: int = 20):
        self.history: List[Dict[str, str]] = []
        self.max_length = max_length

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_length * 2:
            self.compress()

    def recent(self, count: int = None) -> List[Dict[str, str]]:
        if count is None:
            count = self.max_length
        return self.history[-count:]

    def clear(self):
        self.history = []

    def compress(self):
        \"\"\"
        토큰 절약을 위해 이전 대화 내용들을 하나의 요약본(System Prompt 형태 등)으로 압축합니다.
        추후 LLM을 호출하여 요약하는 로직을 연동할 수 있습니다.
        \"\"\"
        if len(self.history) <= 4:
            return  # 압축하기엔 너무 짧음
        
        # 임시 로직: 오래된 대화를 잘라내고 요약 텍스트로 대체하는 뼈대
        old_messages = self.history[:-4]
        # TODO: old_messages를 LLM에 보내어 요약 텍스트를 받음
        summary_text = "이전 대화 요약: 사용자가 기분이 안 좋다고 하였음."
        
        self.history = [
            {"role": "system", "content": summary_text}
        ] + self.history[-4:]
