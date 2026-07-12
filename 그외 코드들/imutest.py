import modi_plus
import time
import pydirectinput  # ⚠️ 필수 설치: pip install pydirectinput

# pydirectinput 입력 지연 최소화
pydirectinput.PAUSE = 0.001

bundle = modi_plus.MODIPlus()
imu = bundle.imus[0]
dial = bundle.dials[0]
joystick = bundle.joysticks[0]

OFFSET = 0

print("==================================================")
print("🏎️ 레이싱 게임 컨트롤러 [즉시 HOLD 모드] 작동!")
print("조금만 조작해도 바로 꾹 누르고, 중앙 근처에서만 뗍니다.")
print("==================================================")
time.sleep(1.5)

# 누름 상태 추적을 위한 변수
is_holding = {'w': False, 's': False, 'a': False, 'd': False}

def handle_key_logic(key, factor):
    """
    어느 정도(0.3)만 넘으면 즉시 꾹 누르고(Hold), 
    중앙 데드존(0.05) 이하로 떨어져야 키를 떼는 로직
    """
    # 1. ⚡ 꾹 누르기 (Hold) 발동 기준: 30%만 넘어도 즉시 누름!
    if factor >= 0.30:
        if not is_holding[key]:
            pydirectinput.keyDown(key)
            is_holding[key] = True
            
    # 2. 💨 완전 중앙 근처로 돌아왔을 때만 키를 완전히 뗌 (Release)
    elif factor <= 0.05:
        if is_holding[key]:
            pydirectinput.keyUp(key)
            is_holding[key] = False
            
    # 3. 🔄 그 사이 구간 (0.05 ~ 0.30)
    else:
        # 이미 누르고 있는 상태라면 떼지 않고 유지 (조작 안정성 확보)
        # 만약 이 좁은 구간에서도 연타를 넣고 싶다면 아래 주석을 해제하세요.
        pass

while True:
    # 1. 센서 데이터 읽기
    angle_z = imu.angle_z + OFFSET
    dial_val = dial.turn
    joy_y = joystick.y
    joy_dir = joystick.direction

    # 각 키의 강도 초기화 (0.0 ~ 1.0)
    factors = {'w': 0.0, 's': 0.0, 'a': 0.0, 'd': 0.0}

    # 2. 다이얼 (속도 W/S) 강도 계산
    if dial_val > 55:
        factors['w'] = min(1.0, (dial_val - 55) / 35.0)  # 살짝만 돌려도 1.0에 가깝게
    elif dial_val < 45:
        factors['s'] = min(1.0, (45 - dial_val) / 35.0)

    # 3. 핸들 IMU (방향 A/D) 강도 계산 (+가 오른쪽, -가 LEFT)
    if angle_z > 5:
        factors['d'] = min(1.0, angle_z / 25.0)          # 조금만 꺾어도(25도) 끝까지 도달한 것으로 처리
    elif angle_z < -5:
        factors['a'] = min(1.0, abs(angle_z) / 25.0)

    # 4. 키보드 제어 함수 실행 (W, S, A, D 각각 독립 제어)
    for key in ['w', 's', 'a', 'd']:
        handle_key_logic(key, factors[key])

    # 5. 조이스틱 입력 상태 확인 (C 및 CTRL)
    if joy_y > 40 or joy_dir == 1:
        pydirectinput.press('c')
    elif joy_y < -40 or joy_dir == 5:
        pydirectinput.press('ctrl')

    # 콘솔 출력 (현재 어떤 키가 꾹 누름(Hold) 상태인지 모니터링)
    hold_status = ", ".join([k.upper() for k, v in is_holding.items() if v])
    print(f" 꾹 누르는 중: [{hold_status if hold_status else '없음'}]", end="\r")

    time.sleep(0.005)