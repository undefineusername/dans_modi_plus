import modi_plus
import time

bundle = modi_plus.MODIPlus()

button = bundle.buttons[0]
dial = bundle.dials[0]
env = bundle.envs[0]
display = bundle.displays[0]
speaker = bundle.speakers[0]
tof = bundle.tofs[0]
led = bundle.leds[0]
imu = bundle.imus[0]

print("All modules loaded!")

while True:
    print(dial.degree)
    time.sleep(0.2)