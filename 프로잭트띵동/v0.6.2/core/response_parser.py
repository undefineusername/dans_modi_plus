# core/response_parser.py
import json
import re
from typing import Dict, Any

class ResponseParser:
    def __init__(self):
        # 파싱 실패 시 시스템 다운을 막기 위한 최소한의 안전 구조 정의
        self.default_fallback = {
            "thinking": "파서가 응답을 복구하는 중 오류가 발생하여 기본 상태를 로드했습니다.",
            "reply": "음... 방금 네 말을 듣고 머릿속이 살짝 복잡해졌어. 다시 얘기해 줄래?",
            "story_update": {
                "completion": 10,
                "missing": []
            },
            "memory_update": {
                "action": "IGNORE",
                "category": "etc",
                "entity_name": "",
                "summary": "",
                "importance": 50
            },
            "emotion_update": {
                "emotion": "neutral",
                "stress_delta": 0,
                "trust_delta": 0
            }
        }

    def parse_and_fix(self, raw_text: str) -> Dict[str, Any]:
        """Raw 텍스트를 청소하고 검증하여 안전한 Python Dict 객체로 반환"""
        if not raw_text or raw_text.strip() == "{}":
            return self.default_fallback

        cleaned = raw_text.strip()

        # 1. 마크다운 코드 블록 제거 (```json ... ``` 형태 제거)
        if cleaned.startswith("```"):
            # 정규식을 이용해 앞뒤의 백틱과 언어 명시 제거
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        # 2. JSON 파싱 시도
        try:
            parsed_data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"⚠️ [Parser Warning] JSON 구조가 깨져 자가 치유를 시도합니다. 에러: {e}")
            # 정교한 자가 치유(예: 줄바꿈 문자로 인한 에러 등)를 시도할 수 있으나,
            # 지금은 안전하게 폴백 데이터를 반환하여 무중단 상태를 유지함.
            return self.default_fallback

        # 3. 필수 키 검증 및 보정 (Schema Validation)
        validated_data = self._validate_and_fill_schema(parsed_data)
        return validated_data

    def _validate_and_fill_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """추출된 JSON에 필수 키들이 다 들어있는지 확인하고 누락된 것은 기본값으로 보정"""
        fixed = {}

        # 기본 탑벨 수준 키 검증
        fixed["thinking"] = str(data.get("thinking", self.default_fallback["thinking"]))
        fixed["reply"] = str(data.get("reply", self.default_fallback["reply"]))

        # story_update 영역 보정
        story = data.get("story_update", {})
        if not isinstance(story, dict):
            story = {}
        fixed["story_update"] = {
            "completion": int(story.get("completion", self.default_fallback["story_update"]["completion"])),
            "missing": list(story.get("missing", self.default_fallback["story_update"]["missing"]))
        }

        # memory_update 영역 보정
        memory = data.get("memory_update", {})
        if not isinstance(memory, dict):
            memory = {}
        fixed["memory_update"] = {
            "action": str(memory.get("action", self.default_fallback["memory_update"]["action"])),
            "category": str(memory.get("category", self.default_fallback["memory_update"]["category"])),
            "entity_name": str(memory.get("entity_name", self.default_fallback["memory_update"]["entity_name"])),
            "summary": str(memory.get("summary", self.default_fallback["memory_update"]["summary"])),
            "importance": int(memory.get("importance", self.default_fallback["memory_update"]["importance"]))
        }

        # emotion_update 영역 보정
        emotion = data.get("emotion_update", {})
        if not isinstance(emotion, dict):
            emotion = {}
        fixed["emotion_update"] = {
            "emotion": str(emotion.get("emotion", self.default_fallback["emotion_update"]["emotion"])),
            "stress_delta": int(emotion.get("stress_delta", self.default_fallback["emotion_update"]["stress_delta"])),
            "trust_delta": int(emotion.get("trust_delta", self.default_fallback["emotion_update"]["trust_delta"]))
        }

        return fixed