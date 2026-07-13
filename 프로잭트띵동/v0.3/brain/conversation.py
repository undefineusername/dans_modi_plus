# brain/conversation.py


class Conversation:


    def __init__(
        self,
        emotion,
        memory
    ):

        self.emotion = emotion
        self.memory = memory



    def analyze(self, text):

        text = text.lower()


        if "안녕" in text:

            return "hello"


        elif "놀자" in text:

            return "play"


        elif "싫어" in text:

            return "negative"


        elif "잘자" in text:

            return "sleep"


        else:

            return "unknown"