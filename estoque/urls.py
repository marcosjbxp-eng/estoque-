from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('produtos/', views.produto_list_view, name='produto_list'),
    path('produtos/novo/', views.produto_create_view, name='produto_create'),
    path('produtos/<int:pk>/editar/', views.produto_update_view, name='produto_update'),
    path('produtos/<int:pk>/alternar-status/', views.produto_toggle_status_view, name='produto_toggle_status'),
    path('produtos/<int:produto_pk>/movimentar/', views.movimentacao_create_view, name='movimentacao_create'),
    path('movimentacoes/', views.movimentacao_list_view, name='movimentacao_list'),
]
