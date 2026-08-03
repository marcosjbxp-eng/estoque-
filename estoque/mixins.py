from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Loja, Produto

def is_admin_master(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='AdminMaster').exists())

def get_user_lojas(user):
    if is_admin_master(user):
        return Loja.objects.all()
    return Loja.objects.filter(responsavel=user, ativo=True)

class LojaRequiredMixin(LoginRequiredMixin):
    """
    Garante que o usuário esteja autenticado e tenha acesso à Loja específica.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if is_admin_master(request.user):
            return super().dispatch(request, *args, **kwargs)

        # Se houver produto_pk ou pk no kwargs, validar loja do produto
        produto_pk = kwargs.get('produto_pk') or kwargs.get('pk')
        if produto_pk and 'produto' in self.model.__name__.lower():
            produto = get_object_or_404(Produto, pk=produto_pk)
            if produto.loja.responsavel != request.user:
                raise PermissionDenied("Você não tem permissão para acessar produtos de outra loja.")

        return super().dispatch(request, *args, **kwargs)
