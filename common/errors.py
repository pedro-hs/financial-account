from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = 400
    default_detail = ''
    default_code = 'bad_requestl'

    def __init__(self, detail, message=''):
        self.detail = detail
        self.default_detail = message
