from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from estoque.models import Loja, Produto, MovimentacaoEstoque

class EstoqueTestCase(TestCase):
    def setUp(self):
        # Grupos
        self.admin_group = Group.objects.create(name='AdminMaster')
        self.afiliados_group = Group.objects.create(name='Afiliados')

        # Usuários
        self.admin_user = User.objects.create_superuser(
            username='adm_master', email='admin@test.com', password='x7K3m9P2'
        )
        self.admin_user.groups.add(self.admin_group)

        self.afiliado_a = User.objects.create_user(
            username='afiliado_a', email='afiliado_a@test.com', password='senha123'
        )
        self.afiliado_a.groups.add(self.afiliados_group)

        self.afiliado_b = User.objects.create_user(
            username='afiliado_b', email='afiliado_b@test.com', password='senha123'
        )
        self.afiliado_b.groups.add(self.afiliados_group)

        # Lojas
        self.loja_a = Loja.objects.create(nome='Loja A', responsavel=self.afiliado_a)
        self.loja_b = Loja.objects.create(nome='Loja B', responsavel=self.afiliado_b)

        # Produtos
        self.produto_a = Produto.objects.create(
            loja=self.loja_a,
            nome='Produto Loja A',
            sku='PROD-A',
            preco_custo=Decimal('50.00'),
            preco_venda=Decimal('100.00'),
            quantidade_atual=10
        )

        self.produto_b = Produto.objects.create(
            loja=self.loja_b,
            nome='Produto Loja B',
            sku='PROD-B',
            preco_custo=Decimal('30.00'),
            preco_venda=Decimal('70.00'),
            quantidade_atual=5
        )

        self.client = Client()

    def test_isolamento_dados_entre_lojas(self):
        """Um afiliado não deve conseguir acessar nem editar produtos de outra loja."""
        self.client.login(username='afiliado_a', password='senha123')

        # 1. Listagem: afiliado_a só vê o produto_a
        response = self.client.get(reverse('estoque:produto_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Produto Loja A')
        self.assertNotContains(response, 'Produto Loja B')

        # 2. Tentar acessar tela de edição do produto_b (deve retornar 403 Forbidden)
        response_edit = self.client.get(reverse('estoque:produto_update', kwargs={'pk': self.produto_b.pk}))
        self.assertEqual(response_edit.status_code, 403)

        # 3. Tentar registrar movimentação no produto_b (deve retornar 403 Forbidden)
        response_mov = self.client.get(reverse('estoque:movimentacao_create', kwargs={'produto_pk': self.produto_b.pk}))
        self.assertEqual(response_mov.status_code, 403)

    def test_bloqueio_saida_estoque_insuficiente(self):
        """Tentar remover mais unidades do que o disponível em estoque deve ser bloqueado."""
        self.client.login(username='afiliado_a', password='senha123')

        # produto_a possui quantidade_atual = 10. Tentar remover 15.
        url = reverse('estoque:movimentacao_create', kwargs={'produto_pk': self.produto_a.pk})
        data = {
            'tipo': 'SAIDA',
            'quantidade': 15,
            'preco_venda_unitario': '100.00',
            'observacao': 'Venda grande'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Permanece no form exibindo erro

        # Verificar se o produto continua com 10 unidades
        self.produto_a.refresh_from_db()
        self.assertEqual(self.produto_a.quantidade_atual, 10)

    def test_calculo_lucro_e_movimentacao_sucesso(self):
        """Mover estoque com saída deve atualizar o produto e calcular lucro corretamente."""
        self.client.login(username='afiliado_a', password='senha123')

        url = reverse('estoque:movimentacao_create', kwargs={'produto_pk': self.produto_a.pk})
        data = {
            'tipo': 'SAIDA',
            'quantidade': 4,
            'preco_venda_unitario': '120.00',  # Venda a 120, custo era 50 -> Lucro por unid: 70 -> total 280
            'observacao': 'Venda balcão'
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verificar estoque atualizado (10 - 4 = 6)
        self.produto_a.refresh_from_db()
        self.assertEqual(self.produto_a.quantidade_atual, 6)

        # Verificar registro da movimentação e cálculo do lucro
        mov = MovimentacaoEstoque.objects.latest('id')
        self.assertEqual(mov.quantidade, 4)
        self.assertEqual(mov.lucro, Decimal('280.00'))
