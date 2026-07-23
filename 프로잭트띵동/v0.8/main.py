import time
import os
import json
import random
import requests
import modi_plus
from gtts import gTTS
import pygame

# ==========================================
# 1. 설정 및 API 키 정의
# ==========================================
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"  # 실제 API 키 입력
MODEL_NAME = "llama-3.1-8b-instant"
refresh_time = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_FILE = os.path.join(BASE_DIR, "my_memory.json")
CONVERSATION_FILE = os.path.join(BASE_DIR, "conversation.json")

# ==========================================
# 2. 로컬 기억 저장 및 대사 로드 함수
# ==========================================
def save_user_info(key: str, value: str) -> str:
    """AI가 툴 호출을 통해 중요한 유저 정보를 저장하는 함수"""
    memory = {}
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
        except Exception:
            memory = {}

    memory[key] = value

    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)
        
    return f"성공적으로 로컬 기억장치에 저장됨: [{key}] -> {value}"

def load_current_memory():
    """저장된 유저 기억을 문자열로 반환"""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "{}"

def load_dialogue():
    fallback = {
        "bother_ments": ["저기요?", "계세요?", "거기 누구 없나요?", "일로 와보세요.", "심심해요."],
        "come_closer": ["앞으로 오세요."],
        "hello": ["오늘 기분은 어떤가요?"],
        "save_success": ["점 저장 완료."]
    }
    try:
        json_path = os.path.join(BASE_DIR, "dialogue.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in data:
                    if isinstance(data[key], str):
                        data[key] = [data[key]]
                return data
    except Exception as e:
        print(f"[경고] JSON 로드 실패, 예비 멘트 사용: {e}")
    return fallback

dialogue = load_dialogue()

def save_counseling_session(mood, mode_id, mode_name, ai_response):
    """상담 이력을 conversation.json에 기록"""
    try:
        history = []
        if os.path.exists(CONVERSATION_FILE):
            with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []

        session_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "mood_score": mood,
            "selected_mode_id": mode_id,
            "selected_mode_name": mode_name,
            "ai_response": ai_response
        }
        
        history.append(session_data)
        with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"세션 저장 오류: {e}")

# ==========================================
# 3. Groq API 대화 및 Tool Calling 연동
# ==========================================
def get_system_prompt_by_mode(mode_id, mood_score):
    user_memory = load_current_memory()
    
    base_instruction = f"""
너는 MODI+ 기반의 청소년 전용 심리상담 AI 로봇 'MindMODI'다.
상담을 진행하며 유저가 언급한 중요 인물, 관계, 주요 사건, 감정 패턴, 선호사항이 있다면 절대 놓치지 말고 즉시 'save_user_info' 함수를 호출하여 저장해라.
유저가 직접 "기억해줘"라고 하지 않아도 상담에 중요한 핵심 키워드는 스스로 알아서 저장해야 한다.
청소년 사용자가 쉽게 이해하고 위안을 얻을 수 있도록 친근한 존댓말(~해요, ~했구나)로 2~3문장 이내로 짧고 명확하게 말해라.

[현재 기억된 유저 정보]
{user_memory}

[현재 유저의 기분 점수]: {mood_score}점 (100점 만점)
"""

    if mode_id == 0:  # 일반 상담
        return base_instruction + "\n[모드]: 일반 상담 모드. 유저의 이야기를 따뜻하게 들어주고 공감해라."
    elif mode_id == 1:  # 심화 상담
        return base_instruction + "\n[모드]: 심화 상담 모드. 객관적 '사건'과 주관적 '감정'을 분리하여 유저가 스스로 문제를 인지할 수 있도록 돕는 질문을 해라."
    elif mode_id == 2:  # 생활 상담
        return base_instruction + "\n[모드]: 생활 상담 모드. 수면, 활동, 방 안 환경(조도/온습도 등)과 심리 상태의 연결고리를 짚어주며 습관 케어를 해라."
    elif mode_id == 3:  # 솔루션 상담
        return base_instruction + "\n[모드]: 솔루션 상담 모드. 거창하지 않고 지금 당장 실천할 수 있는 작고 구체적인 1가지 행동 지침을 제시해라."
    return base_instruction

def talk_to_groq_counselor(user_text, mode_id, mood_score):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = get_system_prompt_by_mode(mode_id, mood_score)
    
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
                "description": "유저의 중요 개인 정보, 인물 관계, 고민, 생활 패턴을 기억장치에 저장합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "정보 카테고리 (예: '고민_원인', '친구_이름')"},
                        "value": {"type": "string", "description": "기억해야 할 구체적 내용"}
                    },
                    "required": ["key", "value"]
                }
            }
        }]
    }

    while True:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            res_json = response.json()
            message = res_json['choices'][0]['message']
            tool_calls = message.get('tool_calls')
            
            # AI가 기억 저장을 결정한 경우 (Tool Call)
            if tool_calls:
                tool_call = tool_calls[0]
                func_name = tool_call['function']['name']
                args = json.loads(tool_call['function']['arguments'])
                
                if func_name == "save_user_info":
                    print(f"\n💾 (MindMODI 기억 저장 중...) -> [{args['key']}]: {args['value']}")
                    result_msg = save_user_info(args['key'], args['value'])
                    
                    payload['messages'].append(message)
                    payload['messages'].append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "name": func_name,
                        "content": result_msg
                    })
                    continue  # 툴 결과를 반영하여 최종 응답 문장 재요청
                    
            return message.get('content', '죄송해요, 다시 말씀해 주시겠어요?')
            
        except Exception as e:
            print(f"Groq API 오류: {e}")
            return "잠시 대화 시스템에 연결이 원활하지 않아요. 마음을 조금 가라앉히고 다시 이야기해요."

# ==========================================
# 4. MODI+ 하드웨어 제어 및 출력
# ==========================================
def announce(hw, text, is_tts=True):
    print(f"\n[MindMODI] {text}")
    if hw["display"]:
        hw["display"].text = text[:30]  # Display 길이 제한 방지
        
    if is_tts:
        try:
            tts = gTTS(text=text, lang='ko', slow=False) 
            filename = f"temp_{int(time.time() * 1000)}.mp3"
            tts.save(filename)
            
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): 
                time.sleep(0.05)
                
            pygame.mixer.music.unload()
            if os.path.exists(filename): 
                os.remove(filename)
        except Exception as e:
            print(f"TTS Error: {e}")

def play_beep_three_times(hw):
    if hw["speaker"]:
        for _ in range(3):
            hw["speaker"].tune = (523, 30)  
            time.sleep(0.08)                
            hw["speaker"].reset()           
            time.sleep(0.05)                

def connect_modules():
    print("Connecting MODI+ Modules...")
    bundle = modi_plus.MODIPlus()
    return {
        "speaker": bundle.speakers[0] if bundle.speakers else None,
        "display": bundle.displays[0] if bundle.displays else None,
        "led": bundle.leds[0] if bundle.leds else None,
        "button": bundle.buttons[0] if bundle.buttons else None,
        "dial": bundle.dials[0] if bundle.dials else None,
        "tof": bundle.tofs[0] if bundle.tofs else None,
        "imu": bundle.imus[0] if bundle.imus else None,
    }

def startup(hw):
    if hw["led"]: hw["led"].rgb = (0, 0, 255)  
    play_beep_three_times(hw)
    start_ment = random.choice(dialogue["bother_ments"])
    announce(hw, start_ment)
    time.sleep(1)

def wait_motion_with_bother(hw):
    if not hw["imu"]: return
    if hw["display"]: hw["display"].text = "대기 중..."
    if hw["led"]: hw["led"].rgb = (0, 0, 255)  

    last_bother_time = time.time()
    motion_count = 0

    while True:
        movement = abs(hw["imu"].angular_vel_x) + abs(hw["imu"].angular_vel_y) + abs(hw["imu"].angular_vel_z)
        print(f"Movement : {movement:.1f} (Count: {motion_count})      ", end="\r")

        if movement > 5:   
            motion_count += 1
        else:
            motion_count = 0

        if motion_count >= 3:
            if hw["led"]: hw["led"].rgb = (255, 255, 0)  
            come_closer_ment = random.choice(dialogue["come_closer"])
            announce(hw, come_closer_ment)
            return

        if time.time() - last_bother_time > 4.0:
            bother_ment = random.choice(dialogue["bother_ments"])
            announce(hw, bother_ment)
            if hw["display"]: hw["display"].text = "대기 중..."
            last_bother_time = time.time()
            motion_count = 0

        time.sleep(0.05)

def wait_user(hw):
    if not hw["tof"]: return
    print("Waiting user...")
    tof_count = 0
    
    while True:
        distance = hw["tof"].distance
        if 2 < distance < 30:
            tof_count += 1
        else:
            tof_count = 0
            
        if tof_count >= 3:
            if hw["led"]: hw["led"].rgb = (0, 255, 0)  
            hello_ment = random.choice(dialogue["hello"])
            announce(hw, hello_ment)
            return
        time.sleep(0.05)

def input_mood(hw):
    if not hw["dial"] or not hw["button"]: return 50
    if hw["display"]: hw["display"].text = "오늘의 기분은?"
    while True:
        mood = min(int(hw["dial"].turn), 100)
        score_text = f"현재 점수 : {mood}"
        print(f"[MindMODI] {score_text}      ", end="\r")
        if hw["display"]: hw["display"].text = score_text
        if hw["led"]: hw["led"].rgb = (255, 0, 0)  
        
        if hw["button"].pressed:
            while hw["button"].pressed: time.sleep(0.01)
            return mood
        time.sleep(0.05)

def select_mode(hw):
    """다이얼로 상담 모드 선택 (0:일반, 1:심화, 2:생활, 3:솔루션)"""
    modes = {
        0: ("일반 상담", (255, 255, 255)),
        1: ("심화 상담", (255, 0, 255)),
        2: ("생활 상담", (0, 255, 255)),
        3: ("솔루션 상담", (255, 255, 0))
    }
    
    announce(hw, "다이얼을 돌려 모드를 선택하고 버튼을 누르세요.")
    
    last_selected = -1
    while True:
        dial_val = min(int(hw["dial"].turn), 100) if hw["dial"] else 0
        mode_idx = min(dial_val // 25, 3)
        mode_name, color = modes[mode_idx]
        
        if mode_idx != last_selected:
            display_text = f"모드: {mode_idx}.{mode_name}"
            print(f"[MindMODI] {display_text}      ", end="\r")
            if hw["display"]: hw["display"].text = display_text
            if hw["led"]: hw["led"].rgb = color
            last_selected = mode_idx
            
        if hw["button"] and hw["button"].pressed:
            while hw["button"].pressed: time.sleep(0.01)
            announce(hw, f"{mode_name}을 시작합니다.")
            return mode_idx, mode_name
            
        time.sleep(0.05)

# ==========================================
# 5. Main 실행 루프
# ==========================================
def main():
    pygame.mixer.init()
    hw = connect_modules()
    startup(hw)
    
    try:
        while True:
            # 1. 사용자 감지
            wait_motion_with_bother(hw)  
            wait_user(hw)                
            
            # 2. 기분 점수 입력
            mood = input_mood(hw)        
            
            # 3. 상담 모드 선택
            mode_id, mode_name = select_mode(hw)
            
            # 4. 콘솔 입력 또는 STT를 통한 유저 대화 전달 (테스트용 input)
            user_input = input("\n[유저 발화 입력 (음성/텍스트)]: ")
            if not user_input.strip():
                user_input = f"오늘 기분 점수는 {mood}점이야. 대화를 시작하고 싶어."

            # 5. Groq AI 상담 대화 실행 (Tool Calling 자동 작동)
            ai_response = talk_to_groq_counselor(user_input, mode_id, mood)
            
            # 6. AI 답변 TTS 출력
            announce(hw, ai_response)
            
            # 7. 세션 데이터 저장
            save_counseling_session(mood, mode_id, mode_name, ai_response)
            
            if hw["speaker"]: hw["speaker"].reset()
            
            # 8. 재시작 카운트다운
            print("") 
            for i in range(refresh_time, 0, -1):
                print(f"[MindMODI] {i}초 뒤 재시작      ", end="\r")
                if hw["display"]: hw["display"].text = f"{i}초 뒤 재시작"
                time.sleep(1)
            print("") 
                
            if hw["led"]: hw["led"].rgb = (0, 0, 255)  
            play_beep_three_times(hw)
            
    except KeyboardInterrupt:
        if hw["display"]: hw["display"].reset()
        if hw["led"]: hw["led"].turn_off()
        print("\n[MindMODI] 안전하게 종료되었습니다.")
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    main()