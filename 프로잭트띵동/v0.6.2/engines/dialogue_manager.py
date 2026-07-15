# engines/dialogue_manager.py
import json
import asyncio
from typing import Dict, Any

from engines.story_engine import StoryEngine
from core.prompt_builder import PromptBuilder
from core.api import GroqAPIClient  # Groq 비동기 통신 객체 가정
from core.response_parser import ResponseParser

class DialogueManager:
    def __init__(self):
        self.story_engine = StoryEngine()
        # self.memory_engine = MemoryEngine() # (구현 예정)
        # self.emotion_engine = EmotionEngine() # (구현 예정)
        self.prompt_builder = PromptBuilder()
        self.api_client = GroqAPIClient()
        self.parser = ResponseParser()

    async def handle_message(self, user_text: str) -> str:
        # 1. 🔍 장기 기억 탐색 (RAG)
        # 💡 [v1.0 설계] memory_engine 구현 전까지 빈 리스트로 대응
        matched_memories = [] 
        
        # 2. 📝 각 인지 엔진들로부터 현재 상태 수집
        current_story = self.story_engine.get_current_context()
        current_emotion = {"emotion": "neutral", "stress": 50, "trust": 60} # (가짜 상태 데이터)
        current_profile = {"name": "단이", "grade": "중3", "style": "친구처럼"} # (가짜 상태 데이터)
        
        # 3. 🏗️ Prompt Builder를 통한 문장화 및 프롬프트 생성
        system_prompt = self.prompt_builder.build_system_instruction(
            profile=current_profile,
            story=current_story,
            emotion=current_emotion,
            memories=matched_memories
        )
        
        # 4. 🤖 LLM 비동기 호출
        raw_response = await self.api_client.request_completion(system_prompt, user_text)
        
        # 5. 🔍 응답 파싱 및 유효성 자가 보정
        parsed_data = self.parser.parse_and_fix(raw_response)
        
        # 6. 💾 파싱 결과를 바탕으로 각 인지 엔진 비동기 업데이트 실행 (Fire-and-Forget 방지용 Task 등록)
        reply = parsed_data.get("reply", "어... 미안 방금 딴생각했어. 다시 말해줘!")
        
        asyncio.create_task(self._update_engines_async(parsed_data))
        
        return reply

    async def _update_engines_async(self, parsed_data: Dict[str, Any]):
        """메인 응답 송출 속도에 영향을 주지 않도록 백그라운드에서 엔진 업데이트 진행"""
        try:
            # 스토리 정보 동기화
            if "story_update" in parsed_data:
                self.story_engine.update_story_state(parsed_data["story_update"])
            
            # TODO: memory_engine.update_memory(...)
            # TODO: emotion_engine.update_emotion(...)
            
        except Exception as e:
            print(f"❌ [Engine Update Error] 백그라운드 업데이트 실패: {e}")