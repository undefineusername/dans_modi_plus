import time
import os
import random
import modi_plus
from gtts import gTTS
import pygame

refresh_time = 10

# ==========================================
# 랜덤 멘트 목록
# ==========================================
BOTHER_MENTS = [
    "저기요?",
    "계세요?",
    "거기 누구 없나요?",
    "일로 와보세요.",
    "심심해요."
]

# ==========================================
# gTTS 음성 출력 함수
# ==========================================
def speak(text):
    print(f"[TTS] \"{text}\"")
    try:
        tts = gTTS(text=text, lang='ko', slow=False) 
        filename = "temp.mp3"
        tts.save(filename)
        
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): time.sleep(0.05)
            
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        if os.path.exists(filename): os.remove(filename)
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
# 시작 (멘트 랜덤 변경)
# ==========================================
def startup(hw):
    # 시작할 때 리스트 중에서 무작위로 하나를 골라 말합니다.
    start_ment = random.choice(BOTHER_MENTS)
    if hw["display"]: hw["display"].text = start_ment
    if hw["led"]: hw["led"].rgb = (0, 0, 255)  
    
    play_beep_three_times(hw)
    speak(start_ment)
    time.sleep(1)

# ==========================================
# 1차 : 움직임 감지 (민감도 대폭 상향 수정)
# ==========================================
def wait_motion_with_bother(hw):
    if not hw["imu"]: return
    print("Waiting motion...")
    if hw["display"]: hw["display"].text = "대기  중..."
    if hw["led"]: hw["led"].rgb = (0, 0, 255)  

    last_bother_time = time.time()

    while True:
        # IMU 자이로 센서 값 읽기
        vel_x = abs(hw["imu"].angular_vel_x)
        vel_y = abs(hw["imu"].angular_vel_y)
        vel_z = abs(hw["imu"].angular_vel_z)
        movement = vel_x + vel_y + vel_z
        
        print(f"Movement : {movement:.1f}", end="\r")

        # 인식을 더 잘하도록 임계값을 기존 30에서 '5'로 낮췄습니다.
        # 살짝만 건드려도 다음(ToF) 단계로 넘어갑니다.
        if movement > 5:   
            print("\n움직임 감지! -> 거리 측정 시작")
            if hw["display"]: hw["display"].text = "앞으로    오세요"
            if hw["led"]: hw["led"].rgb = (255, 255, 0)  
            speak("앞으로 오세요.")
            return

        # 4초 동안 미동이 없으면 쫑알쫑알 말 걸기
        if time.time() - last_bother_time > 4.0:
            ment = random.choice(BOTHER_MENTS)
            if hw["display"]: hw["display"].text = ment
            speak(ment)
            if hw["display"]: hw["display"].text = "대기  중..."
            last_bother_time = time.time()

        time.sleep(0.05)

# ==========================================
# 2차 : 가까이 오면 인식 (ToF)
# ==========================================
def wait_user(hw):
    if not hw["tof"]: return
    print("Waiting user...")
    while True:
        distance = hw["tof"].distance
        # ToF 센서 값이 가끔 0 이하 오류값을 뱉는 걸 방지
        if 2 < distance < 30:
            if hw["display"]: hw["display"].text = "안녕하세요 ! !"
            if hw["led"]: hw["led"].rgb = (0, 255, 0)  
            speak("오늘 기분은 어떤가요?")
            return
        time.sleep(0.05)

def input_mood(hw):
    if not hw["dial"] or not hw["button"]: return 0
    if hw["display"]: hw["display"].text = "오늘의    기분은?"
    while True:
        mood = int(hw["dial"].turn)
        if hw["display"]: hw["display"].text = f"현재  점수 :  {mood}"
        if hw["led"]: hw["led"].rgb = (255, 0, 0)  
        if hw["button"].pressed:
            while hw["button"].pressed: time.sleep(0.01)
            return mood
        time.sleep(0.05)

def save_mood(hw, mood):
    print(f"\nSaved : {mood}")
    if hw["display"]: hw["display"].text = f"저장  완료 :  {mood}"
    if hw["led"]: hw["led"].rgb = (0, 255, 0)  
    speak(f"{mood}점 저장 완료.")
    time.sleep(1)

# ==========================================
# Main
# ==========================================
def main():
    hw = connect_modules()
    startup(hw)
    try:
        while True:
            wait_motion_with_bother(hw)  # 1단계: IMU로 툭 치는 것 감지 (안 치면 말 걸기)
            wait_user(hw)                # 2단계: ToF로 30cm 이내 접근 감지
            mood = input_mood(hw)        
            save_mood(hw, mood)   
            
            print("\n10s Break...")
            if hw["speaker"]: hw["speaker"].reset()
            
            for i in range(refresh_time, 0, -1):
                if hw["display"]: hw["display"].text = f"{i}초  뒤  재시작"
                time.sleep(1)
                
            if hw["led"]: hw["led"].rgb = (0, 0, 255)  
            play_beep_three_times(hw)
    except KeyboardInterrupt:
        if hw["display"]: hw["display"].reset()
        if hw["led"]: hw["led"].turn_off()

if __name__ == "__main__":
    main()