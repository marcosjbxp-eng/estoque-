# Guia de Estilo e Design System — Página de Vendas (Felipe Cell)

Este documento reúne todas as especificações de design, tipografia, paleta de cores, componentes, espaçamentos, botões e efeitos capturados a partir do arquivo [`pagina-vendas/index.html`](file:///c:/Users/mj904/OneDrive/Área%20de%20Trabalho/system/pagina-vendas/index.html).

---

## 1. Identidade Visual & Conceito
- **Conceito:** Tech Minimalista / Editorial Premium (inspirado nas diretrizes visuais da Apple e Oppo).
- **Tema:** Dark Mode nativo (`<html class="dark scroll-smooth">`).
- **Framework de Estilização:** Tailwind CSS (via CDN) + CSS Customizado complementar.

---

## 2. Paleta de Cores

### 2.1 Cores Principais da Marca (Tailwind Config)
| Nome do Token | Código Hexadecimal | Função no Layout |
| :--- | :--- | :--- |
| `brandBlue` | `#1e61e8` | Cor primária de destaque, botões principais de CTA, acentos de tópicos, badges de seção, barra de progresso do loader e hover dos cards do showcase. |
| `brandBlueHover` | `#1850c4` | Estado hover / foco dos botões azuis primários. |
| `brandDark` | `#202224` | Fundo principal da página (`body`), tela de carregamento (loader), rodapé e base escura de botões neutros. |
| `brandCard` | `#27292c` | Fundo principal de cards, containers de serviço, vitrines, colunas modulares e caixas de informação. |
| `brandBorder` | `#34373b` | Borda padrão aplicada em cards, divisões de seção (`border-t`), cabeçalho, badges e caixas. |

### 2.2 Cores Translúcidas e Superfícies (Opacidades)
- **Cabeçalho Fixo:** `bg-brandDark/85` com desfoque de fundo `backdrop-blur-md` e borda inferior `border-brandBorder`.
- **Badges de Destaque:** `bg-brandCard/60` com borda `border-brandBorder`.
- **Cards de Confiança / Sinais Rápidos:** `bg-brandCard/40` com borda `border-brandBorder`.
- **Legendas de Imagens / Vitrine:** `bg-brandCard/90` com separador `border-brandBorder`.
- **Tags de Imagem / Vitrine:** `bg-black/80` com `backdrop-blur-sm` e borda `border-white/10`.
- **Overlays de Vídeo:** `bg-black/40` para play/pause indicators.
- **Trilhas e Gradientes Laterais:** `bg-gradient-to-r from-brandDark to-transparent` e `bg-gradient-to-l from-brandDark to-transparent`.

### 2.3 Cores de Texto e Hierarquia
- **Branco Puro (`#ffffff` / `text-white`):** Títulos principais (H1, H2, H3), títulos de serviços e textos de botões de destaque.
- **Neutro Claro (`text-neutral-200`):** Frases de destaque, textos de cards secundários, horários e informações de contato.
- **Neutro Médio (`text-neutral-300`):** Parágrafos longos, narrativa editorial e textos explicativos.
- **Neutro Secundário (`text-neutral-400`):** Itens do menu de navegação, subtítulos de serviços, legendas de categorias e direitos autorais.
- **Neutro Mudo (`text-neutral-500`):** Informações de rodapé de menor hierarquia.
- **Seleção de Texto Global:** `selection:bg-brandBlue selection:text-white`.

### 2.4 Paleta dos Controles de Vídeo (Zinc UI)
- **Fundo do botão:** `bg-zinc-900`
- **Borda do botão:** `border-zinc-800`
- **Texto:** `text-zinc-100` / `text-zinc-200`
- **Hover:** `hover:bg-zinc-800/80 hover:border-zinc-700 hover:text-zinc-50`
- **Ícones:** `text-zinc-400` / `text-zinc-300`

---

## 3. Tipografia

### 3.1 Fonte Principal
- **Família:** `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`
- **Origem:** Google Fonts (`Inter:wght@300;400;500;600;700;800`)

### 3.2 Escala Tipográfica e Aplicações
| Nível / Elemento | Tamanhos e Classes Tailwind | Peso | Line Height / Tracking |
| :--- | :--- | :--- | :--- |
| **Hero Title (H1)** | `text-3xl sm:text-4xl md:text-5xl lg:text-[3.25rem]` | `font-bold` (700) | `leading-[1.15] tracking-tight` |
| **Títulos de Seção (H2)** | `text-2xl sm:text-3xl md:text-4xl` | `font-bold` (700) | `leading-snug tracking-tight` |
| **Subtítulos de Cards (H3)** | `text-xl` | `font-bold` (700) | Padrão |
| **Eyebrow / Badges de Seção** | `text-xs` (12px) | `font-bold` (700) | `uppercase tracking-widest` |
| **Sub-etiquetas de Mídia** | `text-[11px]` (11px) | `font-bold` (700) | `uppercase tracking-wider` |
| **Links de Navegação Header** | `text-[13px]` (13px) | `font-medium` (500) | Padrão |
| **Texto de Apoio Hero** | `text-base sm:text-lg md:text-xl` | `font-normal` (400) | `leading-relaxed` |
| **Corpo do Texto (Parágrafos)** | `text-sm sm:text-base` | `font-normal` (400) | `leading-relaxed` |
| **Títulos de Serviços / Listas** | `text-base` | `font-semibold` (600) | Padrão |
| **Legendas / Detalhes de Serviços**| `text-xs sm:text-sm` | `font-normal` (400) | Padrão |
| **Numeração de Pilares** | `text-base` | `font-bold` (700) | `uppercase tracking-widest` |
| **Tooltips & Badges Menores** | `text-[10px]` (10px) / `text-[11px]` (11px) | `font-medium` (500) / `font-semibold` (600) | `uppercase tracking-wider` |
| **Rodapé / Copyright** | `text-xs` (12px) e `text-[11px]` (11px) | `font-normal` (400) | Padrão |

---

## 4. Botões e Ações Interativas (CTAs)

### 4.1 Botão CTA do Header (Pill Button com Pulso)
- **Classes:** `inline-flex items-center gap-2 px-3.5 sm:px-4 py-1.5 text-xs font-semibold text-white bg-brandBlue hover:bg-brandBlueHover rounded-full transition-all duration-200 shadow-sm hover:scale-[1.02] active:scale-[0.98]`
- **Detalhes:** Possui formato cápsula (`rounded-full`), leve efeito de escala no hover e bolinha interna com animação contínua de pulso (`w-1.5 h-1.5 rounded-full bg-white animate-pulse`).

### 4.2 Botão CTA Principal da Hero Section (Grande)
- **Classes:** `inline-flex items-center justify-center px-8 py-3.5 text-base font-semibold text-white bg-brandBlue hover:bg-brandBlueHover rounded transition-colors shadow-sm`
- **Arredondamento:** `rounded` (0.25rem / 4px).

### 4.3 Botões de Ação de Bloco / Seções (Médio)
- **Classes:** `inline-flex items-center justify-center px-6 py-3 text-sm font-semibold text-white bg-brandBlue hover:bg-brandBlueHover rounded transition-colors`
- **Utilização:** "Avaliar meu celular agora", "Ver catálogo e preços no WhatsApp".

### 4.4 Botões de Contato (Split na seção Onde Estamos)
- **WhatsApp (Primário):** `inline-flex items-center justify-center flex-1 px-5 py-3 text-sm font-semibold text-white bg-brandBlue hover:bg-brandBlueHover transition-colors text-center`
- **Instagram (Secundário Escuro):** `inline-flex items-center justify-center gap-2 px-5 py-3 text-sm font-semibold text-neutral-200 bg-brandDark hover:bg-neutral-800 border border-brandBorder transition-colors text-center`

### 4.5 Botões de Controle do VSL (Player de Vídeo)
- **Sound Toggle (`#vsl-unmute-btn`):** `inline-flex items-center gap-2 h-8 px-3 rounded-md bg-zinc-900 text-zinc-100 border border-zinc-800 hover:bg-zinc-800/80 hover:border-zinc-700 hover:text-zinc-50 active:scale-[0.98] transition-all duration-150 ease-out`
- **Play/Pause Indicator:** `inline-flex items-center justify-center h-10 w-10 rounded-md bg-zinc-900 text-zinc-100 border border-zinc-800 shadow-xl`

### 4.6 Botões de Redes Sociais com Tooltip (Footer)
- **Container Externo:** `flex items-center gap-2 px-3 py-1.5 rounded-md border border-brandBorder bg-brandCard`
- **Item Social:** `social-link group relative flex items-center justify-center w-9 h-9 rounded transition-colors`
- **Efeito Hover:**
  - Balão `hover-bg`: `absolute inset-0 rounded bg-white/10 opacity-0 scale-90 transition-all` (expande para `opacity: 1; transform: scale(1);`).
  - Ícone: Transição de `text-neutral-400` para `text-white`.
  - Tooltip: `absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded bg-white text-neutral-900 text-[10px] font-medium whitespace-nowrap opacity-0 translate-y-1 transition-all` (aparece com `opacity: 1; transform: translateX(-50%) translateY(0)`).

---

## 5. Estrutura de Layout e Containers

### 5.1 Grid e Largura Máxima
- **Container Central:** `max-w-6xl mx-auto` com padding horizontal `px-4 sm:px-6`.
- **Espaçamento entre Seções:** `space-y-16 sm:space-y-24`.
- **Linha divisória de Seção:** `border-t border-brandBorder pt-12 scroll-mt-20`.
- **Grids mais comuns:**
  - 12 colunas split (Assistência Técnica e Loja): `grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12`.
  - 4 colunas (Mídia/Bastidores e Trust signals): `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6` / `grid grid-cols-2 md:grid-cols-4 gap-3`.
  - 3 colunas (Pilares / 3 Motivos): `grid grid-cols-1 md:grid-cols-3 gap-6`.
  - 2 colunas (Contato / Localização): `grid grid-cols-1 md:grid-cols-2 gap-6`.

### 5.2 Estilo dos Cards
- **Card Padrão:**
  - Fundo: `#27292c` (`bg-brandCard`)
  - Borda: `1px solid #34373b` (`border border-brandBorder`)
  - Arredondamento: `rounded-lg` (0.5rem / 8px) ou `rounded` (0.25rem / 4px)
  - Hover de interação: `transition-all hover:border-neutral-500`
  - Padding padrão: `p-4`, `p-5 sm:p-6` ou `p-6 sm:p-8`

### 5.3 Proporções de Mídia (Aspect Ratio)
- **Player VSL Hero:** `aspect-[9/16]` (vertical estilo Stories/Reels), largura máx `max-w-[290px] sm:max-w-[330px]`, cantos `rounded-lg`, fundo `bg-black`, borda `border-brandBorder` e sombra `shadow-2xl`.
- **Galeria de Bastidores:** `aspect-[4/3]` nos vídeos e fotos.
- **Cards da Galeria Inclinada (Showcase):**
  - Desktop: `270px x 165px`, raio `0.5rem`, borda `1px solid #34373b`, `hover:border-color: #1e61e8`.
  - Mobile (≤768px): `190px x 125px`.
  - Inclinação do container: `transform: rotate(-2.5deg) scale(1.04)` (Desktop) e `rotate(-1.5deg) scale(1.02)` (Mobile).

---

## 6. Animações e Efeitos Especiais

### 6.1 Animação de Entrada (Fade In)
```css
@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}
/* Classe: animate-fade-in (0.6s ease-out forwards) */
```

### 6.2 Loader (Tela de Carregamento)
- Fundo: `#202224` em tela cheia fixa (`fixed inset-0 z-50`).
- Imagem: GIF/WebP com `max-w-[260px] sm:max-w-[300px]`.
- Barra de Progresso: Altura de `1.5` (6px), largura `w-48 sm:w-60`, fundo `bg-white/10` arredondado, preenchimento com `bg-brandBlue transition-all duration-200 ease-out`.
- Transição de Saída: `transition-opacity duration-500 ease-in-out` para desaparecer suavemente, liberando o `main-content` que transiciona com `duration-700 ease-out`.

### 6.3 Showcase Inclinado Infinito
- Duas trilhas com rolagem contínua via `requestAnimationFrame`.
- Trilha esquerda corre para a esquerda; trilha direita corre para a direita com velocidade constante de `0.55px/frame`.
- Efeito sonoro / reprodução sob demanda via `IntersectionObserver` e `mouseenter`/`mouseleave`.
