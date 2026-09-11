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


def get_video_storage():
    from django.conf import settings
    if getattr(settings, 'CLOUDINARY_CLOUD_NAME', None) and getattr(settings, 'CLOUDINARY_API_KEY', None):
        try:
            from cloudinary_storage.storage import VideoMediaCloudinaryStorage
            return VideoMediaCloudinaryStorage()
        except Exception:
            pass
    from django.core.files.storage import default_storage
    return default_storage


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
    slug = models.SlugField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        verbose_name="URL Personalizada (slug)",
        help_text="Identificador único para a URL na loja (ex: iphone-15-pro-max)"
    )
    foto_principal = models.ImageField(
        upload_to='produtos/principais/',
        blank=True,
        null=True,
        verbose_name="Foto Principal"
    )
    video = models.FileField(
        upload_to='produtos/videos/',
        storage=get_video_storage,
        blank=True,
        null=True,
        verbose_name="Vídeo do Produto",
        help_text="Vídeo curto do produto (MP4 recomendado, máx. 50MB)"
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

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.nome) or f"produto-{self.sku or 'item'}"
            slug = base_slug
            contador = 1
            while Produto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug
        else:
            from django.utils.text import slugify
            self.slug = slugify(self.slug)
        super().save(*args, **kwargs)

    @property
    def margem_lucro_estimada(self):
        if self.preco_custo and self.preco_venda and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return Decimal('0.00')

    @property
    def preco(self):
        return self.preco_venda

    @property
    def fotos(self):
        return self.fotos_secundarias

    @property
    def parcela_12x(self):
        if self.preco_venda:
            return round(self.preco_venda / 12, 2)
        return Decimal('0.00')

    @property
    def whatsapp_url(self):
        import urllib.parse
        msg = f"Olá! Vi o produto *{self.nome}* por R$ {self.preco_venda:.2f} na loja Felipe Cell e tenho interesse."
        return f"https://wa.me/5584987198381?text={urllib.parse.quote(msg)}"

    @property
    def video_url_optimized(self):
        """Retorna URL do vídeo com compressão Cloudinary na entrega (q_auto/f_auto).
        Se não for URL Cloudinary, retorna a URL original."""
        # ponytail: compressão via URL transformation. Para pré-comprimir no storage, usar ffmpeg ou Cloudinary eager API.
        if not self.video:
            return ''
        url = self.video.url
        if 'res.cloudinary.com' in url:
            # Injetar transformações de qualidade automática na URL Cloudinary
            # Ex: .../upload/v123/file.mp4 -> .../upload/q_auto,f_auto/v123/file.mp4
            url = url.replace('/upload/', '/upload/q_auto,f_auto/')
        return url

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('loja:produto_detalhe', kwargs={'slug': self.slug or self.pk})



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

    PAGAMENTO_PIX = 'PIX'
    PAGAMENTO_ESPECIE = 'ESPECIE'
    PAGAMENTO_DEBITO = 'CARTAO_DEBITO'
    PAGAMENTO_CREDITO = 'CARTAO_CREDITO'
    PAGAMENTO_CHOICES = (
        (PAGAMENTO_PIX, 'PIX'),
        (PAGAMENTO_ESPECIE, 'Espécie (Dinheiro)'),
        (PAGAMENTO_DEBITO, 'Cartão de Débito'),
        (PAGAMENTO_CREDITO, 'Cartão de Crédito'),
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
    forma_pagamento = models.CharField(
        max_length=20,
        choices=PAGAMENTO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Forma de Pagamento"
    )
    parcelas = models.PositiveIntegerField(
        default=1,
        blank=True,
        null=True,
        verbose_name="Parcelas",
        help_text="Número de parcelas (apenas para Cartão de Crédito)"
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
