from django.contrib.auth.models import AbstractUser
from django.db import models

from api.service_functions import check_username

EMAIL_FIELD_LENGTH = 254
USERNAME_FIELD_LENGTH = 150
FIRST_NAME_FIELD_LENGTH = 150
LAST_NAME_FIELD_LENGTH = 150


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=USERNAME_FIELD_LENGTH,
        blank=False,
        unique=True,
        validators=(check_username,),
        verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_FIELD_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=LAST_NAME_FIELD_LENGTH,
        verbose_name='Фамилия'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscriber',
        on_delete=models.CASCADE,
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribing',
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} {self.author}'
