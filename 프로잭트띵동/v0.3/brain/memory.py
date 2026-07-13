  
# brain/memory.py


class Memory:

    def __init__(self):

        self.visit_count = 0
        self.interaction_count = 0

        self.last_topic = None


    def visit(self):

        self.visit_count += 1


    def interact(self):

        self.interaction_count += 1


    def remember_topic(self, topic):

        self.last_topic = topic


    def get_info(self):

        return {

            "visit": self.visit_count,

            "interaction": self.interaction_count,

            "last_topic": self.last_topic
        }