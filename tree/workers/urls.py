from django.urls import path

from . import views

urlpatterns = [
    path('',                 views.index,            name='index'),
    path('index_v2/',        views.index_ver_two,    name='index_v2'),
    path('get_root_nodes/',  views.get_root_nodes,   name='get_root_nodes'),
    path('get_node_childs/', views.get_node_childs,  name='get_node_childs'),
    path('change_node/',     views.change_node,      name='change_node'),
    path('delete_node/',     views.delete_node,      name='delete_node'),
]
