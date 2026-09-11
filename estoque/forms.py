from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Produto, ProdutoFoto, MovimentacaoEstoque, Loja

MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
MAX_VIDEO_SIZE_MB = 50
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.avi')

def validar_tamanho_imagem(file):
    if file and file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(f"O tamanho máximo permitido por imagem é {MAX_IMAGE_SIZE_MB}MB.")

def validar_video(file):
    if not file:
        return
    import os
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in VIDEO_EXTENSIONS:
        raise ValidationError(f"Formato de vídeo não suportado. Use: {', '.join(VIDEO_EXTENSIONS)}")
    if file.size > MAX_VIDEO_SIZE_BYTES:
        raise ValidationError(f"O tamanho máximo permitido por vídeo é {MAX_VIDEO_SIZE_MB}MB.")


def otimizar_video(file):
    """Comprime o vídeo com ffmpeg antes do upload se disponível e se reduzir peso."""
    if not file or not hasattr(file, 'chunks'):
        return file
    import shutil
    import subprocess
    import tempfile
    import os
    from django.core.files.base import ContentFile

    ffmpeg_bin = shutil.which('ffmpeg')
    if not ffmpeg_bin:
        return file

    in_path = None
    out_path = None
    try:
        ext = os.path.splitext(file.name)[1].lower() or '.mp4'
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as in_tmp:
            for chunk in file.chunks():
                in_tmp.write(chunk)
            in_path = in_tmp.name

        out_path = in_path + '_opt.mp4'
        cmd = [
            ffmpeg_bin, '-y',
            '-i', in_path,
            '-vf', "scale='min(1080,iw)':-2",
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            '-acodec', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            out_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
        if res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            if os.path.getsize(out_path) < file.size:
                with open(out_path, 'rb') as f:
                    compressed_content = f.read()
                return ContentFile(compressed_content, name=file.name)
    except Exception:
        pass
    finally:
        if in_path and os.path.exists(in_path):
            try: os.remove(in_path)
            except Exception: pass
        if out_path and os.path.exists(out_path):
            try: os.remove(out_path)
            except Exception: pass
    return file


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['loja', 'nome', 'slug', 'sku', 'descricao', 'preco_custo', 'preco_venda', 'foto_principal', 'video', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: iPhone 15 Pro Max'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: iphone-15-pro-max (opcional: gerado automaticamente)'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: IPH-15PM-256'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada do produto...'}),
            'preco_custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'loja': forms.Select(attrs={'class': 'form-select'}),
            'foto_principal': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'video': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/mp4,video/webm,video/quicktime,video/x-msvideo'}),
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

    def clean_video(self):
        video = self.cleaned_data.get('video')
        validar_video(video)
        return otimizar_video(video)


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
        fields = ['tipo', 'quantidade', 'preco_venda_unitario', 'forma_pagamento', 'parcelas', 'observacao']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_movimentacao'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Quantidade'}),
            'preco_venda_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Preço praticado'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select', 'id': 'id_forma_pagamento'}),
            'parcelas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 24, 'placeholder': 'Nº de parcelas', 'id': 'id_parcelas'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observação opcional (ex: Venda balcão / Reposição)'}),
        }

    def __init__(self, *args, **kwargs):
        self.produto = kwargs.pop('produto', None)
        super().__init__(*args, **kwargs)
        if self.produto:
            self.fields['preco_venda_unitario'].initial = self.produto.preco_venda
        # Tornar forma_pagamento não obrigatório no form (validação manual no clean)
        self.fields['forma_pagamento'].required = False
        self.fields['parcelas'].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        quantidade = cleaned_data.get('quantidade')
        preco_venda_unitario = cleaned_data.get('preco_venda_unitario')
        forma_pagamento = cleaned_data.get('forma_pagamento')
        parcelas = cleaned_data.get('parcelas')

        if not self.produto:
            raise ValidationError("Produto não informado para esta movimentação.")

        if tipo == MovimentacaoEstoque.TIPO_SAIDA:
            if preco_venda_unitario is None:
                self.add_error('preco_venda_unitario', "Informe o preço de venda unitário para a movimentação de saída.")

            if not forma_pagamento:
                self.add_error('forma_pagamento', "Informe a forma de pagamento para registrar a venda.")

            if forma_pagamento == MovimentacaoEstoque.PAGAMENTO_CREDITO:
                if not parcelas or parcelas < 1:
                    self.add_error('parcelas', "Informe o número de parcelas para pagamento com Cartão de Crédito.")

            if quantidade and quantidade > self.produto.quantidade_atual:
                raise ValidationError(
                    f"Operação negada: quantidade solicitada ({quantidade}) é maior do que a quantidade disponível em estoque ({self.produto.quantidade_atual})."
                )

        return cleaned_data


class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = ['nome', 'responsavel', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Felipe Cell - Unidade Centro'}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsavel'].queryset = User.objects.filter(is_active=True).order_by('username')


class UsuarioCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha de acesso'}),
        label='Senha',
        min_length=6,
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme a senha'}),
        label='Confirmar Senha',
    )
    is_admin_master = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Admin Master (acesso total)',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário (login)'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'As senhas não coincidem.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            if self.cleaned_data.get('is_admin_master'):
                from django.contrib.auth.models import Group
                group, _ = Group.objects.get_or_create(name='AdminMaster')
                user.groups.add(group)
        return user


class UsuarioEditForm(forms.ModelForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Deixe vazio para manter a senha atual'}),
        label='Nova Senha',
        required=False,
        min_length=6,
    )
    is_admin_master = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Admin Master (acesso total)',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['is_admin_master'].initial = (
                self.instance.is_superuser or
                self.instance.groups.filter(name='AdminMaster').exists()
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name='AdminMaster')
            if self.cleaned_data.get('is_admin_master'):
                user.groups.add(group)
            else:
                user.groups.remove(group)
        return user
