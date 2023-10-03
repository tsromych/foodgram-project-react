import re

from rest_framework import serializers


def check_username(username):
    invalid_username = ['me']
    if username in invalid_username:
        raise serializers.ValidationError(
            'Введенное имя недопустимо!'
        )
    if not re.match(r'[\w.@+-]+\Z', username):
        raise serializers.ValidationError(
            'В имени использованы недопустимые символы!'
        )
    return username
