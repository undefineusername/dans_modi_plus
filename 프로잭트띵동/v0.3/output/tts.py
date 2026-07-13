  
# output/tts.py


class TTS:


    def __init__(self):

        self.enabled = True



    def speak(self, text):

        if not self.enabled:
            return


        print(
            "[TTS]",
            text
        )


    def stop(self):

        print(
            "[TTS STOP]"
        )