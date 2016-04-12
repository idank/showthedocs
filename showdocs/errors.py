class NoAnnotatorFound(ValueError):
    def __init__(self, message):
        super(NoAnnotatorFound, self).__init__(message)
