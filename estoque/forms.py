from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Produto, ProdutoFoto, MovimentacaoEstoque, Loja

MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

def validar_tamanho_imagem(file):
    if file and file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(f"O tamanho máximo permitido por imagem é {MAX_IMAGE_SIZE_MB}MB.")


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['loja', 'nome', 'sku', 'descricao', 'preco_custo', 'preco_venda', 'foto_principal', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Camiseta Oversized'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: CAM-001'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada do produto...'}),
            'preco_custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'loja': forms.Select(attrs={'class': 'form-select'}),
            'foto_principal': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser and not user.groups.filter(name='AdminMaster').exists():
            self.fields['loja'].queryset = Loja.objects.filter(responsavel=user, ativo=True)
            if self.fields['loja'].queryset.count() == 1:
                self.fields['loja'].initial = self.fields['loja'].queryset.first()
        else:
            self.fields['loja'].queryset = Loja.objects.filter(ativo=True)

    def clean_foto_principal(self):
        foto = self.cleaned_data.get('foto_principal')
        validar_tamanho_imagem(foto)
        return foto


class ProdutoFotoForm(forms.ModelForm):
    class Meta:
        model = ProdutoFoto
        fields = ['foto']
        widgets = {
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        validar_tamanho_imagem(foto)
        return foto


ProdutoFotoFormSet = inlineformset_factory(
    Produto,
    ProdutoFoto,
    form=ProdutoFotoForm,
    extra=4,
    max_num=4,
    can_delete=True
)


class MovimentacaoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ['tipo', 'quantidade', 'preco_venda_unitario', 'observacao']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_movimentacao'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Quantidade'}),
            'preco_venda_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Preço praticado'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observação opcional (ex: Venda balcão / Reposição)'}),
        }

    def __init__(self, *args, **kwargs):
        self.produto = kwargs.pop('produto', None)
        super().__init__(*args, **kwargs)
        if self.produto:
            self.fields['preco_venda_unitario'].initial = self.produto.preco_venda

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        quantidade = cleaned_data.get('quantidade')
        preco_venda_unitario = cleaned_data.get('preco_venda_unitario')

        if not self.produto:
            raise ValidationError("Produto não informado para esta movimentação.")

        if tipo == MovimentacaoEstoque.TIPO_SAIDA:
            if preco_venda_unitario is None:
                self.add_error('preco_venda_unitario', "Informe o preço de venda unitário para a movimentação de saída.")

            if quantidade and quantidade > self.produto.quantidade_atual:
                raise ValidationError(
                    f"Operação negada: quantidade solicitada ({quantidade}) é maior do que a quantidade disponível em estoque ({self.produto.quantidade_atual})."
                )

        return cleaned_data
