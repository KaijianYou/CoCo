class Constant:
    class _ConstantError(TypeError):
        pass

    class _ConstantCaseError(_ConstantError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise self._ConstantError(f'Cannot change constant {key}')
        if not key.isupper():
            raise self._ConstantCaseError(f'Constant name {key} is not all uppercase')
        self.__dict__[key] = value
