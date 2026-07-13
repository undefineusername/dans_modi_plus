# brain/emotion.py


class Emotion:

    def __init__(self):
        # 0 ~ 100
        self.mood = 50


    def change(self, value):
        """
        감정 변화
        """

        self.mood += value

        # 범위 제한
        self.mood = max(0, min(100, self.mood))


    def get_mood(self):
        return self.mood


    def get_state(self):

        if self.mood >= 70:
            return "happy"

        elif self.mood <= 30:
            return "sad"

        else:
            return "normal"