import gzip
import ipaddress
import re
import abc
from pathlib import Path
from typing import Tuple, Union


class ValidationError(Exception):
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code


class PasswordValidator(abc.ABC):
    """密码校验器"""
    @abc.abstractmethod
    def validate(self, password: str):
        """如果密码校验不通过，抛出 ValidationError 异常"""
        pass


class MinimumLengthValidator(PasswordValidator):
    """校验密码长度是否符合要求"""
    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, password: str):
        if len(password) < self.min_length:
            raise ValidationError(
                f'密码太短了，应该包含至少{self.min_length}个字符。',
                code='PASSWORD_TOO_SHORT',
            )


class CommonPasswordValidator(PasswordValidator):
    """校验密码是否为常见的密码
    common-passwords.txt.gz 复制自 Django 项目，由 Royce Williams 创建并维护：
    https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7
    """
    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / 'common-passwords.txt.gz'

    def __init__(self, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
        try:
            with gzip.open(str(password_list_path)) as f:
                common_passwords_lines = f.read().decode().splitlines()
        except IOError:
            with open(str(password_list_path)) as f:
                common_passwords_lines = f.readlines()

        self.passwords = {p.strip() for p in common_passwords_lines}

    def validate(self, password):
        if password.lower().strip() in self.passwords:
            raise ValidationError('这个密码太常见了，建议更换。', code='PASSWORD_TOO_COMMON')


class NumericPasswordValidator(PasswordValidator):
    """校验密码是否由纯数字组成"""
    def validate(self, password: str):
        if password.isdigit():
            raise ValidationError('密码不应该由纯数字组成。', code='PASSWORD_ENTIRELY_NUMERIC')


PASSWORD_VALIDATORS = (
    MinimumLengthValidator(),
    CommonPasswordValidator(),
    NumericPasswordValidator(),
)


def validate_password(password: str, password_validators: Tuple[PasswordValidator] = None):
    """校验密码
    :return 密码可用，返回 None；密码不可用时会抛出异常 ValidationError
    """
    if password_validators is None:
        password_validators = PASSWORD_VALIDATORS
    for validator in password_validators:
        validator.validate(password)


def validate_ipv4_address(ip: Union[str, bytes, int]):
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise ValidationError('无效的 IPv4 地址', code='invalid')


def validate_ipv6_address(ip: Union[str, bytes, int]):
    try:
        ipaddress.IPv6Address(ip)
    except ValueError:
        raise ValidationError('无效的 IPv6 地址', code='invalid')


def validate_ip_address(value):
    try:
        validate_ipv4_address(value)
    except ValidationError:
        try:
            validate_ipv6_address(value)
        except ValidationError:
            raise ValidationError('无效的 IPv4 或 IPv6 地址', code='invalid')


class EmailValidator:
    message = '无效的 Email 地址！'
    code = 'INVALID_EMAIL'
    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)
    domain_regex = re.compile(
        # max length for domain name labels is 63 characters per RFC 1034
        r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
        re.IGNORECASE)
    literal_regex = re.compile(
        # literal form, ipv4 or ipv6 address (SMTP 4.1.3)
        r'\[([A-f0-9:\.]+)\]\Z',
        re.IGNORECASE)
    domain_whitelist = ('localhost',)

    def __init__(self, message: str = None, code: str = None, whitelist: Tuple[str] = None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if whitelist is not None:
            self.domain_whitelist = whitelist

    def __call__(self, value):
        if not value or '@' not in value:
            raise ValidationError(self.message, code=self.code)

        user_part, domain_part = value.rsplit('@', 1)

        if not self.user_regex.match(user_part):
            raise ValidationError(self.message, code=self.code)

        if (domain_part not in self.domain_whitelist and
                not self.validate_domain_part(domain_part)):
            try:
                domain_part = domain_part.encode('idna').decode('ascii')
            except UnicodeError:
                pass
            else:
                if self.validate_domain_part(domain_part):
                    return
            raise ValidationError(self.message, code=self.code)

    def validate_domain_part(self, domain_part):
        if self.domain_regex.match(domain_part):
            return True

        literal_match = self.literal_regex.match(domain_part)
        if literal_match:
            ip_address = literal_match.group(1)
            try:
                validate_ip_address(ip_address)
                return True
            except ValidationError:
                pass
        return False


validate_email = EmailValidator()
