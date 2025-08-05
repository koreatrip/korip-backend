from rest_framework.exceptions import APIException
from rest_framework import status

class EmailError(APIException):

    def __init__(self, errorcode, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = {
            "error_code": errorcode.code,
            "error_message": errorcode.message
        }
        self.status_code = status_code


class AuthenticationError(APIException):
    default_code = "AUTHENTICATION_ERROR"

    def __init__(self, errorcode, status_code=status.HTTP_401_UNAUTHORIZED):
        self.detail = {
            "error_code": errorcode.code,
            "error_message": errorcode.message
        }
        self.status_code = status_code

class CustomTokenError(APIException):
    default_code = "CUSTOM_TOKEN_ERROR"

    def __init__(self, errorcode, status_code=status.HTTP_401_UNAUTHORIZED):
        self.detail = {
            "error_code": errorcode.code,
            "error_message": errorcode.message
        }
        self.status_code = status_code

class UserError(APIException):
    default_code = "USER_ERROR"

    def __init__(self, errorcode, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = {
            "error_code": errorcode.code,
            "error_message": errorcode.message
        }
        self.status_code = status_code

class RequestError(APIException):
    default_code = "REQUEST_ERROR"

    def __init__(self, errorcode, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = {
            "error_code": errorcode.code,
            "error_message": errorcode.message
        }
        self.status_code = status_code