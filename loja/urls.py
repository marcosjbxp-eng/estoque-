from django.urls import path
from . import views

app_name = 'loja'

urlpatterns = [
    path('', views.catalogo_view, name='catalogo'),
    path('produto/<slug:slug>/', views.produto_detalhe_view, name='produto_detalhe'),
    path('<slug:slug>/', views.produto_detalhe_view, name='produto_detalhe_legacy'),
]

