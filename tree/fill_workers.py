import datetime
import django
import json
import os
import random
import requests

os.environ["DJANGO_SETTINGS_MODULE"] = 'tree.settings'
django.setup()

from django.conf import settings
from workers.models import Workers


def get_random_date() -> datetime:
    """ Выдаёт рандомную (почти) дату... Несколько странная проверка на корректность даты, но ничего :) """

    while True:
        try:
            tmp_tuple = (random.randint(2010, 2020), random.randint(1, 12), random.randint(1, 31))
            rez = datetime.datetime(tmp_tuple[0], tmp_tuple[1], tmp_tuple[2])
        except Exception as ex:
            print(ex, f'Неверная сгенерированная дата - {tmp_tuple}')
            continue
        return rez


def get_dict_names(count_names=1):
    """
    Запрашивает на randomdatatools.ru фамилию, имя, отчество и отдаёт их в списке словарей
    Количество данных в словаре - равно входному параметру
    """

    r = requests.get(f'https://api.randomdatatools.ru/?count={count_names}&params=LastName,FirstName,FatherName')
    if count_names == 1:
        return [json.loads(r.text)]
    else:
        return json.loads(r.text)


def get_random_salary(level_worker) -> int:
    """
    Выдаёт рандомную (типа) зарплату. Для нулевого уровня - просто выбирает из списка, для нижних уровней - уменьшает
    на 10000 за каждый уровень.
    Надеюсь ниже 10 уровней не потребуется :).
    """

    out_salary = random.choice([100000, 101000, 102000, 103000, 104000, 105000, 106000, 107000, 108000, 109000])
    return int(out_salary - (10000 * level_worker))


def load_worker_photo(worker_id):
    """
    Загружает фотографию с ресурса https://thispersondoesnotexist.com сохраняет в файл с именем входного параметра
    """

    url_img = 'https://thispersondoesnotexist.com/image'

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
               'Accept': 'image/webp,*/*',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'Referer': 'https://thispersondoesnotexist.com/'}

    img_req = requests.get(url_img, headers=headers, stream=True)

    img_file_name = os.path.join(settings.MEDIA_ROOT, 'images', f'{str(worker_id)}.jpg')
    with open(img_file_name, 'bw') as img_file:
        for chunk in img_req.iter_content(8192):
            img_file.write(chunk)
    return os.path.join('images', f'{str(worker_id)}.jpg')


def add_worker(level_worker):
    """ Добавляет одного сотрудника указанного уровня """

    list_name_worker = get_dict_names()
    name_worker = f'{list_name_worker[0]["LastName"]} {list_name_worker[0]["FirstName"]} ' \
                  f'{list_name_worker[0]["FatherName"]}'
    if level_worker:
        # Если уровень добавляемого сотрудника >0 то должны быть родители,
        # их нужно выбрать из сотрудников уровня выше.
        parent = random.choice(Workers.objects.filter(level=level_worker-1))
    else:
        parent = None

    new_worker = Workers(name=name_worker, position=f'Должность уровня {level_worker}', start_date=get_random_date(),
                         salary=get_random_salary(level_worker), parent=parent)
    new_worker.save()
    # Сначала сохраняем полученные текстовые данные, чтобы получить id записи
    # Фото сотрудника сохраняем с именем id.jpg сотрудника
    new_worker.photo = load_worker_photo(new_worker.id)
    new_worker.save()
    print(f'Записан сотрудник уровня {level_worker}, id - {new_worker.id}, name - {new_worker.name}')


def add_workers(level_workers=0, count_workers=5):
    """ Цикл добавления сотрудников указанного уровня. По-умолчанию добавляет 5 сотрудников нулевого уровня """

    for count_worker in range(count_workers):
        add_worker(level_workers)


def main():
    """ Функция заполнения базы """

    add_workers(count_workers=5)
    add_workers(level_workers=1, count_workers=10)
    add_workers(level_workers=2, count_workers=10)
    add_workers(level_workers=3, count_workers=10)
    add_workers(level_workers=4, count_workers=10)


if __name__ == '__main__':
    main()
