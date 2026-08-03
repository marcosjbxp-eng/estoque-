# PROMPT MASTER — Sistema de Controle de Estoque Multi-Loja

**Agente alvo:** Antigravity (Gemini 3.6)
**Modo de execução:** Autônomo, com decisões técnicas documentadas ao longo do caminho. Não pare para perguntar sobre detalhes de implementação que já estão especificados aqui — apenas execute. Se encontrar uma ambiguidade real (não coberta neste documento) que puder travar o projeto, registre a decisão tomada e o motivo em um arquivo `DECISIONS.md` e siga em frente com a opção mais segura.

---

## 1. Papel

Você é um **desenvolvedor Python/Django sênior**, especializado em ferramentas internas para empresas que lidam com estoque de giro rápido (produtos que se esgotam e precisam ser repostos com frequência). Você entende de modelagem de dados relacional, isolamento de dados multi-usuário, integrações com serviços externos (upload de imagens) e construção de dashboards analíticos simples e diretos.

## 2. Contexto de Negócio

A empresa possui uma loja principal e **afiliados** — cada afiliado opera sua própria "loja" (ex: Loja A, Loja B), com estoque, produtos e preços independentes. Existe um **admin master** que precisa enxergar o panorama consolidado de todas as lojas, enquanto cada afiliado só deve enxergar e gerenciar o próprio estoque.

O objetivo da ferramenta é dar controle sobre:
- Quais produtos existem, com que preço, em qual loja.
- Quantas unidades estão disponíveis, com histórico de entradas e saídas.
- Quanto de lucro cada loja (e a empresa como um todo) está gerando, no geral e mês a mês.

## 3. Stack e Ambiente

- **Backend:** Python + Django (projeto já existente, rodando via Docker).
- **Banco de dados:** MySQL.
- **Armazenamento de imagens:** Cloudinary. As credenciais já existem no `.env` do projeto:
  - `CLOUDINARY_SECRET`
  - `CLOUDINARY_API_KEY`
  - (Se `CLOUDINARY_CLOUD_NAME` não existir no `.env`, adicione a variável e avise no `DECISIONS.md` — é obrigatória pro SDK do Cloudinary funcionar.)
- **App nova:** Este é um módulo novo dentro do projeto Django existente (ex: `estoque/` ou `inventory/`), criado do zero. Não existe nenhum model prévio de produto, estoque ou loja — modele tudo conforme a seção 4.
- Use o `django-cloudinary-storage` (ou equivalente já consolidado) para a integração de upload, em vez de escrever uma integração HTTP manual com a API do Cloudinary.

## 4. Modelo de Dados (proposto — pode refinar, mas mantenha a essência)

### `Loja`
- `nome`
- `responsavel` (FK para `User` — o afiliado dono da loja)
- `ativo` (boolean)
- `criado_em`

### `Produto`
- `loja` (FK para `Loja` — **obrigatório em todo produto**, é a chave do isolamento de dados)
- `nome`
- `descricao` (opcional)
- `sku` / código interno (opcional, mas recomendado)
- `preco_custo` (decimal)
- `preco_venda` (decimal)
- `quantidade_atual` (inteiro — sempre derivado/atualizado a partir das movimentações, nunca editado diretamente por fora do fluxo de movimentação)
- `foto_principal` (imagem via Cloudinary)
- `fotos_secundarias` (até 4 imagens — usar um model relacionado `ProdutoFoto` com FK para `Produto`, não um campo único)
- `ativo` (boolean)
- `criado_em` / `atualizado_em`

### `MovimentacaoEstoque`
Histórico de toda entrada e saída — é a fonte de verdade do estoque e também a base do cálculo de lucro.
- `produto` (FK)
- `tipo` (`ENTRADA` = reposição, sem impacto em lucro / `SAIDA` = venda, gera lucro)
- `quantidade` (inteiro positivo)
- `preco_venda_unitario` (decimal, **obrigatório quando `tipo = SAIDA`** — permite registrar o preço praticado naquela venda, que pode divergir do `preco_venda` cadastrado no produto por causa de promoções)
- `usuario` (FK para `User` — quem registrou a movimentação)
- `observacao` (texto livre, opcional — ex: "reposição do fornecedor X", "venda balcão")
- `criado_em`

**Regra de lucro:** para cada `MovimentacaoEstoque` do tipo `SAIDA`, o lucro daquela movimentação é:
`(preco_venda_unitario - produto.preco_custo) * quantidade`

O lucro geral e mensal exibido no dashboard é a soma dessas movimentações, agrupadas por loja e por mês.

## 5. Isolamento de Dados (Loja A vs Loja B)

Modelo escolhido: **FK de `Loja` em `Produto`, com filtro por usuário na camada de aplicação** (não é multi-tenancy físico com bancos/schemas separados).

Regras obrigatórias:
- Todo `Produto` e toda `MovimentacaoEstoque` estão sempre amarrados a uma `Loja` (diretamente ou via FK de produto).
- Um usuário afiliado (dono de `Loja`) só pode ver, criar, editar ou movimentar produtos da **própria loja**. Isso deve ser garantido no nível de queryset/view, não só escondido na interface — bloquear no backend mesmo que alguém tente acessar a URL de um produto de outra loja diretamente.
- O **admin master** (superusuário ou grupo `AdminMaster`) enxerga e filtra por qualquer loja, incluindo uma visão consolidada de todas.
- Use os grupos/permissões nativas do Django (`Group`, `Permission`) para diferenciar `AdminMaster` de `Afiliado`, combinado com o filtro por `loja` nas querysets. Não é necessário nenhum pacote de multi-tenancy físico (como `django-tenants`) — seria over-engineering pro tamanho do projeto.

## 6. Funcionalidades Requeridas

### 6.1 Gestão de Produtos
- Cadastrar produto (nome, descrição, SKU, preço de custo, preço de venda, loja, foto principal + até 4 fotos secundárias).
- Editar produto.
- Ativar/desativar produto (soft delete — não excluir fisicamente produtos com histórico de movimentação).
- Listar produtos com filtro por loja (automático pro afiliado, seletor de loja pro admin master) e busca por nome/SKU.

### 6.2 Gestão de Estoque
- Adicionar unidades (`ENTRADA`) — informar quantidade e observação opcional.
- Remover unidades (`SAIDA`) — informar quantidade, preço de venda unitário praticado, e observação opcional. Bloquear saída que deixaria `quantidade_atual` negativa.
- Toda alteração de estoque passa obrigatoriamente por um registro em `MovimentacaoEstoque` — nunca editar `quantidade_atual` diretamente.
- Tela de histórico de movimentações por produto (e por loja, pro admin master).

### 6.3 Upload de Fotos
- Upload da foto principal e das fotos secundárias direto pro Cloudinary no momento do cadastro/edição do produto.
- Pré-visualização das imagens já enviadas na tela de edição, com opção de substituir ou remover cada uma.
- Validar tipo de arquivo (imagens apenas) e um limite de tamanho razoável (ex: 5MB por imagem) antes de subir pro Cloudinary.

### 6.4 Dashboard de Lucros
- Apenas visual (gráficos/tabelas na tela — **sem exportação em PDF/Excel nesta fase**).
- Lucro geral (acumulado desde o início).
- Lucro mensal (agrupado por mês, com visão dos últimos 12 meses, por exemplo).
- Pro admin master: comparativo de lucro entre lojas (Loja A vs Loja B vs demais).
- Pro afiliado: visão restrita apenas ao lucro da própria loja.
- Sugestão de biblioteca de gráficos: Chart.js (via CDN) renderizado em cima de dados servidos por uma view/endpoint Django simples — não é necessário um framework de front pesado pra isso.

## 7. Requisitos Não-Funcionais

- Autenticação obrigatória em todas as views (nenhuma tela de estoque/produto acessível sem login).
- Toda ação de escrita (criar produto, movimentar estoque, upload de foto) deve validar que o usuário tem permissão sobre a loja em questão — inclusive contra manipulação direta de IDs na URL.
- Testes automatizados (mesmo que básicos) cobrindo:
  - Isolamento de dados entre lojas (um afiliado não deve conseguir ver/editar produto de outra loja).
  - Bloqueio de saída de estoque maior que a quantidade disponível.
  - Cálculo de lucro (geral e mensal) batendo com os dados esperados.
- Migrations do Django organizadas e revisáveis (nada de squash prematuro).

## 8. Critérios de Aceite (Definition of Done)

- [ ] Admin master consegue logar e ver o consolidado de todas as lojas.
- [ ] Afiliado consegue logar e só vê a própria loja (validado tanto na UI quanto tentando acessar URL de outra loja diretamente).
- [ ] É possível cadastrar um produto completo, com foto principal e até 4 fotos secundárias, e elas aparecem corretamente vindas do Cloudinary.
- [ ] É possível adicionar e remover unidades de estoque, e o histórico de movimentações reflete exatamente essas ações.
- [ ] Tentar remover mais unidades do que o disponível é bloqueado com uma mensagem de erro clara.
- [ ] Dashboard mostra lucro geral e lucro mês a mês, batendo com o cálculo `(preço de venda - preço de custo) × quantidade` das saídas registradas.
- [ ] Testes automatizados cobrindo os pontos da seção 7 estão passando.
- [ ] Nenhuma credencial (Cloudinary, banco) foi hardcoded — tudo lido do `.env`.

## 9. Estilo de Trabalho Esperado

- Trabalhe por fases: (1) modelagem de dados e migrations, (2) CRUD de produtos + upload de fotos, (3) movimentação de estoque, (4) dashboard de lucros, (5) permissões/isolamento e testes.
- Ao final de cada fase, deixe claro o que foi entregue antes de seguir pra próxima.
- Documente qualquer decisão técnica que fuja do que está especificado aqui (ex: escolha de biblioteca, nome de campo diferente) em `DECISIONS.md`.
- Priorize código legível e manutenível em vez de abstrações prematuras — este é um sistema interno de porte pequeno/médio, não uma plataforma SaaS multi-tenant de grande escala.
