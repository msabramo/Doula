class Tag(object):
    """
    Represents a git tag
    """
    def __init__(self, name, date, message):
        self.name = name
        self.date = date
        self.message = message
