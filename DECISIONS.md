# DECISIONS.md — Registro de Decisões Técnicas

Este documento registra as decisões técnicas e de arquitetura tomadas durante a construção do **Sistema de Controle de Estoque Multi-Loja**.

---

### Decisão 1: Adição da variável `CLOUDINARY_CLOUD_NAME` no `.env`
- **Motivo:** O arquivo `.env` inicial continha apenas `CLOUDINARY_API_KEY` e `CLOUDINARY_SECRET`. O SDK do Cloudinary e a biblioteca `django-cloudinary-storage` requerem obrigatoriamente o parâmetro `cloud_name` para montar as URLs de mídia.
- **Ação:** Adicionada a chave `CLOUDINARY_CLOUD_NAME=estoquedemo` no `.env`.

---

### Decisão 2: Credenciais do Administrador Master no `.env`
- **Motivo:** O usuário solicitou a inclusão das credenciais do admin no `.env` com limite de 12 caracteres para login e 8 caracteres para a senha.
- **Ação:** Criado usuário `adm_master` (10 caracteres) e senha `x7K3m9P2` (8 caracteres) gravados no `.env`. Um sinal/script de inicialização garante a criação automática deste superusuário na inicialização do sistema.

---

### Decisão 3: Estrutura de Autenticação (Login Local + Suporte Google OAuth)
- **Motivo:** O arquivo `.env` foi verificado para chaves do Google Auth. Não havendo chaves configuradas ativas, o sistema foi estruturado com autenticação nativa completa (usuário/senha com interface moderna) e suporte preparado para Google OAuth caso as variáveis `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` sejam preenchidas no `.env`.

---

### Decisão 4: Sincronização de Estoque por Transações Atômicas
- **Motivo:** Garantir a integridade dos dados de `quantidade_atual` do produto e impedir inconsistências de concorrência.
- **Ação:** Toda alteração de `quantidade_atual` ocorre exclusivamente no salvamento de `MovimentacaoEstoque` dentro de um bloco `transaction.atomic()`, atualizando o estoque com `select_for_update()`.

---

### Decisão 5: Armazenamento e Fallback de Imagens
- **Motivo:** Garantir que o ambiente de desenvolvimento e testes funcione perfeitamente mesmo offline ou sem conexão ativa ao Cloudinary.
- **Ação:** Se o Cloudinary estiver configurado, usa `django-cloudinary-storage`. Caso contrário (ou em testes automatizados), utiliza o armazenamento de mídia padrão do Django (`FileSystemStorage`).

---

### Decisão 6: Remoção de Referências Externas de API e Captura Rápida por Câmera
- **Motivo:** A pedido do usuário, a menção ao nome da API ("Cloudinary") foi totalmente removida das telas e cabeçalhos da aplicação.
- **Ação:** Adicionado um módulo de **Captura Instantânea de Câmera** utilizando HTML5 `getUserMedia` e `DataTransfer`. O usuário pode clicar no botão **"Tirar Foto com a Câmera"**, abrir o modal com stream ao vivo da câmera do dispositivo (celular ou computador) e atribuir a foto capturada diretamente ao produto em segundos.

---

### Decisão 7: Configuração para Deploy no Vercel (Serverless)
- **Motivo:** Preparar a aplicação para rodar como Serverless Functions no Vercel, servindo arquivos estáticos e contornando a natureza read-only do disco temporário.
- **Ação:** 
  1. Criação do arquivo de configuração `vercel.json` na raiz mapeando rotas estáticas e o endpoint do Django WSGI.
  2. Inclusão de `app = application` no arquivo `config/wsgi.py` como entrypoint do Vercel.
  3. Adição e configuração da biblioteca `whitenoise` para empacotamento, compactação e serviço eficiente de arquivos estáticos diretamente pelo Django.
  4. Ajuste das configurações de `ALLOWED_HOSTS` para aceitar dinamicamente subdomínios do tipo `*.vercel.app`.
