import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from .models import Workers


def index(request):
    """ Разные подходы выдачи index-страницы:
        Здесь сначала загружается пустая страница с которой через axios идёт ajax запрос
    """

    return render(request, 'base.html', {'serverUrl': settings.SERVER_URL})


def index_ver_two(request):
    """ Разные подходы выдачи index-страницы:
        Здесь страница рендерится с уже встроенным json-списком, который передаётся в vue
    """

    return render(request, 'base_two.html', {'tree': return_begin_levels_tree(levels=2),
                                             'serverUrl': settings.SERVER_URL})


def get_list_child(input_item, max_nested_level, current_nested_level=1) -> list:
    """ Рекурсивная функция вибирает вложенные уровни от input_item и возвращает в виде списка.
        Ограничение на вложенность - max_nested_level
    """

    if input_item.is_leaf_node() or max_nested_level <= current_nested_level:
        return []
    rezult_list = list(input_item.get_children().values())
    for num, item in enumerate(input_item.get_children()):
        rezult_list[num]['children'] = get_list_child(item, max_nested_level, current_nested_level+1)
    return rezult_list


def return_begin_levels_tree(levels=1) -> list:
    """ Выбирает верхний (корневой) уровень дерева, и возвращает в виде списка """

    root_level = Workers.objects.filter(level=0)
    list_root_level = list(root_level.values())
    for num, item in enumerate(root_level):
        list_root_level[num]['children'] = get_list_child(item, levels)

    return list_root_level


def get_root_nodes(request):
    """ Возвращает json на ajax при загрузке страницы. """

    if request.is_ajax():
        return JsonResponse({'nodes': return_begin_levels_tree(levels=2)})
    else:
        return JsonResponse({'error': 'Тип запроса не поддерживается'}, status=400)


def get_node_childs(request):
    """ Вызывается для загрузке дочерних элементов при открытии узлов дерева """

    if request.is_ajax():
        input_json = json.loads(request.body)
        current_node = Workers.objects.get(id=input_json['node_id'])
        return JsonResponse({'children': get_list_child(current_node, max_nested_level=3)})
    else:
        return JsonResponse({'error': 'Тип запроса не поддерживается'}, status=400)


def change_node(request):
    """ Изменение данных узла. Изменяются ФИО, должность, зарплата и дата приёма на работу """

    if request.is_ajax():
        input_json = json.loads(request.body)
        try:
            changed_node = Workers.objects.get(id=input_json['id'])
            changed_node.name = input_json['name']
            changed_node.position = input_json['position']
            changed_node.salary = input_json['salary']
            changed_node.start_date = input_json['start_date']
            changed_node.save()
        except Exception as e:
            return JsonResponse({'state': 'bad', 'exception': e})
        return JsonResponse({'state': 'ok'})
    else:
        return JsonResponse({'error': 'Тип запроса не поддерживается'}, status=400)


def move_children(children, new_parent_node):
    """ Функция переносит детей к другому родителю.
        Применяется при удалении ноды у которой есть дети. В этом случае все дети переносятся родителю удаляемой ноды
        Если в качестве new_parent_node приходит None, то дети становятся рутовыми нодами.
    """

    current_child = Workers.objects.get(id=children.id)
    current_child.move_to(new_parent_node, 'last-child')
    current_child.save()


def delete_node(request):
    """  Удаление ноды.
        Единственный вопрос - что делать с детьми удаляемой ноды.
        Решение - мы их переносим на уровень выше.
    """

    if request.is_ajax():
        input_json = json.loads(request.body)
        deleted_node = Workers.objects.get(id=input_json['id'])
        # Если удаляемая нода - рутовая, то в качестве будущего родителя нужно отправить None,
        # тогда все дети станут рутовыми нодами.
        if deleted_node.is_root_node():
            for deleted_node_child in deleted_node.get_children():
                move_children(deleted_node_child, None)
        else:
            for deleted_node_child in deleted_node.get_children():
                move_children(deleted_node_child, deleted_node.parent)
        deleted_node.delete()
        return JsonResponse({'state': 'ok'})
    else:
        return JsonResponse({'error': 'Тип запроса не поддерживается'}, status=400)

