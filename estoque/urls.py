from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    # Produtos
    path('produtos/', views.produto_list_view, name='produto_list'),
    path('produtos/novo/', views.produto_create_view, name='produto_create'),
    path('produtos/<int:pk>/editar/', views.produto_update_view, name='produto_update'),
    path('produtos/<int:pk>/alternar-status/', views.produto_toggle_status_view, name='produto_toggle_status'),
    path('produtos/<int:produto_pk>/movimentar/', views.movimentacao_create_view, name='movimentacao_create'),
    path('movimentacoes/', views.movimentacao_list_view, name='movimentacao_list'),
    path('movimentacoes/nova/', views.movimentacao_geral_create_view, name='movimentacao_geral_create'),

    # Lojas (Admin Master)
    path('lojas/', views.loja_list_view, name='loja_list'),
    path('lojas/nova/', views.loja_create_view, name='loja_create'),
    path('lojas/<int:pk>/editar/', views.loja_update_view, name='loja_update'),
    path('lojas/<int:pk>/alternar-status/', views.loja_toggle_status_view, name='loja_toggle_status'),

    # Usuários (Admin Master)
    path('usuarios/', views.usuario_list_view, name='usuario_list'),
    path('usuarios/novo/', views.usuario_create_view, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_update_view, name='usuario_update'),
    path('usuarios/<int:pk>/alternar-status/', views.usuario_toggle_status_view, name='usuario_toggle_status'),

    # Exportação CSV
    path('exportar/produtos/', views.export_produtos_csv, name='export_produtos_csv'),
    path('exportar/movimentacoes/', views.export_movimentacoes_csv, name='export_movimentacoes_csv'),

    # Relatório PDF
    path('relatorio/mensal/pdf/', views.relatorio_mensal_pdf, name='relatorio_mensal_pdf'),
]
