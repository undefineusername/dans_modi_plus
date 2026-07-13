"""
===========================================
 MindMODI v0.1
 Hardware Bring-Up Test
===========================================
"""

import os
import time
import modi_plus


# -------------------------------------------------
# 화면 초기화
# -------------------------------------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")


# -------------------------------------------------
# MODI 연결
# -------------------------------------------------
print("Connecting to MODI...")

bundle = modi_plus.MODIPlus()

time.sleep(2)

print("Connected!\n")


# -------------------------------------------------
# 모듈 연결
# -------------------------------------------------
speaker = bundle.speakers[0] if bundle.speakers else None
display = bundle.displays[0] if bundle.displays else None
led = bundle.leds[0] if bundle.leds else None
button = bundle.buttons[0] if bundle.buttons else None
dial = bundle.dials[0] if bundle.dials else None
tof = bundle.tofs[0] if bundle.tofs else None
env = bundle.envs[0] if bundle.envs else None
imu = bundle.imus[0] if bundle.imus else None


# -------------------------------------------------
# 시작 테스트
# -------------------------------------------------

if speaker:
    speaker.tune = (800, 70)

if display:
    display.text = "MindMODI\nv0.1"

if led:
    led.rgb = (0, 255, 0)


# -------------------------------------------------
# 메인 루프
# -------------------------------------------------

try:

    while True:

        clear()

        print("=" * 60)
        print("              MindMODI v0.1")
        print("            Hardware Test")
        print("=" * 60)

        print("\n[ Module Status ]\n")

        print(f"Speaker      : {'OK' if speaker else 'X'}")
        print(f"Display      : {'OK' if display else 'X'}")
        print(f"LED          : {'OK' if led else 'X'}")
        print(f"Button       : {'OK' if button else 'X'}")
        print(f"Dial         : {'OK' if dial else 'X'}")
        print(f"TOF          : {'OK' if tof else 'X'}")
        print(f"Environment  : {'OK' if env else 'X'}")
        print(f"IMU          : {'OK' if imu else 'X'}")

        print("\n" + "-" * 60)

        # ------------------------
        # Button
        # ------------------------

        if button:
            print(f"Pressed       : {button.pressed}")
            print(f"Double Click  : {button.double_clicked}")

        print()

        # ------------------------
        # Dial
        # ------------------------

        if dial:
            print(f"Dial Turn     : {dial.turn}")

        print()

        # ------------------------
        # TOF
        # ------------------------

        if tof:
            print(f"Distance      : {tof.distance:.1f} cm")

        print()

        # ------------------------
        # ENV
        # ------------------------

        if env:

            print(f"Temperature   : {env.temperature:.1f} °C")
            print(f"Humidity      : {env.humidity:.1f} %")
            print(f"Light         : {env.illuminance:.1f} %")
            print(f"Volume        : {env.volume:.1f} %")

        print()

        # ------------------------
        # IMU
        # ------------------------

        if imu:

            print("Angle")

            print(f" X            : {imu.angle_x:.1f}")
            print(f" Y            : {imu.angle_y:.1f}")
            print(f" Z            : {imu.angle_z:.1f}")

            print()

            print("Angular Velocity")

            print(f" X            : {imu.angular_vel_x:.1f}")
            print(f" Y            : {imu.angular_vel_y:.1f}")
            print(f" Z            : {imu.angular_vel_z:.1f}")

            print()

            print("Acceleration")

            print(f" X            : {imu.acceleration_x:.2f}")
            print(f" Y            : {imu.acceleration_y:.2f}")
            print(f" Z            : {imu.acceleration_z:.2f}")

        print("\n" + "-" * 60)

        print("Speaker : READY")
        print("Display : READY")
        print("LED     : GREEN")

        print("\nPress Ctrl+C to Exit")

        time.sleep(0.1)

except KeyboardInterrupt:

    clear()

    print("Shutting down...")

    if led:
        led.turn_off()

    if display:
        display.reset()

    if speaker:
        speaker.reset()

    print("Good Bye!")