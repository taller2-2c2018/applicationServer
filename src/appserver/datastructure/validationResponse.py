class ValidationResponse:
    def __init__(self, has_errors, message=""):
        self.hasErrors = has_errors
        self.message = message
