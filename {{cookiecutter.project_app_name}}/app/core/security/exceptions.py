class JWTDecodeError(Exception):
    pass


class JWTTokenInvalidError(Exception):
    pass


class JWTTokenExpiredError(Exception):
    pass


class AuthUserNotFoundError(Exception):
    pass


class AuthPasswordError(Exception):
    pass
