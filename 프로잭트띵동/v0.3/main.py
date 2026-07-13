import json
import random
import os
import json


from brain import (
    Emotion,
    Memory,
    Conversation,
    RobotState
)


from output import (
    TTS,
    SoundEffect,
    Display,
    SpeechManager
)



# -------------------
# 데이터 로드
# -------------------



BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


dialogue_path = os.path.join(
    BASE_DIR,
    "data",
    "dialogue.json"
)


with open(
    dialogue_path,
    "r",
    encoding="utf-8"
) as f:

    dialogue = json.load(f)



# -------------------
# 객체 생성
# -------------------

emotion = Emotion()

memory = Memory()

state = RobotState()


conversation = Conversation(
    emotion,
    memory
)



tts = TTS()

speech = SpeechManager(
    tts
)


effect = SoundEffect()

display = Display()



# -------------------
# 함수
# -------------------

def get_text(intent):

    return random.choice(
        dialogue.get(
            intent,
            dialogue["unknown"]
        )
    )



def react(intent):


    # 기억
    memory.interact()



    # 감정 변화

    if intent == "hello":

        emotion.change(5)

        effect.play(
            "happy"
        )


    elif intent == "play":

        emotion.change(10)

        effect.play(
            "happy"
        )


    elif intent == "negative":

        emotion.change(-5)



    elif intent == "sleep":

        state.set(
            "sleep"
        )



    # 대사

    text = get_text(
        intent
    )


    # 출력

    speech.say(
        text
    )


    display.show_face(
        emotion.get_state()
    )



# -------------------
# 시작
# -------------------

print(
    "MODI v0.3 START"
)


state.set(
    "idle"
)



while True:


    user = input(
        "YOU : "
    )


    intent = conversation.analyze(
        user
    )


    react(
        intent
    )