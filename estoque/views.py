import json
import csv
from decimal import Decimal
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q, Count
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Loja, Produto, ProdutoFoto, MovimentacaoEstoque
from .forms import (
    ProdutoForm, ProdutoFotoFormSet, MovimentacaoEstoqueForm, MovimentacaoEstoqueGeralForm,
    LojaForm, UsuarioForm, UsuarioCreateForm, UsuarioEditForm,
)
from .mixins import is_admin_master, get_user_lojas
from .relatorio_pdf import gerar_relatorio_pdf


@login_required
def dashboard_view(request):
    user_lojas = get_user_lojas(request.user)
    selected_loja_id = request.GET.get('loja_id')

    # Query base para saÃ­das
    saidas_qs = MovimentacaoEstoque.objects.filter(
        tipo=MovimentacaoEstoque.TIPO_SAIDA,
        preco_venda_unitario__isnull=False
    )

    if not is_admin_master(request.user):
        saidas_qs = saidas_qs.filter(produto__loja__in=user_lojas)
    elif selected_loja_id:
        saidas_qs = saidas_qs.filter(produto__loja_id=selected_loja_id)

    # CÃ¡lculo do Lucro Acumulado Total
    lucro_total = Decimal('0.00')
    total_saidas_qtd = 0
    total_vendas_valor = Decimal('0.00')

    for mov in saidas_qs.select_related('produto'):
        lucro_total += mov.lucro
        total_saidas_qtd += mov.quantidade
        total_vendas_valor += (mov.preco_venda_unitario * mov.quantidade)

    # CÃ¡lculo de Lucro Mensal (Ãšltimos 12 Meses)
    hoje = timezone.now().date()
    meses_labels = []
    lucros_mensais = []

    for i in range(11, -1, -1):
        # Calcular primeiro e Ãºltimo dia do mÃªs correspondente
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

    # Produtos mais rentÃ¡veis
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

    paginator = Paginator(produtos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'produtos': page_obj,
        'page_obj': page_obj,
        'query': query,
        'selected_loja_id': loja_id,
        'lojas_filtro': Loja.objects.filter(ativo=True) if is_admin_master(request.user) else [],
    }
    return render(request, 'estoque/produto_list.html', context)


@login_required
def produto_create_view(request):
    user_lojas = get_user_lojas(request.user)

    if not user_lojas.exists():
        messages.error(request, "VocÃª nÃ£o possui nenhuma loja associada para cadastrar produtos.")
        return redirect('estoque:produto_list')

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, user=request.user)
        formset = ProdutoFotoFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            loja = form.cleaned_data['loja']
            if not is_admin_master(request.user) and loja.responsavel != request.user:
                raise PermissionDenied("OperaÃ§Ã£o nÃ£o permitida para esta loja.")

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
        raise PermissionDenied("VocÃª nÃ£o tem permissÃ£o para editar produtos desta loja.")

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
        'titulo': f"Editar Produto â€” {produto.nome}",
    }
    return render(request, 'estoque/produto_form.html', context)


@require_POST
@login_required
def produto_toggle_status_view(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    if not is_admin_master(request.user) and produto.loja.responsavel != request.user:
        raise PermissionDenied("VocÃª nÃ£o tem permissÃ£o para alterar o status deste produto.")

    produto.ativo = not produto.ativo
    produto.save(update_fields=['ativo'])

    status_str = "ativado" if produto.ativo else "desativado"
    messages.info(request, f"Produto '{produto.nome}' foi {status_str} com sucesso.")
    return redirect('estoque:produto_list')


@login_required
def movimentacao_create_view(request, produto_pk):
    produto = get_object_or_404(Produto, pk=produto_pk)

    if not is_admin_master(request.user) and produto.loja.responsavel != request.user:
        raise PermissionDenied("VocÃª nÃ£o tem permissÃ£o para movimentar o estoque deste produto.")

    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST, produto=produto)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.produto = produto
            movimentacao.usuario = request.user
            movimentacao.save()  # Dispara o sinal que atualiza quantidade_atual

            messages.success(
                request,
                f"MovimentaÃ§Ã£o de {movimentacao.get_tipo_display()} registrada com sucesso para {produto.nome}!"
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

    paginator = Paginator(movimentacoes, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # OpÃ§Ãµes para o painel de download PDF
    hoje = timezone.now().date()
    meses_opcoes = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'MarÃ§o'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]
    ano_atual = hoje.year
    anos_opcoes = list(range(ano_atual, ano_atual - 5, -1))

    context = {
        'movimentacoes': page_obj,
        'page_obj': page_obj,
        'selected_loja_id': loja_id,
        'selected_tipo': tipo,
        'query': query,
        'lojas_filtro': Loja.objects.filter(ativo=True) if is_admin_master(request.user) else [],
        'meses_opcoes': meses_opcoes,
        'mes_atual': hoje.month,
        'ano_atual': ano_atual,
        'anos_opcoes': anos_opcoes,
    }
    return render(request, 'estoque/movimentacao_list.html', context)


# ============================================================================
# CRUD de Lojas (Admin Master)
# ============================================================================

@login_required
def loja_list_view(request):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode gerenciar lojas.")

    lojas = Loja.objects.annotate(
        total_produtos=Count('produtos'),
    ).select_related('responsavel').order_by('nome')

    context = {'lojas': lojas}
    return render(request, 'estoque/loja_list.html', context)


@login_required
def loja_create_view(request):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode criar lojas.")

    if request.method == 'POST':
        form = LojaForm(request.POST)
        if form.is_valid():
            loja = form.save()
            messages.success(request, f"Loja '{loja.nome}' criada com sucesso!")
            return redirect('estoque:loja_list')
    else:
        form = LojaForm()

    context = {'form': form, 'titulo': 'Cadastrar Nova Loja'}
    return render(request, 'estoque/loja_form.html', context)


@login_required
def loja_update_view(request, pk):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode editar lojas.")

    loja = get_object_or_404(Loja, pk=pk)

    if request.method == 'POST':
        form = LojaForm(request.POST, instance=loja)
        if form.is_valid():
            form.save()
            messages.success(request, f"Loja '{loja.nome}' atualizada com sucesso!")
            return redirect('estoque:loja_list')
    else:
        form = LojaForm(instance=loja)

    context = {'form': form, 'loja': loja, 'titulo': f'Editar Loja â€” {loja.nome}'}
    return render(request, 'estoque/loja_form.html', context)


@require_POST
@login_required
def loja_toggle_status_view(request, pk):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode alterar o status de lojas.")

    loja = get_object_or_404(Loja, pk=pk)
    loja.ativo = not loja.ativo
    loja.save(update_fields=['ativo'])

    status_str = "ativada" if loja.ativo else "desativada"
    messages.info(request, f"Loja '{loja.nome}' foi {status_str} com sucesso.")
    return redirect('estoque:loja_list')


# ============================================================================
# GestÃ£o de UsuÃ¡rios (Admin Master)
# ============================================================================

@login_required
def usuario_list_view(request):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode gerenciar usuÃ¡rios.")

    usuarios = User.objects.prefetch_related('lojas', 'groups').order_by('username')

    context = {'usuarios': usuarios}
    return render(request, 'estoque/usuario_list.html', context)


@login_required
def usuario_create_view(request):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode criar usuÃ¡rios.")

    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"UsuÃ¡rio '{user.username}' criado com sucesso!")
            return redirect('estoque:usuario_list')
    else:
        form = UsuarioCreateForm()

    context = {'form': form, 'titulo': 'Criar Novo UsuÃ¡rio'}
    return render(request, 'estoque/usuario_form.html', context)


@login_required
def usuario_update_view(request, pk):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode editar usuÃ¡rios.")

    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"UsuÃ¡rio '{usuario.username}' atualizado com sucesso!")
            return redirect('estoque:usuario_list')
    else:
        form = UsuarioEditForm(instance=usuario)

    context = {'form': form, 'usuario': usuario, 'titulo': f'Editar UsuÃ¡rio â€” {usuario.username}'}
    return render(request, 'estoque/usuario_form.html', context)


@require_POST
@login_required
def usuario_toggle_status_view(request, pk):
    if not is_admin_master(request.user):
        raise PermissionDenied("Apenas Admin Master pode alterar o status de usuÃ¡rios.")

    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, "VocÃª nÃ£o pode desativar a si mesmo.")
        return redirect('estoque:usuario_list')

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=['is_active'])

    status_str = "ativado" if usuario.is_active else "desativado"
    messages.info(request, f"UsuÃ¡rio '{usuario.username}' foi {status_str} com sucesso.")
    return redirect('estoque:usuario_list')


# ============================================================================
# ExportaÃ§Ã£o CSV
# ============================================================================

@login_required
def export_produtos_csv(request):
    user_lojas = get_user_lojas(request.user)
    produtos = Produto.objects.select_related('loja')

    if not is_admin_master(request.user):
        produtos = produtos.filter(loja__in=user_lojas)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produtos.csv"'
    response.write('\ufeff')  # BOM for Excel UTF-8

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nome', 'SKU', 'Loja', 'PreÃ§o Custo', 'PreÃ§o Venda', 'Estoque Atual', 'Status', 'Criado em'])

    for p in produtos:
        writer.writerow([
            p.nome,
            p.sku or 'N/A',
            p.loja.nome,
            f'{p.preco_custo:.2f}',
            f'{p.preco_venda:.2f}',
            p.quantidade_atual,
            'Ativo' if p.ativo else 'Inativo',
            p.criado_em.strftime('%d/%m/%Y %H:%M'),
        ])

    return response


@login_required
def export_movimentacoes_csv(request):
    user_lojas = get_user_lojas(request.user)
    movimentacoes = MovimentacaoEstoque.objects.select_related('produto', 'produto__loja', 'usuario')

    if not is_admin_master(request.user):
        movimentacoes = movimentacoes.filter(produto__loja__in=user_lojas)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="movimentacoes.csv"'
    response.write('\ufeff')  # BOM for Excel UTF-8

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Data/Hora', 'Produto', 'SKU', 'Loja', 'Tipo', 'Qtd', 'PreÃ§o Venda Unit.', 'Forma Pagamento', 'Parcelas', 'Lucro', 'UsuÃ¡rio', 'ObservaÃ§Ã£o'])

    for m in movimentacoes:
        writer.writerow([
            m.criado_em.strftime('%d/%m/%Y %H:%M'),
            m.produto.nome,
            m.produto.sku or 'N/A',
            m.produto.loja.nome,
            m.get_tipo_display(),
            m.quantidade,
            f'{m.preco_venda_unitario:.2f}' if m.preco_venda_unitario else 'â€”',
            m.get_forma_pagamento_display() if m.forma_pagamento else 'â€”',
            f'{m.parcelas}x' if m.forma_pagamento == 'CARTAO_CREDITO' and m.parcelas else ('Ã€ vista' if m.forma_pagamento else 'â€”'),
            f'{m.lucro:.2f}' if m.tipo == MovimentacaoEstoque.TIPO_SAIDA else 'â€”',
            m.usuario.username,
            m.observacao or '',
        ])

    return response


@login_required
def relatorio_mensal_pdf(request):
    """Gera e retorna PDF com relatÃ³rio mensal de vendas."""
    user_lojas = get_user_lojas(request.user)

    # ParÃ¢metros
    hoje = timezone.now().date()
    try:
        mes = int(request.GET.get('mes', hoje.month))
        ano = int(request.GET.get('ano', hoje.year))
    except (ValueError, TypeError):
        mes = hoje.month
        ano = hoje.year

    loja_id = request.GET.get('loja_id', '')

    # Filtrar movimentaÃ§Ãµes do tipo saÃ­da no mÃªs/ano
    movimentacoes = MovimentacaoEstoque.objects.filter(
        tipo=MovimentacaoEstoque.TIPO_SAIDA,
        criado_em__year=ano,
        criado_em__month=mes,
    ).select_related('produto', 'produto__loja', 'usuario').order_by('criado_em')

    loja_nome = None
    if not is_admin_master(request.user):
        movimentacoes = movimentacoes.filter(produto__loja__in=user_lojas)
        if user_lojas.count() == 1:
            loja_nome = user_lojas.first().nome
    elif loja_id:
        try:
            loja = Loja.objects.get(pk=loja_id)
            movimentacoes = movimentacoes.filter(produto__loja=loja)
            loja_nome = loja.nome
        except Loja.DoesNotExist:
            pass

    # Gerar PDF
    buffer = gerar_relatorio_pdf(movimentacoes, mes, ano, loja_nome)

    # Retornar como download
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_vendas_{mes:02d}_{ano}.pdf"'
    return response

@login_required
def movimentacao_geral_create_view(request):
    if request.method == 'POST':
        form = MovimentacaoEstoqueGeralForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            produto = form.cleaned_data['produto']
            if not is_admin_master(request.user) and produto.loja.responsavel != request.user:
                raise PermissionDenied('Você não tem permissão para movimentar o estoque deste produto.')
            movimentacao.usuario = request.user
            movimentacao.save()
            messages.success(request, f'Movimentação de {movimentacao.get_tipo_display()} registrada com sucesso para {produto.nome}!')
            return redirect('estoque:movimentacao_list')
    else:
        form = MovimentacaoEstoqueGeralForm()
    context = {'form': form}
    return render(request, 'estoque/movimentacao_geral_form.html', context)


