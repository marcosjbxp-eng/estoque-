from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Loja(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Loja")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lojas',
        verbose_name="Responsável (Afiliado)"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    loja = models.ForeignKey(
        Loja,
        on_delete=models.CASCADE,
        related_name='produtos',
        verbose_name="Loja"
    )
    nome = models.CharField(max_length=150, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    sku = models.CharField(max_length=50, blank=True, verbose_name="SKU / Código Interno")
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Custo (R$)")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda (R$)")
    quantidade_atual = models.IntegerField(default=0, verbose_name="Quantidade Atual em Estoque")
    foto_principal = models.ImageField(
        upload_to='produtos/principais/',
        blank=True,
        null=True,
        verbose_name="Foto Principal"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo (Soft Delete)")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome} ({self.loja.nome})"

    @property
    def margem_lucro_estimada(self):
        if self.preco_custo and self.preco_venda and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return Decimal('0.00')


class ProdutoFoto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='fotos_secundarias',
        verbose_name="Produto"
    )
    foto = models.ImageField(upload_to='produtos/secundarias/', verbose_name="Foto Secundária")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Foto Secundária do Produto"
        verbose_name_plural = "Fotos Secundárias do Produto"

    def __str__(self):
        return f"Foto secundária de {self.produto.nome}"


class MovimentacaoEstoque(models.Model):
    TIPO_ENTRADA = 'ENTRADA'
    TIPO_SAIDA = 'SAIDA'
    TIPO_CHOICES = (
        (TIPO_ENTRADA, 'Entrada (Reposição)'),
        (TIPO_SAIDA, 'Saída (Venda)'),
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='movimentacoes',
        verbose_name="Produto"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo de Movimentação")
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    preco_venda_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço de Venda Unitário (R$)"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        verbose_name="Usuário Responsável"
    )
    observacao = models.TextField(blank=True, verbose_name="Observação")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data / Hora")

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.quantidade}x {self.produto.nome}"

    @property
    def lucro(self):
        if self.tipo == self.TIPO_SAIDA and self.preco_venda_unitario is not None:
            return (self.preco_venda_unitario - self.produto.preco_custo) * self.quantidade
        return Decimal('0.00')
