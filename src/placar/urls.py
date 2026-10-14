from django.urls import path

from . import views

app_name = 'placar'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('ranking/', views.ranking_json, name='ranking_json'),
    path('gerenciar/', views.gerenciar_pontos, name='gerenciar_pontos'),
    path(
        'gerenciar/total-pontos/',
        views.total_pontos_json,
        name='total_pontos_json',
    ),
]
