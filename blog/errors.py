class BaseError:
    __slots__ = ('code', 'message')

    def __init__(self, code, message):
        self.code = code
        self.message = message


PERMISSION_FORBIDDEN = BaseError('ForBidden', '没有权限')

