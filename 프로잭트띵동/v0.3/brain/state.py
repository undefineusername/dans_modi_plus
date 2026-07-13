  
# brain/state.py


class RobotState:


    def __init__(self):

        self.state = "idle"


    def set(self, state):

        self.state = state


    def get(self):

        return self.state