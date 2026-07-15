# engines/emotion_engine.py
import json
import os
from typing import Dict, Any
from config import EMOTION_PATH

class EmotionEngine:
    def __init__(self):
        self.emotion_data = self._load_emotion()

    def _load_emotion(self) -> Dict[str, Any]:
        default_emotion = {
            "emotion": "neutral",
            "stress": 50,
            "trust": 60
        }
        if os.path.exists(EMOTION_PATH):
            try:
                with open(EMOTION_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default_emotion
        return default_emotion

    def save_emotion(self):
        with open(EMOTION_PATH, "w", encoding="utf-8") as f:
            json.dump(self.emotion_data, f, ensure_ascii=False, indent=4)

    def get_current_context(self) -> Dict[str, Any]:
        return self.emotion_data

    def update_emotion_state(self, emotion_delta: Dict[str, Any]):
        """LLM 분석 결과 수치를 기존 감정 상태에 점진적으로 누적 반영"""
        if not emotion_delta:
            return

        # 1. 주 감정 키워드 갱신
        self.emotion_data["emotion"] = emotion_delta.get("emotion", self.emotion_data["emotion"])

        # 2. 스트레스 지수 변화량 반영 (0~100 경계 제한)
        stress_delta = emotion_delta.get("stress_delta", 0)
        new_stress = self.emotion_data["stress"] + stress_delta
        self.emotion_data["stress"] = max(0, min(100, new_stress))

        # 3. 신뢰도 지수 변화량 반영 (0~100 경계 제한)
        trust_delta = emotion_delta.get("trust_delta", 0)
        new_trust = self.emotion_data["trust"] + trust_delta
        self.emotion_data["trust"] = max(0, min(100, new_trust))

        self.save_emotion()
        print(f"🎭 [감정 트래커 업데이트] 감정: {self.emotion_data['emotion']} | 스트레스: {self.emotion_data['stress']} | 신뢰도: {self.emotion_data['trust']}")