import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.db import transaction
from django.utils import timezone

from .models import Loja, Produto, ProdutoFoto, MovimentacaoEstoque
from .forms import ProdutoForm, ProdutoFotoFormSet, MovimentacaoEstoqueForm
from .mixins import is_admin_master, get_user_lojas


@login_required
def dashboard_view(request):
    user_lojas = get_user_lojas(request.user)
    selected_loja_id = request.GET.get('loja_id')

    # Query base para saídas
    saidas_qs = MovimentacaoEstoque.objects.filter(
        tipo=MovimentacaoEstoque.TIPO_SAIDA,
        preco_venda_unitario__isnull=False
    )

    if not is_admin_master(request.user):
        saidas_qs = saidas_qs.filter(produto__loja__in=user_lojas)
    elif selected_loja_id:
        saidas_qs = saidas_qs.filter(produto__loja_id=selected_loja_id)

    # Cálculo do Lucro Acumulado Total
    lucro_total = Decimal('0.00')
    total_saidas_qtd = 0
    total_vendas_valor = Decimal('0.00')

    for mov in saidas_qs.select_related('produto'):
        lucro_total += mov.lucro
        total_saidas_qtd += mov.quantidade
        total_vendas_valor += (mov.preco_venda_unitario * mov.quantidade)

    # Cálculo de Lucro Mensal (Últimos 12 Meses)
    hoje = timezone.now().date()
    meses_labels = []
    lucros_mensais = []

    for i in range(11, -1, -1):
        # Calcular primeiro e último dia do mês correspondente
        mes_dt = hoje.replace(day=1) - timedelta(days=i*30)
        ano = mes_dt.year
        mes = mes_dt.month
        nome_mes = mes_dt.strftime('%b/%Y')
        meses_labels.append(nome_mes)

        movs_mes = saidas_qs.filter(criado_em__year=ano, criado_em__month=mes).select_related('produto')
        lucro_mes = sum((m.lucro for m in movs_mes), Decimal('0.00'))
        lucros_mensais.append(float(lucro_mes))

    # Comparativo por Loja (Admin Master)
    lojas_labels = []
    lojas_lucros = []

    if is_admin_master(request.user):
        todas_lojas = Loja.objects.filter(ativo=True)
        for loja in todas_lojas:
            movs_loja = MovimentacaoEstoque.objects.filter(
                tipo=MovimentacaoEstoque.TIPO_SAIDA,
                produto__loja=loja,
                preco_venda_unitario__isnull=False
            ).select_related('produto')
            lucro_l = sum((m.lucro for m in movs_loja), Decimal('0.00'))
            lojas_labels.append(loja.nome)
            lojas_lucros.append(float(lucro_l))

    # Produtos mais rentáveis
    produtos_qs = Produto.objects.filter(ativo=True)
    if not is_admin_master(request.user):
        produtos_qs = produtos_qs.filter(loja__in=user_lojas)
    elif selected_loja_id:
        produtos_qs = produtos_qs.filter(loja_id=selected_loja_id)

    total_produtos = produtos_qs.count()
    total_estoque_unidades = produtos_qs.aggregate(total=Sum('quantidade_atual'))['total'] or 0

    context = {
        'lucro_total': lucro_total,
        'total_vendas_valor': total_vendas_valor,
        'total_saidas_qtd': total_saidas_qtd,
        'total_produtos': total_produtos,
        'total_estoque_unidades': total_estoque_unidades,
        'selected_loja_id': selected_loja_id,
        'lojas_filtro': Loja.objects.filter(ativo=True) if is_admin_master(request.user) else [],
        'chart_meses_json': json.dumps(meses_labels),
        'chart_lucros_json': json.dumps(lucros_mensais),
        'chart_lojas_json': json.dumps(lojas_labels),
        'chart_lojas_lucros_json': json.dumps(lojas_lucros),
    }

    return render(request, 'estoque/dashboard.html', context)


@login_required
def produto_list_view(request):
    user_lojas = get_user_lojas(request.user)
    query = request.GET.get('q', '').strip()
    loja_id = request.GET.get('loja_id', '')

    produtos = Produto.objects.select_related('loja').prefetch_related('fotos_secundarias')

    if not is_admin_master(request.user):
        produtos = produtos.filter(loja__in=user_lojas)
    elif loja_id:
        produtos = produtos.filter(loja_id=loja_id)

    if query:
        produtos = produtos.filter(
            Q(nome__icontains=query) | Q(sku__icontains=query) | Q(descricao__icontains=query)
        )

    context = {
        'produtos': produtos,
        'query': query,
        'selected_loja_id': loja_id,
        'lojas_filtro': Loja.objects.filter(ativo=True) if is_admin_master(request.user) else [],
    }
    return render(request, 'estoque/produto_list.html', context)


@login_required
def produto_create_view(request):
    user_lojas = get_user_lojas(request.user)

    if not user_lojas.exists():
        messages.error(request, "Você não possui nenhuma loja associada para cadastrar produtos.")
        return redirect('estoque:produto_list')

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, user=request.user)
        formset = ProdutoFotoFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            loja = form.cleaned_data['loja']
            if not is_admin_master(request.user) and loja.responsavel != request.user:
                raise PermissionDenied("Operação não permitida para esta loja.")

            with transaction.atomic():
                produto = form.save()
                formset.instance = produto
                formset.save()

            messages.success(request, f"Produto '{produto.nome}' cadastrado com sucesso!")
            return redirect('estoque:produto_list')
    else:
        form = ProdutoForm(user=request.user)
        formset = ProdutoFotoFormSet()

    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Cadastrar Novo Produto',
    }
    return render(request, 'estoque/produto_form.html', context)


@login_required
def produto_update_view(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    # Validar isolamento de loja no backend
    if not is_admin_master(request.user) and produto.loja.responsavel != request.user:
        raise PermissionDenied("Você não tem permissão para editar produtos desta loja.")

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto, user=request.user)
        formset = ProdutoFotoFormSet(request.POST, request.FILES, instance=produto)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()

            messages.success(request, f"Produto '{produto.nome}' atualizado com sucesso!")
            return redirect('estoque:produto_list')
    else:
        form = ProdutoForm(instance=produto, user=request.user)
        formset = ProdutoFotoFormSet(instance=produto)

    context = {
        'form': form,
        'formset': formset,
        'produto': produto,
        'titulo': f"Editar Produto — {produto.nome}",
    }
    return render(request, 'estoque/produto_form.html', context)


@login_required
def produto_toggle_status_view(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    if not is_admin_master(request.user) and produto.loja.responsavel != request.user:
        raise PermissionDenied("Você não tem permissão para alterar o status deste produto.")

    produto.ativo = not produto.ativo
    produto.save(update_fields=['ativo'])

    status_str = "ativado" if produto.ativo else "desativado"
    messages.info(request, f"Produto '{produto.nome}' foi {status_str} com sucesso.")
    return redirect('estoque:produto_list')


@login_required
def movimentacao_create_view(request, produto_pk):
    produto = get_object_or_404(Produto, pk=produto_pk)

    if not is_admin_master(request.user) and produto.loja.responsavel != request.user:
        raise PermissionDenied("Você não tem permissão para movimentar o estoque deste produto.")

    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST, produto=produto)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.produto = produto
            movimentacao.usuario = request.user
            movimentacao.save()  # Dispara o sinal que atualiza quantidade_atual

            messages.success(
                request,
                f"Movimentação de {movimentacao.get_tipo_display()} registrada com sucesso para {produto.nome}!"
            )
            return redirect('estoque:produto_list')
    else:
        form = MovimentacaoEstoqueForm(produto=produto)

    context = {
        'form': form,
        'produto': produto,
    }
    return render(request, 'estoque/movimentacao_form.html', context)


@login_required
def movimentacao_list_view(request):
    user_lojas = get_user_lojas(request.user)
    loja_id = request.GET.get('loja_id', '')
    tipo = request.GET.get('tipo', '')
    query = request.GET.get('q', '').strip()

    movimentacoes = MovimentacaoEstoque.objects.select_related('produto', 'produto__loja', 'usuario')

    if not is_admin_master(request.user):
        movimentacoes = movimentacoes.filter(produto__loja__in=user_lojas)
    elif loja_id:
        movimentacoes = movimentacoes.filter(produto__loja_id=loja_id)

    if tipo:
        movimentacoes = movimentacoes.filter(tipo=tipo)

    if query:
        movimentacoes = movimentacoes.filter(
            Q(produto__nome__icontains=query) | Q(observacao__icontains=query)
        )

    context = {
        'movimentacoes': movimentacoes,
        'selected_loja_id': loja_id,
        'selected_tipo': tipo,
        'query': query,
        'lojas_filtro': Loja.objects.filter(ativo=True) if is_admin_master(request.user) else [],
    }
    return render(request, 'estoque/movimentacao_list.html', context)
