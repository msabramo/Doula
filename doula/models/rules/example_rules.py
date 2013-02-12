import random

class ExampleRule(object):

    def __init__(self, category):
        self.category = category
        self.is_valid = False
        self.error_text = ""
        self.description = "Validate that this service does what it should."

    def validate(self):
        if random.random() > 0.4:
            self.is_valid = True
        else:
            self.is_valid = False
            self.error_text = "This error was randomly generated"
