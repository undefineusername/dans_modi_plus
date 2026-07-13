import time
import modi_plus

# ==========================================
# 효과음: 삡삡삡 (파란불용)
# ==========================================
def play_beep_three_times(hw):
    if hw["speaker"]:
        for _ in range(3):
            hw["speaker"].tune = (523, 30)  # 부드러운 5옥타브 도
            time.sleep(0.08)                # 소리 유지 시간
            hw["speaker"].reset()           # 소리 잠시 끄기
            time.sleep(0.05)                # 음과 음 사이 간격

# ==========================================
# MODI 연결
# ==========================================
def connect_modules():
    print("Connecting MODI...")
    bundle = modi_plus.MODIPlus()
    time.sleep(2)

    hw = {
        "speaker": bundle.speakers[0] if bundle.speakers else None,
        "display": bundle.displays[0] if bundle.displays else None,
        "led": bundle.leds[0] if bundle.leds else None,
        "button": bundle.buttons[0] if bundle.buttons else None,
        "dial": bundle.dials[0] if bundle.dials else None,
        "tof": bundle.tofs[0] if bundle.tofs else None,
        "env": bundle.envs[0] if bundle.envs else None,
        "imu": bundle.imus[0] if bundle.imus else None,
    }
    print("Connected!")
    return hw

# ==========================================
# 시작
# ==========================================
def startup(hw):
    if hw["display"]:
        hw["display"].text = "MindMODI  v0.2"
    if hw["led"]:
        hw["led"].rgb = (0, 0, 255)  # 파란불
    
    # 파란불 켜지면서 삡삡삡
    play_beep_three_times(hw)
    time.sleep(1)

# ==========================================
# 사용자 대기
# ==========================================
def wait_user(hw):
    if not hw["tof"]:
        print("Error: No ToF sensor")
        return

    print("기다리는 중..")
    if hw["display"]:
        hw["display"].text = "Waiting___"
    if hw["led"]:
        hw["led"].rgb = (0, 0, 255)  # 파란불 보장

    while True:
        distance = hw["tof"].distance
        print(f"Distance : {distance:.1f} cm", end="\r")

        if 0 < distance < 30:
            print("\n안녕하세요! 오늘 기분은?")
            if hw["speaker"]:
                # 감지되었을 때는 단발성 음
                hw["speaker"].tune = (523, 30)
            if hw["led"]:
                hw["led"].rgb = (255, 255, 0)
            return
        time.sleep(0.05)

# ==========================================
# 기분 입력
# ==========================================
def input_mood(hw):
    if not hw["dial"] or not hw["button"]:
        print("Error: No dial or button")
        return 0

    if hw["display"]:
        hw["display"].text = "Today Mood?"

    while True:
        mood = int(hw["dial"].turn)
        if hw["display"]:
            hw["display"].text = f"Score  ___  {mood}"
        print(f"Mood : {mood}    ", end="\r")

        if hw["button"].pressed:
            while hw["button"].pressed:
                time.sleep(0.01)
            return mood
        time.sleep(0.05)

# ==========================================
# 저장
# ==========================================
def save_mood(hw, mood):
    print(f"\nSaved : {mood}")
    if hw["display"]:
        hw["display"].text = f"Saved  ___  {mood}"
    if hw["speaker"]:
        hw["speaker"].tune = (659, 30)  # 미~ 소리
    if hw["led"]:
        hw["led"].rgb = (0, 255, 0)
    time.sleep(2)

# ==========================================
# 종료
# ==========================================
def shutdown(hw):
    print("\nShutdown...")
    if hw["display"]:
        hw["display"].reset()
    if hw["speaker"]:
        hw["speaker"].reset()
    if hw["led"]:
        hw["led"].turn_off()

# ==========================================
# Main
# ==========================================
def main():
    hw = connect_modules()
    startup(hw)

    try:
        while True:
            wait_user(hw)
            mood = input_mood(hw)
            save_mood(hw, mood)
            
            print("\n10초 대기 중...")
            if hw["display"]:
                hw["display"].text = "Next_in_10s"
            if hw["speaker"]:
                hw["speaker"].reset()
                
            time.sleep(10) # 10초 리프레시 타임
            
            # 10초 대기가 끝나고 다시 파란불로 바뀔 때 삡삡삡!
            print("다시 시작합니다.")
            play_beep_three_times(hw)
            
    except KeyboardInterrupt:
        shutdown(hw)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExit")