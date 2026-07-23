import time

from ai.counselor import Counselor
from constants import (
    BOTHER_INTERVAL_SEC,
    COUNSEL_EXIT_WORDS,
    LED_BLUE,
    LED_GREEN,
    LED_RED,
    LED_YELLOW,
    MOTION_COUNT_REQUIRED,
    MOTION_THRESHOLD,
    REFRESH_TIME_SEC,
    TOF_COUNT_REQUIRED,
    TOF_MAX_DISTANCE,
    TOF_MIN_DISTANCE,
)
from database import save_mood_score
from hardware import connect_hardware
from voice import Voice


def startup(hw, voice):
    hw.set_led(LED_BLUE)
    hw.play_beep_three_times()
    time.sleep(1)


def wait_motion_with_bother(hw, voice):
    if not hw.imu:
        return

    hw.show_text("대기  중...")
    hw.set_led(LED_BLUE)

    last_bother_time = time.time()
    motion_count = 0

    while True:
        movement = hw.read_movement()
        print(f"Movement : {movement:.1f} (Count: {motion_count})      ", end="\r")

        if movement > MOTION_THRESHOLD:
            motion_count += 1
        else:
            motion_count = 0

        if motion_count >= MOTION_COUNT_REQUIRED:
            hw.set_led(LED_YELLOW)
            voice.announce(hw, "앞으로 오세요.")
            return

        if time.time() - last_bother_time > BOTHER_INTERVAL_SEC:
            voice.announce(hw, "저기요?")
            hw.show_text("대기  중...")
            last_bother_time = time.time()
            motion_count = 0

        hw.sleep()


def wait_user(hw, voice):
    if not hw.tof:
        return

    print("Waiting user...")
    tof_count = 0

    while True:
        distance = hw.read_distance()

        if TOF_MIN_DISTANCE < distance < TOF_MAX_DISTANCE:
            tof_count += 1
        else:
            tof_count = 0

        if tof_count >= TOF_COUNT_REQUIRED:
            hw.set_led(LED_GREEN)
            voice.announce(hw, "오늘 기분은 어떤가요?")
            return

        hw.sleep()


def input_mood(hw):
    if not hw.dial or not hw.button:
        return 0

    hw.show_text("오늘의    기분은?")

    while True:
        mood = hw.read_mood()
        score_text = f"현재  점수 :  {mood}"
        print(f"[MindMODI] {score_text}      ", end="\r")
        hw.show_text(score_text)
        hw.set_led(LED_RED)

        if hw.is_button_pressed():
            hw.wait_button_release()
            return mood

        hw.sleep()


def save_mood(hw, voice, mood):
    hw.set_led(LED_GREEN)
    save_mood_score(mood)
    voice.announce(hw, f"{mood}점 저장 완료.")
    time.sleep(1)


def run_counseling(hw, voice, mood):
    counselor = Counselor(mood)
    opening = counselor.opening_message()
    voice.announce(hw, opening)

    print("\n[상담 시작] 말하기는 콘솔 입력, 종료는 '종료' 입력\n")

    while True:
        user_text = input("YOU: ").strip()
        if not user_text:
            continue

        if user_text.lower() in COUNSEL_EXIT_WORDS:
            voice.announce(hw, "상담을 마칠게요. 오늘도 수고했어요.")
            break

        reply = counselor.chat(user_text)
        counselor.refresh_system_prompt()
        print(f"MindMODI: {reply}\n")
        voice.announce(hw, reply)


def countdown_restart(hw):
    print("")
    for i in range(REFRESH_TIME_SEC, 0, -1):
        countdown_text = f"{i}초 뒤 재시작"
        print(f"[MindMODI] {countdown_text}      ", end="\r")
        hw.show_text(f"{i}초  뒤  재시작")
        time.sleep(1)
    print("")


def main():
    voice = Voice()
    voice.init()

    hw = connect_hardware()
    startup(hw, voice)

    try:
        while True:
            wait_motion_with_bother(hw, voice)
            wait_user(hw, voice)
            mood = input_mood(hw)
            save_mood(hw, voice, mood)
            run_counseling(hw, voice, mood)

            hw.stop_beep()
            countdown_restart(hw)

            hw.set_led(LED_BLUE)
            hw.play_beep_three_times()

    except KeyboardInterrupt:
        hw.shutdown()
    finally:
        voice.shutdown()


if __name__ == "__main__":
    main()
