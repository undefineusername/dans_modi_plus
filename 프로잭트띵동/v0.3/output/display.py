  
# output/display.py


class Display:


    def __init__(self):

        self.face = "normal"



    def show_face(self, emotion):

        self.face = emotion


        faces = {


            "happy":
            "(^_^)",


            "sad":
            "(T_T)",


            "normal":
            "(・_・)",


            "angry":
            "(ಠ_ಠ)",


            "sleep":
            "(-_-)"

        }


        print(
            "[DISPLAY]",
            faces.get(
                emotion,
                "(?)"
            )
        )