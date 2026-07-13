  
# output/sound_effect.py


class SoundEffect:


    def __init__(self):

        self.enabled = True



    def play(self, name):

        if not self.enabled:
            return


        sounds = {

            "happy":
            "띠링♪",

            "error":
            "삐빅!",

            "fall":
            "쿠당!",

            "click":
            "딸깍"

        }


        if name in sounds:

            print(
                "[EFFECT]",
                sounds[name]
            )