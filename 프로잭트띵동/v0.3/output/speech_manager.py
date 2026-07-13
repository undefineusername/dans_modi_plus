  
# output/speech_manager.py


class SpeechManager:


    def __init__(self, tts):

        self.tts = tts

        self.speaking = False



    def say(
        self,
        text,
        priority=1
    ):


        if self.speaking:

            if priority < 3:

                print(
                    "말하는 중..."
                )

                return


            else:

                self.stop()



        self.speaking = True


        self.tts.speak(text)


        self.speaking = False



    def stop(self):

        self.tts.stop()

        self.speaking = False