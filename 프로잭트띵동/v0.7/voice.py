import os
import time

import pygame
from gtts import gTTS


class Voice:
    """TTS 및 화면/콘솔 출력."""

    def __init__(self):
        self._ready = False

    def init(self):
        pygame.mixer.init()
        self._ready = True

    def announce(self, hardware, text, use_tts=True):
        print(f"\n[MindMODI] {text}")
        if hardware:
            hardware.show_text(text)

        if not use_tts or not self._ready:
            return

        try:
            tts = gTTS(text=text, lang="ko", slow=False)
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

    def shutdown(self):
        if self._ready:
            pygame.mixer.quit()
            self._ready = False
