import cv2
import numpy as np
import math

# 전역 변수 선언
clicked_points = []  # 사용자가 마우스로 클릭한 좌표
is_tracking = False  # 락온 활성화 여부

def mouse_callback(event, x, y, flags, param):
    global clicked_points, is_tracking
    
    # 클릭했을 때 이미 락온 상태라면 리셋하기 전까지 클릭 무시
    if event == cv2.EVENT_LBUTTONDOWN and not is_tracking:
        if len(clicked_points) < 2:
            clicked_points.append((x, y))
            if len(clicked_points) == 1:
                print(f"🔴 [1/2] 첫 번째 빨간 점(헤드) 지정: ({x}, {y}) -> 두 번째 빨간 점을 클릭하세요.")
            elif len(clicked_points) == 2:
                is_tracking = True
                print(f"🎯 [2/2] 두 번째 빨간 점(바퀴) 지정: ({x}, {y}) -> 빨간 마커 락온 추적을 시작합니다!")

# 카메라 캡처 시작
cap = cv2.VideoCapture(0)
cv2.namedWindow("Robot Red Marker Lock-on")
cv2.setMouseCallback("Robot Red Marker Lock-on", mouse_callback)

print("--------------------------------------------------")
print("🖱️ [빨간색 마커 지정 추적기 사용법]")
print("   1. 로봇에 붙어있는 첫 번째 '빨간 점'을 마우스로 클릭하세요.")
print("   2. 이어서 두 번째 '빨간 점'을 마우스로 클릭하세요.")
print("   3. 두 점을 찍는 순간 자동으로 빨간 마커만 락온 추적합니다.")
print("   4. 'r' 키를 누르면 락온을 풀고 리셋합니다. 'q'는 종료입니다.")
print("--------------------------------------------------")

while True:
    ret, frame = cap.read()
    if not ret:
        print("카메라 프레임을 읽을 수 없습니다.")
        break

    # 조명 변화에 강한 HSV 색상 공간 변환
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 1. 빨간색 기본 필터링 범위 설정
    lower_red1, upper_red1 = np.array([0, 120, 70]), np.array([10, 255, 255])
    lower_red2, upper_red2 = np.array([170, 120, 70]), np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2

    # 자잘한 노이즈 제거
    red_mask = cv2.erode(red_mask, None, iterations=1)
    red_mask = cv2.dilate(red_mask, None, iterations=2)

    # 빨간색 덩어리들의 윤곽선(테두리) 찾기
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 현재 화면에서 발견된 모든 빨간 점들의 중심 좌표 계산
    current_red_pts = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 20: # 최소 크기 필터링
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                current_red_pts = sorted(current_red_pts, key=lambda p: p[1])
                current_red_pts.append((cx, cy))

    # 2. 🚀 사용자가 점 2개를 찍어서 락온이 활성화된 상태일 때
    if is_tracking and len(clicked_points) == 2:
        tracked_pair = []
        
        # 내가 처음에 찍었던 마우스 좌표와 가장 가까운 진짜 빨간 점 2개를 매칭
        for target_pt in clicked_points:
            closest_pt = None
            min_dist = 9999
            for red_pt in current_red_pts:
                dist = math.hypot(red_pt[0] - target_pt[0], red_pt[1] - target_pt[1])
                if dist < min_dist and dist < 80: # 80픽셀 이내의 근접한 점만 인정
                    min_dist = dist
                    closest_pt = red_pt
            
            if closest_pt is not None:
                tracked_pair.append(closest_pt)

        # 실시간으로 추적된 두 개의 빨간 점이 모두 존재할 때 각도 연산
        if len(tracked_pair) == 2:
            # 실시간 좌표로 유저 기준점 갱신 (로봇이 움직여도 따라가도록)
            clicked_points = tracked_pair 
            
            pt_head = tracked_pair[0]
            pt_wheel = tracked_pair[1]

            # 시각화 가이드라인 그리기
            cv2.circle(frame, pt_head, 8, (0, 255, 0), -1)  # 추적 중인 헤드 (초록)
            cv2.circle(frame, pt_wheel, 8, (255, 0, 0), -1) # 추적 중인 바퀴 (파랑)
            cv2.line(frame, pt_head, pt_wheel, (0, 255, 255), 2) # 로봇 중심선 (노랑)
            cv2.line(frame, (pt_wheel[0] - 150, pt_wheel[1]), (pt_wheel[0] + 150, pt_wheel[1]), (0, 255, 0), 1) # 지면선 (초록)

            # 📐 실시간 각도 계산
            dx = pt_head[0] - pt_wheel[0]
            dy = pt_wheel[1] - pt_head[1]
            angle_deg = math.degrees(math.atan2(dy, dx))
            tilt_angle = angle_deg - 90

            # 텍스트 출력
            cv2.putText(frame, "RED LOCK-ON [ON]", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Absolute Angle: {angle_deg:.1f} deg", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame, f"Tilt Angle: {tilt_angle:.1f} deg", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            # 로봇을 너무 빨리 움직였거나 가려져서 빨간 점을 순간 놓쳤을 때
            cv2.putText(frame, "LOCK LOST! Keep robot still or press 'r'", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # 3. 🎯 준비 단계 (사용자가 마우스로 빨간 마커 위치 지정하는 중)
    else:
        for i, pt in enumerate(clicked_points):
            cv2.circle(frame, pt, 5, (0, 0, 255), -1)
            cv2.putText(frame, f"Target {i+1}", (pt[0]+10, pt[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        rem = 2 - len(clicked_points)
        cv2.putText(frame, f"Click on the 2 Red Markers (Remaining: {rem})", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # 결과 화면 출력
    cv2.imshow("Robot Red Marker Lock-on", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        clicked_points = []
        is_tracking = False
        print("🔄 락온이 해제되었습니다. 빨간 마커를 다시 클릭해 주세요.")

cap.release()
cv2.destroyAllWindows()