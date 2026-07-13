import time
import modi_plus

bundle = modi_plus.MODIPlus()

speaker = bundle.speakers[0]

# 음계 테스트
speaker.set_tune("LA5", 100)
time.sleep(1)

speaker.set_tune("DO6", 100)
time.sleep(1)

speaker.reset()

# 프리셋 음악 테스트
speaker.play_music("Start", 100)
time.sleep(3)
speaker.stop_music()