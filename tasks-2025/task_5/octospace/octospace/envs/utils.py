class NoSpaceOnMapException(Exception):
    def __init__(self, message):
        super().__init__(message)

class EffectError(Exception):
    def __init__(self, message):
        super().__init__(message)
