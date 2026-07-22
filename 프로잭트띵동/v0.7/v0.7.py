import time
import os
import json
import random
from datetime import datetime
import modi_plus
from gtts import gTTS
import pygame

# AI 모듈 불러오기
from ai import AIChatSession

refresh_time = 200

def load_dialogue():
    fallback = {
        "bother_ments": ["저기요?", "계세요?", "거기 누구 없나요?", "일로 와보세요.", "심심해요."],
        "come_closer": ["앞으로 오세요."],
        "hello": ["오늘 기분은 어떤가요?"],
        "save_success": ["점 저장 완료."]
    }
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "dialogue.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in data:
                    if isinstance(data[key], str):
                        data[key] = [data[key]]
                return data
    except Exception as e:
        print(f"[경고] JSON 로드 실패, 예비 멘트를 사용합니다: {e}")
    return fallback

dialogue = load_dialogue()

def announce(hw, text, is_tts=True):
    print(f"\n[MindMODI] {text}")
    if hw["display"]:
        hw["display"].text = text
        
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
    print("Connecting...")
    bundle = modi_plus.MODIPlus()
    time.sleep(2)
    return {
        "speaker": bundle.sdpeakers[0] if bundle.speakers else None,
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
    if not hw["dial"] or not hw["button"]: return 0
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

def save_mood(hw, mood):
    if hw["led"]: hw["led"].rgb = (0, 255, 0)  
    success_ment = random.choice(dialogue["save_success"])
    
    if success_ment.startswith("점"):
        save_text = f"{mood}{success_ment}"
    else:
        save_text = f"{mood}점, {success_ment}"
        
    announce(hw, save_text)
    time.sleep(1)

# ==========================================
# AI 대화 루프 연동 함수
# ==========================================
def run_ai_conversation(hw, mood):
    """기분 입력 후 AI와의 대화를 진행하는 함수"""
    ai_session = AIChatSession()
    
    # 1. 확장 가능한 Context 생성
    context = {
        "mood": mood,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # 필요 시 센서 데이터 추가 가능 (예: "temperature": hw["env"].temperature)
    }
    
    system_prompt = ai_session.start_session(context)
    
    # 2. 첫 AI 안내 멘트 출력 (선택 사항)
    initial_prompt = f"오늘 기분 점수가 {mood}점이구나! 무슨 일 있었어?"
    announce(hw, initial_prompt)

    # 3. 콘솔 대화 루프 (종료 시 'exit' 입력)
    while True:
        try:
            user_input = input("\n[사용자 입력 (종료: exit)] : ").strip()
            
            if not user_input or user_input.lower() in ["exit", "종료", "끝"]:
                announce(hw, "대화를 종료할게. 오늘 하루도 수고했어!")
                break
                
            # AI 답변 생성 및 출력 (TTS 포함)
            response = ai_session.chat(user_input, system_prompt)
            announce(hw, response)
            
        except KeyboardInterrupt:
            break

# ==========================================
# Main
# ==========================================
def main():
    pygame.mixer.init()
    
    hw = connect_modules()
    startup(hw)
    try:
        while True:
            wait_motion_with_bother(hw)  
            wait_user(hw)                
            mood = input_mood(hw)        
            save_mood(hw, mood)   
            
            # --- AI 상담 시작 ---
            run_ai_conversation(hw, mood)
            # --------------------
            
            if hw["speaker"]: hw["speaker"].reset()
            
            print("") 
            for i in range(refresh_time, 0, -1):
                countdown_text = f"{i}초 뒤 재시작"
                print(f"[MindMODI] {countdown_text}      ", end="\r")
                if hw["display"]: hw["display"].text = f"{i}초 뒤 재시작"
                time.sleep(1)
            print("") 
                
            if hw["led"]: hw["led"].rgb = (0, 0, 255)  
            play_beep_three_times(hw)
            
    except KeyboardInterrupt:
        if hw["display"]: hw["display"].reset()
        if hw["led"]: hw["led"].turn_off()
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    main()