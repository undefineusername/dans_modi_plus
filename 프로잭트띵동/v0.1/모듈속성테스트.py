import modi_plus

# MODI+ 연결
bundle = modi_plus.MODIPlus()

# 모듈 가져오기
button = bundle.buttons[0]
dial = bundle.dials[0]
env = bundle.envs[0]
display = bundle.displays[0]
speaker = bundle.speakers[0]
tof = bundle.tofs[0]
led = bundle.leds[0]
imu = bundle.imus[0]

print("=" * 50)
print("All modules loaded!")
print("=" * 50)

modules = {
    "Button": button,
    "Dial": dial,
    "Env": env,
    "Display": display,
    "Speaker": speaker,
    "TOF": tof,
    "LED": led,
    "IMU": imu,
}

for name, module in modules.items():
    print(f"\n{name}")
    print("-" * 50)
    print("Type :", type(module))
    print("Available attributes:")
    for attr in dir(module):
        if not attr.startswith("_"):
            print(attr)

print("\nProgram finished.")