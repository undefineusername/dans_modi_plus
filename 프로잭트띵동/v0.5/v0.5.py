import time
import os
import json
import random
import modi_plus
from gtts import gTTS
import pygame

refresh_time = 10

# ==========================================
# JSON 대사 데이터 로드 함수
# ==========================================
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

# ==========================================
# 통합 출력 및 TTS 함수 (개선 완료)
# ==========================================
def announce(hw, text, is_tts=True):
    print(f"\n[MindMODI] {text}")
    if hw["display"]:
        hw["display"].text = text
        
    if is_tts:
        try:
            tts = gTTS(text=text, lang='ko', slow=False) 
            
            # 개선 ②: 타임스탬프를 이용해 고유한 파일명 생성 (충돌 방지)
            filename = f"temp_{int(time.time() * 1000)}.mp3"
            tts.save(filename)
            
            # 개선 ①: 오디오 로드 및 재생만 수행 (init/quit 제거로 속도 향상)
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
        "speaker": bundle.speakers[0] if bundle.speakers else None,
        "display": bundle.displays[0] if bundle.displays else None,
        "led": bundle.leds[0] if bundle.leds else None,
        "button": bundle.buttons[0] if bundle.buttons else None,
        "dial": bundle.dials[0] if bundle.dials else None,
        "tof": bundle.tofs[0] if bundle.tofs else None,
        "imu": bundle.imus[0] if bundle.imus else None,
    }

# ==========================================
# 시스템 루프 구조
# ==========================================
def startup(hw):
    if hw["led"]: hw["led"].rgb = (0, 0, 255)  
    play_beep_three_times(hw)
    
    start_ment = random.choice(dialogue["bother_ments"])
    announce(hw, start_ment)
    time.sleep(1)

# 개선 ③: IMU 3회 연속 감지 로직 적용
def wait_motion_with_bother(hw):
    if not hw["imu"]: return
    if hw["display"]: hw["display"].text = "대기  중..."
    if hw["led"]: hw["led"].rgb = (0, 0, 255)  

    last_bother_time = time.time()
    motion_count = 0

    while True:
        movement = abs(hw["imu"].angular_vel_x) + abs(hw["imu"].angular_vel_y) + abs(hw["imu"].angular_vel_z)
        print(f"Movement : {movement:.1f} (Count: {motion_count})      ", end="\r")

        # 3번 연속 감지 체크
        if movement > 5:   
            motion_count += 1
        else:
            motion_count = 0

        if motion_count >= 3:
            if hw["led"]: hw["led"].rgb = (255, 255, 0)  
            come_closer_ment = random.choice(dialogue["come_closer"])
            announce(hw, come_closer_ment)
            return

        # 4초 동안 반응 없으면 시비 걸기
        if time.time() - last_bother_time > 4.0:
            bother_ment = random.choice(dialogue["bother_ments"])
            announce(hw, bother_ment)
            if hw["display"]: hw["display"].text = "대기  중..."
            last_bother_time = time.time()
            motion_count = 0 # 멘트 도중 움직임 카운트 리셋

        time.sleep(0.05)

# 개선 ④: ToF 3회 연속 감지 로직 적용
def wait_user(hw):
    if not hw["tof"]: return
    print("Waiting user...")
    tof_count = 0
    
    while True:
        distance = hw["tof"].distance
        
        # 3번 연속 2cm ~ 30cm 사이 유지 체크
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
    if hw["display"]: hw["display"].text = "오늘의    기분은?"
    while True:
        mood = min(int(hw["dial"].turn), 100)
        score_text = f"현재  점수 :  {mood}"
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
# Main
# ==========================================
def main():
    # 개선 ①: 프로그램 시작 시 단 한 번만 pygame mixer 초기화
    pygame.mixer.init()
    
    hw = connect_modules()
    startup(hw)
    try:
        while True:
            wait_motion_with_bother(hw)  
            wait_user(hw)                
            mood = input_mood(hw)        
            save_mood(hw, mood)   
            
            if hw["speaker"]: hw["speaker"].reset()
            
            print("") 
            for i in range(refresh_time, 0, -1):
                countdown_text = f"{i}초 뒤 재시작"
                print(f"[MindMODI] {countdown_text}      ", end="\r")
                if hw["display"]: hw["display"].text = f"{i}초  뒤  재시작"
                time.sleep(1)
            print("") 
                
            if hw["led"]: hw["led"].rgb = (0, 0, 255)  
            play_beep_three_times(hw)
            
    except KeyboardInterrupt:
        if hw["display"]: hw["display"].reset()
        if hw["led"]: hw["led"].turn_off()
    finally:
        # 개선 ①: 프로그램이 완전히 끝날 때 딱 한 번 닫기
        pygame.mixer.quit()

if __name__ == "__main__":
    main()