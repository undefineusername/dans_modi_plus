import os
from datetime import datetime
from llm import ask_groq

class AIChatSession:
    def __init__(self, prompt_file="prompt.txt"):
        self.history = []
        self.system_prompt = self._load_prompt(prompt_file)

    def _load_prompt(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return "당신은 친절한 AI 상담가 'MindMODI'입니다."

    def start_session(self, context: dict):
        """새로운 대화 세션 시작 시 Context 초기화"""
        self.history = []
        
        # Context 정보를 바탕으로 초기 시스템 가이드 구성
        context_info = (
            f"[현재 상태 정보]\n"
            f"- 일시: {context.get('time', datetime.now().strftime('%Y-%m-%d %H:%M'))}\n"
            f"- 사용자의 오늘 기분 점수: {context.get('mood', '알 수 없음')}/100점\n"
        )
        if "temperature" in context:
            context_info += f"- 주변 온도: {context['temperature']}°C\n"
            
        full_system_prompt = f"{self.system_prompt}\n\n{context_info}"
        return full_system_prompt

    def chat(self, user_input: str, system_prompt: str) -> str:
        """사용자 입력을 받아서 LLM 응답 반환 및 히스토리 갱신"""
        # Gemini history 형식으로 변환
        formatted_history = []
        for h in self.history:
            formatted_history.append({"role": h["role"], "parts": [h["content"]]})

        response_text = ask_groq(system_prompt, formatted_history, user_input)

        # 히스토리 기록
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "model", "content": response_text})

        return response_text