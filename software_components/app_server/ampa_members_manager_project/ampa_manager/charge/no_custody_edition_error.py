class NoCustodyEditionError(Exception):
    def __init__(self):
        super().__init__("NoCustodyEditionError")
