import csv

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка данных из CSV файла в базу данных."""
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
                'Начинаем загрузку данных из CSV файла...'))

        try:
            with open(
                './data/ingredients.csv', mode='r', encoding='utf-8'
            ) as file:
                reader = csv.reader(file)
                ingredients = [
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in reader
                ]
                Ingredient.objects.bulk_create(ingredients)
        except IntegrityError:
            print('Ошибка при импорте данных в базу!')
        except FileNotFoundError:
            print('Файл не найден!')

        self.stdout.write(self.style.SUCCESS('Загрузка данных завершена!'))
