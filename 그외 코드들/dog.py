import modi_plus
import time

bundle = modi_plus.MODIPlus()

imu = bundle.imus[0]
motor_l = bundle.motors[0]
motor_r = bundle.motors[1]

# 💡 예측을 도입하면 감속이 빨라지므로, Kp를 살짝 높이거나 Kd를 조절해야 할 수 있습니다.
Kp = 1.5  
Kd = 0.2
Ki = 0.0

target = -87

prev_angle = 0  # error 대신 실제 각도의 변화를 추적하기 위해 변경
prev_error = 0

MAX_SPEED = 100
MIN_SPEED = 10 

DEADZONE = 0.5 # 0보다는 약간의 마진을 주는 것이 모터 진동을 막기에 좋습니다.

LEFT_SIGN = 1
RIGHT_SIGN = -1

time.sleep(2.5)

# 초기 각도 설정
prev_angle = imu.angle_x

while True:
    angle = imu.angle_x

    # 1. 🔮 미래 각도 예측 (Prediction)
    # 현재 각속도(변화량) = 현재 각도 - 이전 각도
    angle_velocity = angle - prev_angle
    prev_angle = angle
    
    # 다음 루프(또는 수 루프 뒤)에 도달할 '예측 각도' 계산 
    # 곱하는 상수(예: 1.5)를 조절하여 예측의 가중치(얼마나 앞을 내다볼지)를 설정합니다.
    predicted_angle = angle + (angle_velocity * 1.5) 

    # 2. 오차 계산 (현재 각도 대신 '예측 각도'를 사용)
    error = target - predicted_angle

    # 3. 미분항 계산
    derivative = error - prev_error
    prev_error = error

    # 4. 제어 출력 계산
    output = Kp * error + Kd * derivative

    # 데드존 적용
    if abs(error) < DEADZONE:
        motor_l.speed = 0
        motor_r.speed = 0
        continue

    speed = max(-MAX_SPEED, min(MAX_SPEED, output))

    # min speed 적용
    if speed != 0:
        if 0 < abs(speed) < MIN_SPEED:
            speed = MIN_SPEED if speed > 0 else -MIN_SPEED

    motor_l.speed = speed * LEFT_SIGN
    motor_r.speed = speed * RIGHT_SIGN

    # 모니터링을 위해 predicted_angle도 함께 출력
    print(f"angle:{angle:.2f} (pred:{predicted_angle:.2f}) speed:{speed:.2f}", end="\r")

    time.sleep(0.02)