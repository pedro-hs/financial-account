from django.conf import settings
from rest_framework_jwt.utils import jwt_payload_handler


def custom_jwt(user):
    payload = jwt_payload_handler(user)
    payload['role'] = user.role

    return payload
