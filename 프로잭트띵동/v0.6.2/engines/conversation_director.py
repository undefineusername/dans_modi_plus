# engines/conversation_director.py
from typing import Dict, Any

class ConversationDirector:
    def __init__(self):
        pass

    def evaluate_turn(self, user_text: str, current_story: Dict[str, Any], last_thinking: Dict[str, Any]) -> Dict[str, Any]:
        """
        LLM이 답변을 만들기 전에, 이전 맥락과 유저 입력을 분석하여 
        이번 턴에 수행해야 할 '대화 행동 가이드라인'을 결정하는 규칙 기반 및 메타 분석기.
        """
        user_len = len(user_text)
        
        # 1. 주제 전환 감지 논리 (유저가 "근데", "맞다 그리고", "시험은" 등 화제를 돌릴 때)
        should_change_topic = False
        change_reason = ""
        
        transition_keywords = ["근데", "그건 그렇고", "딴얘기인데", "아 맞다", "시험", "학원", "엄마"]
        if any(kw in user_text for kw in transition_keywords) and current_story.get("title") != "일상":
            # 현재 대화 주제와 다른 키워드가 들어오면 일시 일시정지 유도
            should_change_topic = True
            change_reason = "사용자가 명시적/암묵적으로 새로운 화제를 꺼냄"

        # 2. 대화 액션 결정 (공감 40%, 질문 40%, 의견 20% 황금 비율 강제화)
        # 이전 턴에 질문을 던졌다면, 이번에는 질문하지 않고 공감과 의견만 주도록 제어
        had_asked_last_turn = last_thinking.get("should_ask", False)
        
        if had_asked_last_turn:
            action = "comfort_or_opinion"  # 질문 금지, 공감/의견 제시 턴
            should_ask = False
        else:
            action = "continue_story"
            should_ask = True if user_len > 5 else False # 유저가 성의 있게 대답할 때만 질문 던지기

        # 3. 신뢰도 및 자신감(Confidence) 점수 계산
        confidence = 95
        if any(pronoun in user_text for pronoun in ["걔", "그 애", "걔네"]):
            confidence = 60

        return {
            "current_story": current_story.get("title", "일상"),
            "action": action,
            "reason": change_reason or "현재 사용자가 일관된 주제로 이야기 중",
            "should_change_topic": should_change_topic,
            "should_ask": should_ask,
            "confidence": confidence,
            "reply_length_target": "long" if user_len > 30 else "short" # 유저 길이에 맞춤 (S급 24번 해결)
        }