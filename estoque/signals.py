from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MovimentacaoEstoque, Produto

@receiver(post_save, sender=MovimentacaoEstoque)
def atualizar_estoque_ao_salvar(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            produto = Produto.objects.select_for_update().get(pk=instance.produto.pk)
            if instance.tipo == MovimentacaoEstoque.TIPO_ENTRADA:
                produto.quantidade_atual += instance.quantidade
            elif instance.tipo == MovimentacaoEstoque.TIPO_SAIDA:
                produto.quantidade_atual -= instance.quantidade
            produto.save(update_fields=['quantidade_atual', 'atualizado_em'])
