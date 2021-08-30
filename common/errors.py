from rest_framework.exceptions import APIException


class BadRequest(APIException):
    def __init__(self, message=''):
        setattr('status_code', 400)
        setattr('default_detail', message)
        setattr('default_code', 'bad_request')
