"""
MindMODI v0.7 - MODI+ 하드웨어 레이어

v0.4.1의 connect_modules / LED / 부저 / 센서 읽기 로직을
v0.7 모듈 구조로 분리했다.
v0.1 테스트 코드의 MODI 연결 패턴을 따른다.
"""

import time

import modi_plus

from constants import (
    BEEP_COUNT,
    BEEP_FREQ,
    BEEP_OFF_SEC,
    BEEP_ON_SEC,
    BEEP_VOLUME,
    BUTTON_RELEASE_SLEEP_SEC,
    CONNECT_WAIT_SEC,
    LOOP_SLEEP_SEC,
    MOOD_MAX,
)


class Hardware:
    """MODI+ 모듈 연결 및 저수준 제어."""

    def __init__(self):
        self.speaker = None
        self.display = None
        self.led = None
        self.button = None
        self.dial = None
        self.tof = None
        self.imu = None
        self.env = None

    def connect(self):
        """MODI+ 번들에 연결하고 사용 가능한 모듈을 할당한다."""
        print("Connecting to MODI...")
        bundle = modi_plus.MODIPlus()
        time.sleep(CONNECT_WAIT_SEC)

        self.speaker = bundle.speakers[0] if bundle.speakers else None
        self.display = bundle.displays[0] if bundle.displays else None
        self.led = bundle.leds[0] if bundle.leds else None
        self.button = bundle.buttons[0] if bundle.buttons else None
        self.dial = bundle.dials[0] if bundle.dials else None
        self.tof = bundle.tofs[0] if bundle.tofs else None
        self.imu = bundle.imus[0] if bundle.imus else None
        self.env = bundle.envs[0] if bundle.envs else None

        print("Connected!")
        self.print_status()
        return self

    def print_status(self):
        """v0.1 스타일 모듈 연결 상태 출력."""
        modules = {
            "Speaker": self.speaker,
            "Display": self.display,
            "LED": self.led,
            "Button": self.button,
            "Dial": self.dial,
            "TOF": self.tof,
            "Environment": self.env,
            "IMU": self.imu,
        }

        print("\n[ Module Status ]")
        for name, module in modules.items():
            print(f"{name:<13}: {'OK' if module else 'X'}")
        print()

    # -------------------------------------------------
    # 출력
    # -------------------------------------------------

    def show_text(self, text):
        if self.display:
            self.display.text = text

    def set_led(self, rgb):
        if self.led:
            self.led.rgb = rgb

    def turn_off_led(self):
        if self.led:
            self.led.turn_off()

    def play_beep(self, freq=BEEP_FREQ, volume=BEEP_VOLUME):
        if self.speaker:
            self.speaker.tune = (freq, volume)

    def stop_beep(self):
        if self.speaker:
            self.speaker.reset()

    def play_beep_three_times(self):
        """v0.4.1 시작/재시작 알림음."""
        if not self.speaker:
            return

        for _ in range(BEEP_COUNT):
            self.play_beep()
            time.sleep(BEEP_ON_SEC)
            self.stop_beep()
            time.sleep(BEEP_OFF_SEC)

    # -------------------------------------------------
    # 센서 읽기
    # -------------------------------------------------

    def read_movement(self):
        """IMU 각속도 합산값. 모듈 없으면 0."""
        if not self.imu:
            return 0.0

        return (
            abs(self.imu.angular_vel_x)
            + abs(self.imu.angular_vel_y)
            + abs(self.imu.angular_vel_z)
        )

    def read_distance(self):
        """ToF 거리(cm). 모듈 없으면 -1."""
        if not self.tof:
            return -1.0

        return self.tof.distance

    def read_mood(self):
        """Dial 회전값을 0~MOOD_MAX 범위로 반환."""
        if not self.dial:
            return 0

        return min(int(self.dial.turn), MOOD_MAX)

    def is_button_pressed(self):
        return bool(self.button and self.button.pressed)

    def wait_button_release(self):
        if not self.button:
            return

        while self.button.pressed:
            time.sleep(BUTTON_RELEASE_SLEEP_SEC)

    # -------------------------------------------------
    # 센서 추상화 (v1.0)
    # -------------------------------------------------

    def get_mood(self):
        """v1.0 기분 센싱 래퍼"""
        return self.read_mood()

    def get_environment(self):
        """v1.0 환경 데이터 반환"""
        if not self.env:
            return {"temperature": 0.0, "humidity": 0.0, "brightness": 0.0}
        return {
            "temperature": self.env.temperature,
            "humidity": self.env.humidity,
            "brightness": self.env.brightness
        }

    def detect_presence(self, motion_threshold, tof_min, tof_max):
        """v1.0 사람 감지 래퍼"""
        movement = self.read_movement()
        distance = self.read_distance()
        has_motion = movement > motion_threshold
        has_close_object = (tof_min < distance < tof_max)
        return has_motion or has_close_object

    # -------------------------------------------------
    # 종료
    # -------------------------------------------------

    def reset_outputs(self):
        if self.display:
            self.display.reset()
        if self.speaker:
            self.speaker.reset()

    def shutdown(self):
        """v0.1 / v0.4.1 종료 처리."""
        print("\nShutting down...")
        self.reset_outputs()
        self.turn_off_led()
        print("Good Bye!")

    @staticmethod
    def sleep(interval=LOOP_SLEEP_SEC):
        time.sleep(interval)


def connect_hardware():
    """main.py에서 바로 쓸 수 있는 연결 헬퍼."""
    return Hardware().connect()
