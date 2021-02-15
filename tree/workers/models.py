from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Workers(MPTTModel):
    name = models.CharField(max_length=50, unique=True, verbose_name='Ф.И.О. работника')
    position = models.CharField(max_length=100, verbose_name='Должность')
    start_date = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Дата приёма на работу')
    salary = models.IntegerField(verbose_name='Зарплата')
    added_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    loaded = models.BooleanField(default=False, verbose_name='Флаг загрузки для JS')
    photo = models.ImageField(blank=True, upload_to='images', verbose_name='Фотография сотрудника')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return f'ID: {self.id}, Name:{self.name}, level: {self.level}'

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
