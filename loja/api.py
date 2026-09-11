from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from estoque.models import Produto, Loja

def produtos_api(request):
    """
    Lista todos os produtos ativos.
    Aceita parâmetros:
    - q: string de busca
    - loja: id da loja
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

    data = []
    for p in produtos:
        data.append({
            'id': p.id,
            'nome': p.nome,
            'slug': p.slug,
            'descricao': p.descricao,
            'preco_venda': float(p.preco_venda) if p.preco_venda else 0.0,
            'quantidade_atual': p.quantidade_atual,
            'loja_id': p.loja.id,
            'loja_nome': p.loja.nome,
            'foto_principal': p.foto_principal.url if p.foto_principal else None,
        })
    
    return JsonResponse({'produtos': data})

def produto_detalhe_api(request, slug):
    """
    Detalhes de um produto específico.
    """
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

    fotos_secundarias = [f.foto.url for f in produto.fotos_secundarias.all()]
    
    # Produtos Relacionados (mesma loja)
    relacionados_qs = Produto.objects.filter(
        ativo=True,
        loja=produto.loja
    ).exclude(pk=produto.pk)[:4]
    
    relacionados = []
    for r in relacionados_qs:
        relacionados.append({
            'id': r.id,
            'nome': r.nome,
            'slug': r.slug,
            'preco_venda': float(r.preco_venda) if r.preco_venda else 0.0,
            'foto_principal': r.foto_principal.url if r.foto_principal else None,
        })

    data = {
        'id': produto.id,
        'nome': produto.nome,
        'slug': produto.slug,
        'descricao': produto.descricao,
        'preco_venda': float(produto.preco_venda) if produto.preco_venda else 0.0,
        'quantidade_atual': produto.quantidade_atual,
        'loja_id': produto.loja.id,
        'loja_nome': produto.loja.nome,
        'foto_principal': produto.foto_principal.url if produto.foto_principal else None,
        'fotos_secundarias': fotos_secundarias,
        'relacionados': relacionados
    }

    return JsonResponse({'produto': data})

def lojas_api(request):
    """
    Lista de lojas ativas para o filtro.
    """
    lojas = Loja.objects.filter(ativo=True).order_by('nome')
    data = [{'id': l.id, 'nome': l.nome} for l in lojas]
    return JsonResponse({'lojas': data})
