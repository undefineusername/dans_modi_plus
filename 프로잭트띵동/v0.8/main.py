import time
import llm  # llm.py 파일 불러오기
import os
import json
import csv
import random
import math  # 조도 보정 연산을 위해 추가
from datetime import datetime
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
# 통합 출력 및 TTS 함수
# ==========================================
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


# ==========================================
# 모듈 연결 (공식 예제 코드 반영)
# ==========================================
def connect_modules():
    print("Connecting MODI+ modules...")
    bundle = modi_plus.MODIPlus()
    time.sleep(1.0)  # 모듈 연결 안정화를 위한 1초 대기

    return {
        "speaker": bundle.speakers[0] if bundle.speakers else None,
        "display": bundle.displays[0] if bundle.displays else None,
        "led": bundle.leds[0] if bundle.leds else None,
        "button": bundle.buttons[0] if bundle.buttons else None,
        "dial": bundle.dials[0] if bundle.dials else None,
        "tof": bundle.tofs[0] if bundle.tofs else None,
        "imu": bundle.imus[0] if bundle.imus else None,
        "env": bundle.envs[0] if bundle.envs else None,
    }


# ==========================================
# 환경 센서 데이터 수집 함수 (조도 보정 15 적용)
# ==========================================
def read_environment_data(hw):
    """예제 스크립트 기준 속성을 읽어오며, 조도(illuminance) 수치를 계수 15로 보정합니다."""
    env_data = {
        "temperature": None,
        "humidity": None,
        "illuminance": None,
        "volume": None
    }

    if not hw["env"]:
        print("[참고] 환경 센서(env) 모듈이 연결되어 있지 않습니다.")
        return env_data

    try:
        env_data["temperature"] = round(float(hw["env"].temperature), 1)
        env_data["humidity"] = round(float(hw["env"].humidity), 1)

        # [조도 보정 적용] sqrt(raw_illu) * 15 (최대 100.0%)
        raw_illu = float(hw["env"].illuminance)
        adjusted_illu = min(round(math.sqrt(raw_illu) * 15, 1), 100.0)
        env_data["illuminance"] = adjusted_illu

        env_data["volume"] = round(float(hw["env"].volume), 1)
    except Exception as e:
        print(f"[경고] 환경 센서 데이터 읽기 실패: {e}")

    return env_data


# ==========================================
# 시스템 루프 구조
# ==========================================
def startup(hw):
    if hw["led"]: hw["led"].rgb = (0, 0, 255)
    play_beep_three_times(hw)

    start_ment = random.choice(dialogue["bother_ments"])
    announce(hw, start_ment)
    time.sleep(1)


def wait_motion_with_bother(hw):
    if not hw["imu"]: return
    if hw["display"]: hw["display"].text = "대기  중..."
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
            if hw["display"]: hw["display"].text = "대기  중..."
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
    if not hw["dial"] or not hw["button"]:
        print("\n[경고] 다이얼 또는 버튼 센서가 연결되지 않아 기본 값(50점)을 기록합니다.")
        return 50

    if hw["display"]: hw["display"].text = "오늘의    기분은?"

    # 이전 버튼 누름 신호 잔상 방지
    while hw["button"].pressed:
        time.sleep(0.01)

    while True:
        mood = min(int(hw["dial"].turn), 100)
        score_text = f"현재  점수 :  {mood}"
        print(f"[MindMODI] {score_text}      ", end="\r")
        if hw["display"]: hw["display"].text = score_text
        if hw["led"]: hw["led"].rgb = (255, 0, 0)

        if hw["button"].pressed:
            time.sleep(0.05)
            while hw["button"].pressed:
                time.sleep(0.01)
            print("")
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

    # 1. 환경 센서 데이터 및 타임스탬프 추출
    env_data = read_environment_data(hw)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. CSV 파일에 데이터 기록
    csv_file = "mood_env_log.csv"
    file_exists = os.path.exists(csv_file)

    try:
        with open(csv_file, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Mood", "Temperature(C)", "Humidity(%)", "Illuminance(%)", "Volume(%)"])

            writer.writerow([
                now_str,
                mood,
                env_data["temperature"],
                env_data["humidity"],
                env_data["illuminance"],
                env_data["volume"]
            ])
        print(f"\n[저장 완료] CSV 파일 기록: {now_str} | 점수: {mood}점 | 환경: {env_data}")

        try:
            llm.run_consultation_system(user_mood=mood, env_data=env_data)
        except Exception as err:
            print(f"[경고] 심리 상담 모드 실행 중 오류 발생: {err}")
    except Exception as e:
        print(f"\n[오류] 데이터 파일 저장 실패: {e}")

    time.sleep(1)


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
        pygame.mixer.quit()


if __name__ == "__main__":
    main()
