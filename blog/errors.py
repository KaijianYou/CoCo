class BaseError:
    def __init__(self, code, message):
        self.code = code
        self.message = message


class PermissionError:
    Forbidden = BaseError('Forbidden', '没有权限')