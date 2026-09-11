from django.contrib import admin
from .models import Loja, Produto, ProdutoFoto, MovimentacaoEstoque

class ProdutoFotoInline(admin.TabularInline):
    model = ProdutoFoto
    extra = 1
    max_num = 4

@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'responsavel', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome', 'responsavel__username', 'responsavel__email')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'loja', 'sku', 'preco_custo', 'preco_venda', 'quantidade_atual', 'ativo')
    list_filter = ('loja', 'ativo')
    search_fields = ('nome', 'slug', 'sku', 'loja__nome')
    prepopulated_fields = {'slug': ('nome',)}
    inlines = [ProdutoFotoInline]

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'preco_venda_unitario', 'forma_pagamento', 'parcelas', 'usuario', 'criado_em')
    list_filter = ('tipo', 'forma_pagamento', 'produto__loja')
    search_fields = ('produto__nome', 'usuario__username', 'observacao')
    readonly_fields = ('criado_em',)
