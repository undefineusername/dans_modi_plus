import json
import os
import requests

GROQ_API_KEY = ""
MODEL_NAME = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_FILE = os.path.join(BASE_DIR, "my_memory.json")

# ==========================================
# 1. 비서가 호출할 로컬 기억 저장 함수
# ==========================================
def save_user_info(key: str, value: str) -> str:
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)
    else:
        memory = {}

    memory[key] = value

    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)
        
    return f"성공적으로 로컬 기억장치에 저장됨: [{key}] -> {value}"

# ==========================================
# 2. 기존 기억 불러오기 및 시스템 지침 정의
# ==========================================
current_memory = "{}"
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        current_memory = f.read()

system_prompt = f"""
너는 유저의 아주 유능한 하드웨어/소프트웨어 개발 전용 AI 비서다.
유저가 앞으로 대화에 참고할 만한 중요한 정보(새로운 프로젝트 이름, 현재 자전거 부품 스펙, 수리 결과 등)를 말하면, 
절대 빼놓지 말고 즉시 'save_user_info' 함수를 호출하여 로컬에 저장해라.
유저가 직접 "기억해줘"라고 하지 않아도 눈치껏 저장해야 한다.

[중요] 함수를 호출해 저장을 완료한 후에는, 유저에게 저장했다는 사실과 함께 유저가 좋아할 만한 친절하고 명확한 대답을 돌려주어야 한다.

[현재 기억하고 있는 유저 정보]
{current_memory}
"""

# ==========================================
# 3. Groq API 호출 및 연속 대화 턴 처리 루프
# ==========================================
def talk_to_groq_with_memory(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "tools": [{
            "type": "function",
            "function": {
                "name": "save_user_info",
                "description": "유저의 중요한 개인 정보, 설정, 상태, 관심사 등을 기억장치에 저장합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "정보 카테고리 (예: '프로젝트_이름')"},
                        "value": {"type": "string", "description": "기억해야 할 구체적인 내용"}
                    },
                    "required": ["key", "value"]
                }
            }
        }]
    }

    # 대화 턴이 완전히 끝날 때까지 도는 루프
    while True:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        
        try:
            message = res_json['choices'][0]['message']
            tool_calls = message.get('tool_calls')
        except (KeyError, IndexError):
            return f"❌ 서버 에러 발생: {res_json}"
            
        # AI가 함수(기억하기)를 호출한 경우
        if tool_calls:
            tool_call = tool_calls[0]
            func_name = tool_call['function']['name']
            args = json.loads(tool_call['function']['arguments'])
            
            if func_name == "save_user_info":
                print(f"💾 (비서가 기억하는 중...) -> 키: {args['key']}, 값: {args['value']}")
                result_msg = save_user_info(args['key'], args['value'])
                
                # 턴을 이어가기 위해 메시지 히스토리에 'AI의 툴 요청'과 '코드가 실행한 툴 결과'를 둘 다 박아줍니다.
                payload['messages'].append(message)
                payload['messages'].append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "name": func_name,
                    "content": result_msg
                })
                
                # 💡 핵심: 툴 결과를 들고 'continue'로 루프를 다시 돌아 Groq에게 최종 대답 문장을 받아옵니다!
                continue
                
        # 툴 호출이 없거나, 툴 결과를 반영한 최종 대답 문장이 나온 경우 리턴
        return message['content']

# ==========================================
# 4. 실행 테스트
# ==========================================
if __name__ == "__main__":
    print("🤖 기억과 대답을 동시에 하는 Groq 개발 비서 가동\n")
    
    msg = "내가 전에 너한테 말헀던게 뭐가있었지?"
    print(f"유저: {msg}")
    
    answer = talk_to_groq_with_memory(msg)
    print(f"\n비서:\n{answer}")