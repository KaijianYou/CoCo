class Constant:
    class _ConstantError(TypeError):
        pass

    class _CosntantCaseError(_ConstantError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise self._ConstantError(f'Cannot change constant {key}')
        if not key.isupper():
            raise self._ConstantCaseError(f'Constant name {key} is not alll uppercase')
        self.__dict__[key] = value
