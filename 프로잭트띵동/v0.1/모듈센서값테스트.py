import time
import modi_plus

bundle = modi_plus.MODIPlus()

button = bundle.buttons[0]
dial = bundle.dials[0]
env = bundle.envs[0]
tof = bundle.tofs[0]
imu = bundle.imus[0]

print("Start Monitoring...\n")

while True:
    print("-" * 50)

    print(f"Dial Turn      : {dial.turn}")
    print(f"Dial Speed     : {dial.speed}")

    print(f"Button Pressed : {button.pressed}")
    print(f"Button Clicked : {button.clicked}")

    print(f"Distance       : {tof.distance}")

    print(f"Temperature    : {env.temperature:.1f}")
    print(f"Humidity       : {env.humidity:.1f}")

    print(f"Pitch          : {imu.angle_x:.1f}")
    print(f"Roll           : {imu.angle_y:.1f}")
    print(f"Yaw            : {imu.angle_z:.1f}")

    time.sleep(0.5)