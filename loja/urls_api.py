from django.urls import path
from . import api

app_name = 'loja_api'

urlpatterns = [
    path('produtos/', api.produtos_api, name='produtos'),
    path('produtos/<slug:slug>/', api.produto_detalhe_api, name='produto_detalhe'),
    path('lojas/', api.lojas_api, name='lojas'),
]
