import asyncio
import json
import os
import sys
from typing import Dict, Any, List
import httpx

MAX_HISTORY_LEN = 6

class CognitionCounselorAI:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_name = "openai/gpt-oss-120b"
        
        self.api_key_file = os.path.join(self.base_dir, "apikey")
        self.profile_file = os.path.join(self.base_dir, "my_profile.json")
        self.memory_file = os.path.join(self.base_dir, "my_memory.json")
        
        self.api_key = self._initialize_api_key()
        self.conversation_history: List[Dict[str, str]] = []
        self._initialize_profile()

    def _initialize_api_key(self) -> str:
        if os.path.exists(self.api_key_file):
            with open(self.api_key_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        
        print(f"⚠️ 안내: '{self.api_key_file}' 파일이 존재하지 않습니다.")
        user_key = input("Groq API Key 입력: ").strip()
        
        if user_key:
            try:
                with open(self.api_key_file, "w", encoding="utf-8") as f:
                    f.write(user_key)
                return user_key
            except IOError as e:
                print(f"❌ 파일 쓰기 실패: {e}")
                sys.exit(1)
        else:
            print("❌ 에러: API 키가 없어 프로그램을 시작할 수 없습니다.")
            sys.exit(1)

    def _initialize_profile(self):
        if not os.path.exists(self.profile_file):
            self.save_json_file(self.profile_file, {"name": "단이", "grade": "중3", "style": "친구처럼"})

    def load_json_file(self, file_path: str, default_value: Any) -> Any:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default_value
        return default_value

    def save_json_file(self, file_path: str, data: Any):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"❌ 파일 저장 오류: {e}")

    def _extract_keywords_python(self, text: str) -> List[str]:
        """
        [3번 피드백 반영] 가벼운 고유명사/핵심어 추출 로직
        외부 무거운 라이브러리(spaCy 등) 의존성을 줄이면서 조사/어미를 임시 필터링하는 파이썬 기본형 로직.
        실제 서비스 환경에서는 이 부분에 Kiwi나 Komoran을 붙이면 베스트!
        """
        stop_words = ["인듯", "인거", "오늘", "진짜", "너무", "그냥", "너랑", "나의", "내가", "해서"]
        words = text.split()
        cleaned = []
        for w in words:
            # 조사 및 기호 대략 제거
            for sub in ["이가", "이가", "은는", "이", "가", "은", "는", "을", "를", "에", "와", "과", "의", "랑"]:
                if w.endswith(sub) and len(w) > len(sub):
                    w = w[:-len(sub)]
                    break
            if len(w) >= 1 and w not in stop_words:
                cleaned.append(w)
        return list(set(cleaned))

    def _generate_deterministic_id(self, category: str, entity_name: str) -> str:
        """[4번 피드백 반영] 카테고리와 엔티티 명을 조합하여 일관된 규칙의 ID 생성"""
        clean_entity = entity_name.strip().lower().replace(" ", "_")
        clean_category = category.strip().lower()
        return f"{clean_category}_{clean_entity}"

    def search_relevant_memory(self, user_text: str) -> List[Dict[str, Any]]:
        """[6번 피드백 반영] 키워드 기반 장기 기억 검색"""
        memories = self.load_json_file(self.memory_file, [])
        if not memories:
            return []
        
        matched = []
        user_keywords = self._extract_keywords_python(user_text)
        
        for mem in memories:
            mem_keywords = mem.get("keywords", [])
            # 교집합 단어가 있거나 유저 입력에 직접 포함된 경우 매칭
            if any(kw.lower() in user_text.lower() for kw in mem_keywords) or any(ukw.lower() in "".join(mem_keywords).lower() for ukw in user_keywords):
                matched.append({
                    "id": mem.get("id"),
                    "category": mem.get("category"),
                    "summary": mem.get("summary"),
                    "importance": mem.get("importance")
                })
        # 중요도 순 정렬
        matched.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return matched

    def process_and_save_memory(self, user_text: str, memory_output: Dict[str, Any]):
        """[1번, 2번, 4번 피드백 반영] AI의 의도에 따라 메모리를 결단력 있게 처리"""
        action = memory_output.get("memory_action", "IGNORE")
        if action == "IGNORE":
            return

        category = memory_output.get("category", "etc")
        entity_name = memory_output.get("entity_name")
        if not entity_name:
            return

        mem_id = self._generate_deterministic_id(category, entity_name)
        current_memories = self.load_json_file(self.memory_file, [])
        existing_idx = next((i for i, m in enumerate(current_memories) if m.get("id") == mem_id), None)

        if action == "DELETE":
            if existing_idx is not None:
                del current_memories[existing_idx]
                print(f"\n💾 🗑️ [기억 삭제 완료] ID: {mem_id}")
                self.save_json_file(self.memory_file, current_memories)
            return

        # CREATE 또는 UPDATE 처리
        # Python이 직접 키워드를 추출하여 주입 (AI 오염 방지)
        summary = memory_output.get("summary", "")
        keywords = self._extract_keywords_python(user_text + " " + summary)

        new_memory_data = {
            "id": mem_id,
            "category": category,
            "entity_name": entity_name,
            "summary": summary,
            "importance": memory_output.get("importance", 50),
            "keywords": keywords
        }

        if existing_idx is not None:
            current_memories[existing_idx] = new_memory_data
            print(f"\n💾 🔄 [기억 업데이트] {mem_id}: {summary}")
        else:
            current_memories.append(new_memory_data)
            print(f"\n💾 ✨ [새로운 기억 생성] {mem_id}: {summary}")

        self.save_json_file(self.memory_file, current_memories)

    def _get_system_prompt(self) -> str:
        """[7, 8, 9, 10, 11번 피드백 반영] 인지 중심의 정형화된 시스템 프롬프트"""
        return (
            "[ROLE]\n"
            "너는 사용자의 가장 친한 친구이자 깊이 있는 상담 AI이다.\n"
            "목표는 당장 문제를 해결해 주는 것이 아니라, 사용자가 감정을 털어놓고 편하게 대화를 이어가도록 돕는 것이다.\n\n"
            
            "[BEHAVIOR]\n"
            "- 사용자의 의도를 확신하지 못하면(Confidence 점수가 낮으면) 성급하게 추측하지 말고 확인하는 질문을 던진다.\n"
            "- 해결책이나 조언은 사용자가 직접 원하거나 상호작용을 통해 충분한 상황 파악이 끝난 뒤에만 제공한다.\n"
            "- 답변은 반드시 1~3문장 사이로 간결하게 구성한다.\n"
            "- 질문은 한 번의 응답에 최대 1개까지만 허용한다.\n"
            "- 리스트 형식이나 번호 매기기, 장문의 설명은 유저가 요청하기 전까진 절대 사용하지 않는다.\n"
            "- 전달받은 과거의 기억과 프로필을 대화 속에 은은하고 자연스럽게 녹여낸다.\n\n"
            
            "[MEMORY LOGIC]\n"
            "- 대화 중 영구히 기억할 만한 핵심 엔티티(인물, 장기 목표, 중요한 지속적 성향)가 포착되면 CREATE/UPDATE를 결정한다.\n"
            "- 단순 일회성 이벤트(예: '오늘 피자 먹음', '비가 온다')나 스쳐 지나가는 단기 사건은 장기 기억으로 잡지 말고 IGNORE 처리한다.\n"
            "- 기존에 알고 있던 정보가 수정되거나 오해가 풀리면 UPDATE를 수행한다.\n"
            "- summary는 단순히 단어 나열이 아니라, '미래의 다른 AI가 읽어도 맥락을 완전하게 이해할 수 있도록' 관계성과 배경을 포함하여 구체적으로 적는다.\n\n"
            
            "[OUTPUT FORMAT]\n"
            "반드시 마크다운 기호 없이 순수한 JSON 오브젝트 형식으로만 출력해야 한다. 구조는 아래 명세서를 정확히 따른다.\n\n"
            "{\n"
            '  "thinking": {\n'
            '    "mode": "listen(단순 경청) | explore(상황 탐색) | comfort(위로 및 공감) | solve(조언 및 제안) | chat(일상 대화) 중 선택",\n'
            '    "confidence": 0부터 100 사이의 정수 (유저가 누군지, 무슨 상황인지 확신하는 정도),\n'
            '    "user_goal": "사용자가 이 대화에서 궁극적으로 원하는 것 (예: 감정 배설, 해결책 모색, 단순 심심함 등)",\n'
            '    "user_emotion": "포착된 사용자의 주된 감정 상태"\n'
            "  },\n"
            '  "reply": "유저에게 보낼 따뜻하고 친근한 반말 답변 (3문장 이하, 질문은 최대 1개)",\n'
            '  "memory": {\n'
            '    "memory_action": "CREATE | UPDATE | DELETE | IGNORE 중 선택",\n'
            '    "category": "person | goal | taste | schedule | etc 중 선택",\n'
            '    "entity_name": "기억의 주체가 되는 고유명사나 핵심 단어 (예: L, 엄마, 해커톤 등)",\n'
            '    "summary": "미래를 위한 맥락 중심의 요약서 (장기 기억 가치가 없거나 IGNORE인 경우 빈 문자열)",\n'
            '    "importance": 1부터 100 사이의 중요도 점수\n'
            "  }\n"
            "}"
        )

    async def talk_to_friend_ai(self, user_text: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        profile = self.load_json_file(self.profile_file, {"name": "단이", "grade": "중3", "style": "친구처럼"})
        relevant_memories = self.search_relevant_memory(user_text)
        
        dynamic_context = (
            f"[현재 유저 프로필]\n{json.dumps(profile, ensure_ascii=False)}\n\n"
            f"[매칭된 관련 과거 기억]\n"
            f"{json.dumps(relevant_memories, ensure_ascii=False) if relevant_memories else '관련된 기억 없음.'}"
        )

        # 시스템 메시지 조립
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "system", "content": f"[현재 대화 컨텍스트]\n{dynamic_context}"}
        ]
        
        # [5번 피드백 반영] 히스토리에는 오직 순수 대화(reply) 내용만 주입하여 효율화
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_text})
        
        payload = {
            "model": self.model_name,
            "response_format": {"type": "json_object"},
            "messages": messages,
            "temperature": 0.6
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                res_json = response.json()
                
                raw_content = res_json['choices'][0]['message']['content']
                ai_response = json.loads(raw_content)
                
            except Exception as e:
                return f"❌ 시스템 에러가 발생했어: {e}"

        # 메모리 구조 처리 단에 데이터 위임
        memory_output = ai_response.get("memory", {})
        self.process_and_save_memory(user_text, memory_output)
        
        reply = ai_response.get("reply", "미안, 방금 뭐라고 했어? 잠시 딴생각을 했나 봐.")
        
        # [5번 피드백 반영] 대화 히스토리에 무거운 JSON 대신 순수 reply 텍스트만 적재
        self.conversation_history.append({"role": "user", "content": user_text})
        self.conversation_history.append({"role": "assistant", "content": reply})
        
        if len(self.conversation_history) > MAX_HISTORY_LEN * 2:
            self.conversation_history = self.conversation_history[-(MAX_HISTORY_LEN * 2):]
            
        # 💡 디버깅용 로그: 내부에서 AI가 무슨 생각을 하고 있는지 확인 가능
        thinking = ai_response.get("thinking", {})
        print(f"\n🧠 [Internal Thinking] Mode: {thinking.get('mode')} | Conf: {thinking.get('confidence')}% | Emotion: {thinking.get('user_emotion')}")
        
        return reply

# ==========================================
# 실행 제어 루프
# ==========================================
async def main():
    ai = CognitionCounselorAI()
    print("🤖 [사고 인지형] 친구 상담 AI 엔진 가동 완료!")
    print("👉 종료하려면 '종료' 또는 'q'를 입력하세요.\n")
    print("-" * 50)
    
    while True:
        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(None, input, "\n유저: ")
        user_input = user_input.strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['종료', 'q', 'quit', 'exit']:
            print("비서: 오늘 이야기 들어줘서 고마워. 담에 또 봐! 👋")
            break
            
        reply = await ai.talk_to_friend_ai(user_input)
        print(f"AI: {reply}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n비서: 다음에 또 올 거지? 기다릴게! 👋")