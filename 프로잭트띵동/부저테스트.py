import time
import modi_plus

bundle = modi_plus.MODIPlus()

speaker = bundle.speakers[0]

print(speaker.preset_musics()[:5])

speaker.tune = 300, 60

time.sleep(5)