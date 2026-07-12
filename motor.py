import modi_plus
import time

bundle = modi_plus.MODIPlus()
imu = bundle.imus[0]

while True:
    print(
        f"angle_x:{imu.angle_x:<10}"
        f"angle_y:{imu.angle_y:<10}"
        f"angle_z:{imu.angle_z:<10}",
        end="\r"
    )
    time.sleep(0.05)