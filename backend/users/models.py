from django.contrib.auth.models import AbstractUser
from django.db import models

from . import constants
from .validators import check_username


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=constants.EMAIL_FIELD_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=constants.USERNAME_FIELD_LENGTH,
        blank=False,
        unique=True,
        validators=[check_username],
        verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(
        max_length=constants.FIRST_NAME_FIELD_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=constants.LAST_NAME_FIELD_LENGTH,
        verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

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
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_user_subscribing'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
