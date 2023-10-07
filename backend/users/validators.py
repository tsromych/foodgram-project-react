import re

from django.core.exceptions import ValidationError


def check_username(username):
    invalid_username = ['me']
    if username in invalid_username:
        raise ValidationError(
            'Введенное имя недопустимо!'
        )
    if not re.match(r'[\w.@+-]+\Z', username):
        raise ValidationError(
            'В имени использованы недопустимые символы!'
        )
    return username
