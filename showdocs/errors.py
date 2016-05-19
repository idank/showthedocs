class NoAnnotatorFound(ValueError):
    def __init__(self, message):
        super(NoAnnotatorFound, self).__init__(message)

class ParsingError(Exception):
    def __init__(self, message, s, position):
        if position >= len(s):
            raise ValueError('position %d not within string %r' %
                             (position, s))
        self.message = message or 'parser gave no additional information'
        self.s = s
        self.position = position

        super(ParsingError, self).__init__('%s (position %d)' %
                                           (self.message, position))
