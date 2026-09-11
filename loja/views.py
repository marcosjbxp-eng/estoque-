from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from estoque.models import Produto, Loja


def catalogo_view(request):
    """
    Exibe os produtos disponíveis na Loja.
    URL: /loja/
    """
    query = request.GET.get('q', '').strip()
    loja_id = request.GET.get('loja', '').strip()

    produtos = Produto.objects.filter(ativo=True).select_related('loja').order_by('-criado_em')

    if query:
        produtos = produtos.filter(
            Q(nome__icontains=query) | Q(descricao__icontains=query)
        )

    if loja_id:
        produtos = produtos.filter(loja_id=loja_id)

    lojas = Loja.objects.filter(ativo=True)

    context = {
        'produtos': produtos,
        'query': query,
        'lojas': lojas,
        'selected_loja_id': loja_id,
        'total_produtos': produtos.count(),
    }
    return render(request, 'loja/catalogo.html', context)


def produto_detalhe_view(request, slug):
    """
    Exibe a página de detalhes de um produto específico através de sua URL personalizada (slug).
    URL: /loja/<slug>/
    """
    # Tenta obter pelo slug; fallback por ID caso seja numérico
    if slug.isdigit():
        produto = get_object_or_404(
            Produto.objects.filter(ativo=True).select_related('loja').prefetch_related('fotos_secundarias'),
            Q(slug=slug) | Q(pk=int(slug))
        )
    else:
        produto = get_object_or_404(
            Produto.objects.filter(ativo=True).select_related('loja').prefetch_related('fotos_secundarias'),
            slug=slug
        )

    produtos_relacionados = Produto.objects.filter(
        ativo=True,
        loja=produto.loja
    ).exclude(pk=produto.pk)[:4]

    context = {
        'produto': produto,
        'fotos_secundarias': produto.fotos_secundarias.all(),
        'produtos_relacionados': produtos_relacionados,
    }
    return render(request, 'loja/detalhe.html', context)


# Aliases para compatibilidade de rotas e templates clássicos
catalogo = catalogo_view
produto_detalhe = produto_detalhe_view

