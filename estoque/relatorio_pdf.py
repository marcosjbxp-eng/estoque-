"""
Módulo de geração de relatório PDF mensal de vendas.
Usa ReportLab para gerar PDFs profissionais com tabela de vendas e resumo.
"""
import io
from decimal import Decimal
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}

# Mapeamento de formas de pagamento para labels
PAGAMENTO_LABELS = {
    'PIX': 'PIX',
    'ESPECIE': 'Espécie',
    'CARTAO_DEBITO': 'Débito',
    'CARTAO_CREDITO': 'Crédito',
}


def gerar_relatorio_pdf(movimentacoes, mes, ano, loja_nome=None):
    """
    Gera um PDF com relatório mensal de vendas.

    Args:
        movimentacoes: QuerySet de MovimentacaoEstoque (já filtrado por saídas do mês)
        mes: int (1-12)
        ano: int
        loja_nome: str ou None (se None, mostra "Todas as Lojas")

    Returns:
        buffer: io.BytesIO com o PDF gerado
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    style_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e61e8'),
        spaceAfter=2 * mm,
        alignment=TA_CENTER,
    )
    style_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=6 * mm,
        alignment=TA_CENTER,
    )
    style_secao = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1e61e8'),
        spaceBefore=8 * mm,
        spaceAfter=4 * mm,
    )
    style_normal = styles['Normal']
    style_right = ParagraphStyle(
        'Right',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontSize=9,
    )

    elements = []

    # ========== CABEÇALHO ==========
    nome_mes = MESES_PT.get(mes, str(mes))
    titulo_loja = loja_nome or "Todas as Lojas"

    elements.append(Paragraph("ESTOQUE MASTER — Relatório de Vendas", style_titulo))
    elements.append(Paragraph(
        f"{titulo_loja} &bull; {nome_mes} de {ano}",
        style_subtitulo
    ))
    elements.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor('#1e61e8'),
        spaceAfter=6 * mm
    ))

    # ========== TABELA DE VENDAS ==========
    if not movimentacoes:
        elements.append(Paragraph(
            "Nenhuma venda registrada neste período.",
            ParagraphStyle('Empty', parent=style_normal, fontSize=12, textColor=colors.grey, alignment=TA_CENTER)
        ))
    else:
        elements.append(Paragraph("Detalhamento de Vendas", style_secao))

        # Cabeçalho da tabela
        header = [
            'Data/Hora', 'Produto', 'Loja', 'Qtd',
            'Preço Unit.', 'Total Venda', 'Pagamento', 'Parcelas',
            'Lucro', 'Usuário'
        ]

        data = [header]

        # Totais acumuladores
        total_faturamento = Decimal('0.00')
        total_lucro = Decimal('0.00')
        total_unidades = 0
        totais_por_pagamento = {}

        for mov in movimentacoes:
            preco_unit = mov.preco_venda_unitario or Decimal('0.00')
            total_venda = preco_unit * mov.quantidade
            lucro = mov.lucro

            total_faturamento += total_venda
            total_lucro += lucro
            total_unidades += mov.quantidade

            # Acumular por forma de pagamento
            pgto_key = mov.forma_pagamento or '—'
            pgto_label = PAGAMENTO_LABELS.get(mov.forma_pagamento, mov.forma_pagamento or '—')
            if pgto_key not in totais_por_pagamento:
                totais_por_pagamento[pgto_key] = {
                    'label': pgto_label,
                    'total': Decimal('0.00'),
                    'count': 0,
                }
            totais_por_pagamento[pgto_key]['total'] += total_venda
            totais_por_pagamento[pgto_key]['count'] += 1

            parcelas_txt = ''
            if mov.forma_pagamento == 'CARTAO_CREDITO' and mov.parcelas:
                parcelas_txt = f'{mov.parcelas}x'
            elif mov.forma_pagamento:
                parcelas_txt = 'À vista'

            row = [
                mov.criado_em.strftime('%d/%m/%Y %H:%M'),
                mov.produto.nome[:30],
                mov.produto.loja.nome[:20],
                str(mov.quantidade),
                f'R$ {preco_unit:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                f'R$ {total_venda:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                pgto_label,
                parcelas_txt,
                f'R$ {lucro:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                mov.usuario.username,
            ]
            data.append(row)

        # Larguras das colunas (landscape A4 = ~842pt de largura)
        col_widths = [70, 120, 80, 35, 65, 70, 60, 50, 65, 65]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e61e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),

            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Qtd
            ('ALIGN', (4, 1), (5, -1), 'RIGHT'),   # Preços
            ('ALIGN', (7, 1), (7, -1), 'CENTER'),   # Parcelas
            ('ALIGN', (8, 1), (8, -1), 'RIGHT'),    # Lucro
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),

            # Linhas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4ff')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1e61e8')),
        ]))

        elements.append(table)

        # ========== RESUMO ==========
        elements.append(Spacer(1, 8 * mm))
        elements.append(Paragraph("Resumo do Período", style_secao))

        # Tabela de resumo por forma de pagamento
        resumo_header = ['Forma de Pagamento', 'Nº de Vendas', 'Total (R$)']
        resumo_data = [resumo_header]

        for key, info in totais_por_pagamento.items():
            resumo_data.append([
                info['label'],
                str(info['count']),
                f'R$ {info["total"]:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            ])

        # Linha de totais gerais
        resumo_data.append([
            'TOTAL GERAL',
            str(total_unidades) + ' unid.',
            f'R$ {total_faturamento:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
        ])

        resumo_table = Table(resumo_data, colWidths=[200, 100, 150])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e61e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),

            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),

            # Última linha (totais) em destaque
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f0fe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1e61e8')),
        ]))
        elements.append(resumo_table)

        # Lucro total
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph(
            f'<b>Lucro Líquido do Período:</b> R$ {total_lucro:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            ParagraphStyle('LucroTotal', parent=style_normal, fontSize=12,
                           textColor=colors.HexColor('#10b981'))
        ))

    # ========== RODAPÉ ==========
    elements.append(Spacer(1, 10 * mm))
    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor('#cccccc'),
        spaceAfter=3 * mm
    ))
    elements.append(Paragraph(
        f"Relatório gerado em {date.today().strftime('%d/%m/%Y')} — ESTOQUE MASTER © {date.today().year}",
        ParagraphStyle('Rodape', parent=style_normal, fontSize=8,
                       textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
