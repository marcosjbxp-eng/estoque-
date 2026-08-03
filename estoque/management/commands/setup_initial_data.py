from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.conf import settings
from estoque.models import Loja, Produto, MovimentacaoEstoque

class Command(BaseCommand):
    help = "Cria grupos iniciais, superusuário master a partir do .env e lojas de demonstração."

    def handle(self, *args, **options):
        # 1. Grupos
        admin_group, _ = Group.objects.get_or_create(name='AdminMaster')
        afiliados_group, _ = Group.objects.get_or_create(name='Afiliados')

        # 2. Superusuário Master a partir do .env
        admin_user = settings.ADMIN_USERNAME
        admin_pass = settings.ADMIN_PASSWORD

        if not User.objects.filter(username=admin_user).exists():
            master = User.objects.create_superuser(
                username=admin_user,
                email='admin@master.com',
                password=admin_pass
            )
            master.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f"Superusuário '{admin_user}' criado com sucesso! Senha: '{admin_pass}'"))
        else:
            master = User.objects.get(username=admin_user)
            master.set_password(admin_pass)
            master.is_superuser = True
            master.is_staff = True
            master.save()
            master.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f"Superusuário '{admin_user}' atualizado a partir do .env!"))

        # 3. Criar Afiliados e Lojas de Teste se não existirem
        afiliado_a, _ = User.objects.get_or_create(username='afiliado_a', defaults={'email': 'lojaa@afiliados.com'})
        if _:
            afiliado_a.set_password('senha123')
            afiliado_a.groups.add(afiliados_group)
            afiliado_a.save()

        afiliado_b, _ = User.objects.get_or_create(username='afiliado_b', defaults={'email': 'lojab@afiliados.com'})
        if _:
            afiliado_b.set_password('senha123')
            afiliado_b.groups.add(afiliados_group)
            afiliado_b.save()

        loja_a, _ = Loja.objects.get_or_create(nome='Loja A - Matriz SP', defaults={'responsavel': afiliado_a})
        loja_b, _ = Loja.objects.get_or_create(nome='Loja B - Filial RJ', defaults={'responsavel': afiliado_b})

        self.stdout.write(self.style.SUCCESS("Dados iniciais configurados com sucesso!"))
