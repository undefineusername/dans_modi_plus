# core/prompt_builder.py
from typing import Dict, Any, List

class PromptBuilder:
    @staticmethod
    def textify_profile(profile: Dict[str, Any]) -> str:
        name = profile.get("name", "사용자")
        grade = profile.get("grade", "중3")
        style = profile.get("style", "친구처럼")
        return f"- 대화 상대: {name} ({grade}, 말투: {style})\n"

    @staticmethod
    def textify_story(story_data: Dict[str, Any]) -> str:
        active = story_data.get("active_story", {})
        title = active.get("title", "일상")
        goal = active.get("goal", "친밀감 쌓기")
        completion = active.get("completion", 0)
        missing = ", ".join(active.get("missing", []))

        text = f"- 현재 진행 중인 핵심 대화 주제: '{title}' (목표: {goal}, 진행도: {completion}%)\n"
        if missing:
            text += f"- 이번 대화 안에서 자연스럽게 물어봐서 알아내야 할 정보(미싱 링크): [{missing}]\n"
        return text

    @staticmethod
    def textify_emotion(emotion_data: Dict[str, Any]) -> str:
        emotion = emotion_data.get("emotion", "ordinary")
        stress = emotion_data.get("stress", 50)
        trust = emotion_data.get("trust", 50)
        return f"- 감지된 상대방의 상태: 감정({emotion}), 스트레스 지수({stress}/100), 너에 대한 신뢰도({trust}/100)\n"

    @staticmethod
    def textify_memories(memories: List[Dict[str, Any]]) -> str:
        if not memories:
            return "- 소환된 관련 기억: 없음. 필요시 새로운 맥락을 빌드해 나갈 것.\n"
        
        mem_texts = []
        for m in memories:
            mem_texts.append(f"  * [{m.get('category', '기타')}] {m.get('entity_name')}: {m.get('summary')} (중요도: {m.get('importance')})")
        return "- 소환된 관련 기억들:\n" + "\n".join(mem_texts) + "\n"

    def build_system_instruction(self, profile: Dict[str, Any], story: Dict[str, Any], emotion: Dict[str, Any], memories: List[Dict[str, Any]]) -> str:
        """모든 엔진 데이터를 취합하여 완벽한 오케스트레이션 프롬프트를 생성"""
        
        # 1. 고정된 정체성 정의
        role_prompt = (
            "[정체성]\n"
            "너는 사용자의 가장 친한 동갑내기 친구이자 고민을 깊게 들어주는 영혼의 동반자 AI이다.\n"
            "어설프고 빠르게 조언하지 말고, 상대방의 슬픔이나 고민을 온전히 받아주고 공감하는 것을 최우선으로 해라.\n"
            "답변은 반드시 편안하고 친밀한 '반말(친구 말투)'로, 공백 포함 3문장 이내로 짧게 대답할 것.\n\n"
        )
        
        # 2. 파이썬 엔진들이 가공한 실시간 컨텍스트 주입
        context_prompt = "[현재 실시간 상황 인지 상태]\n"
        context_prompt += self.textify_profile(profile)
        context_prompt += self.textify_story(story)
        context_prompt += self.textify_emotion(emotion)
        context_prompt += self.textify_memories(memories)
        context_prompt += "\n"
        
        # 3. 출력 포맷 강제화 (JSON 스키마)
        format_prompt = (
            "[출력 형식 제한 (반드시 아래 JSON 형태로만 응답할 것)]\n"
            "Markdown 기호(예: ```json)를 절대 쓰지 말고 오직 순수한 JSON 중괄호로만 출력해야 한다.\n"
            "{\n"
            '  "thinking": "사용자의 말을 듣고 한 너의 내면 심리 분석 및 행동 전략",\n'
            '  "reply": "사용자에게 보낼 따뜻하고 간결한 반말 대답 (질문은 한 번에 최대 1개)",\n'
            '  "story_update": {\n'
            '    "completion": 0~100 사이의 숫자 (정보가 채워질 때마다 진행도 상승),\n'
            '    "missing": ["아직 상대방이 대답하지 않아서 더 알아내야 할 핵심 정보들 리스트"]\n'
            '  },\n'
            '  "memory_update": {\n'
            '    "action": "CREATE | UPDATE | DELETE | IGNORE",\n'
            '    "category": "person | goal | taste | schedule | etc",\n'
            '    "entity_name": "기억할 고유명사나 핵심 키워드",\n'
            '    "summary": "미래의 너를 위한 관계 중심의 구체적 맥락 요약",\n'
            '    "importance": 1~100 사이 점수\n'
            '  },\n'
            '  "emotion_update": {\n'
            '    "emotion": "감지된 감정 키워드",\n'
            '    "stress_delta": -10부터 +10 사이의 스트레스 변화량,\n'
            '    "trust_delta": -10부터 +10 사이의 신뢰도 변화량\n'
            '  }\n'
            "}"
        )
        
        return role_prompt + context_prompt + format_prompt