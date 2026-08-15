"use client"

import React, { useState, useEffect } from "react"

export interface ShowcaseItem {
  id: string
  category: string
  title: string
  subtitle: string
  badge: string
  kpi: string
  gradientClass: string
  borderClass: string
  glowClass: string
  description: string
  features: string[]
  specs: Record<string, string>
}

const showcaseData: ShowcaseItem[] = [
  {
    id: "dash-executivo",
    category: "Dashboard & Analytics",
    title: "Dashboard Executivo",
    subtitle: "Visão geral de faturamento e lucro em tempo real.",
    badge: "Módulo Principal",
    kpi: "R$ 148.500,00 Hoje",
    gradientClass: "from-indigo-900/80 via-purple-950/60 to-neutral-900",
    borderClass: "border-indigo-500/30 hover:border-indigo-500/80",
    glowClass: "shadow-indigo-500/20",
    description: "Painel executivo completo com acompanhamento de metas diárias, faturamento consolidado por loja, gráfico de tendência de vendas e margem de lucro em tempo real.",
    features: [
      "Métricas atualizadas instantaneamente sem recarregar",
      "Comparativo mensal, trimestral e anual automático",
      "Exportação de relatórios em PDF, Excel e CSV",
      "Alertas automáticos de metas e desvios de desempenho",
    ],
    specs: {
      "Módulo": "Analytics & BI",
      "Status": "Ativo 24/7",
      "Frequência": "Tempo Real",
      "Acesso": "Gestores e Admins",
    },
  },
  {
    id: "estoque-multiloja",
    category: "Gestão de Estoque",
    title: "Estoque Multi-Loja",
    subtitle: "Transferências e saldo unificado entre filiais.",
    badge: "Logística",
    kpi: "12 Filiais Conectadas",
    gradientClass: "from-blue-900/80 via-slate-950/60 to-neutral-900",
    borderClass: "border-blue-500/30 hover:border-blue-500/80",
    glowClass: "shadow-blue-500/20",
    description: "Controle inteligente de inventário para redes de lojas e galpões. Acompanhe a quantidade disponível em cada filial, movimentações de transferência e rastreamento de lote.",
    features: [
      "Transferência entre filiais com aprovação rápida",
      "Rastreamento por código de barras, QR Code e SKU",
      "Histórico completo e inalterável de entradas e saídas",
      "Contagem de inventário cego via aplicativo mobile",
    ],
    specs: {
      "Módulo": "Logística e Inventário",
      "Status": "Sincronizado",
      "Identificação": "Código de Barras / QR",
      "Alertas": "Notificação Estoque Baixo",
    },
  },
  {
    id: "pdv-checkout",
    category: "Vendas & PDV",
    title: "PDV Frente de Caixa",
    subtitle: "Checkout ultra-rápido com múltiplos pagamentos.",
    badge: "Vendas Diretas",
    kpi: "< 3s por Venda",
    gradientClass: "from-emerald-900/80 via-teal-950/60 to-neutral-900",
    borderClass: "border-emerald-500/30 hover:border-emerald-500/80",
    glowClass: "shadow-emerald-500/20",
    description: "Ponto de venda moderno projetado para velocidade no atendimento. Suporta pagamento via Pix com QR Code dinâmico, Cartões, Boleto e NFC-e rápida.",
    features: [
      "Integração direta com TEF e maquininhas de cartão",
      "Geração e validação instantânea de Pix dinâmico",
      "Modo contingência offline com sincronização automática",
      "Aplicação de descontos e cupons parametrizados",
    ],
    specs: {
      "Módulo": "Frente de Caixa",
      "Status": "Híbrido Online/Offline",
      "Fiscal": "NFC-e / SAT / NF-e",
      "Desempenho": "Checkout em < 3s",
    },
  },
  {
    id: "alertas-compra",
    category: "Automação",
    title: "Reposição Inteligente",
    subtitle: "Sugestão automática de compra baseada em IA.",
    badge: "Automação IA",
    kpi: "Zero Ruptura",
    gradientClass: "from-amber-900/80 via-orange-950/60 to-neutral-900",
    borderClass: "border-amber-500/30 hover:border-amber-500/80",
    glowClass: "shadow-amber-500/20",
    description: "Algoritmo preditivo que analisa o giro de cada produto e calcula automaticamente o ponto de pedido e o lote ideal para evitar faltas sem imobilizar capital.",
    features: [
      "Sugestão automática de pedidos enviada aos fornecedores",
      "Cálculo de cobertura de estoque em dias restantes",
      "Identificação de produtos sem movimentação",
      "Classificação em curva ABC por rentabilidade",
    ],
    specs: {
      "Módulo": "Automação de Compras",
      "Status": "Motor de IA Ativo",
      "Análise": "Preditiva de Demanda",
      "Canais": "E-mail & WhatsApp",
    },
  },
  {
    id: "financeiro-dre",
    category: "Gestão Financeira",
    title: "Fluxo de Caixa & DRE",
    subtitle: "Contas a pagar, receber e DRE gerencial.",
    badge: "Financeiro",
    kpi: "Margem 34%",
    gradientClass: "from-purple-900/80 via-violet-950/60 to-neutral-900",
    borderClass: "border-purple-500/30 hover:border-purple-500/80",
    glowClass: "shadow-purple-500/20",
    description: "Gestão financeira corporativa simplificada. Conciliação bancária automática, gestão de centros de custo e DRE gerencial estruturado.",
    features: [
      "Importação de extratos OFX e integração bancária",
      "Cálculo automático de comissões por vendedor",
      "Categorização inteligente de receitas e despesas",
      "Visão consolidada do fluxo de caixa diário",
    ],
    specs: {
      "Módulo": "Controladoria & Finanças",
      "Status": "Auditado",
      "Conciliação": "Automática via API/OFX",
      "Relatórios": "DRE Gerencial em 1 Clique",
    },
  },
  {
    id: "app-mobile",
    category: "Mobilidade",
    title: "App Mobile & Tablet",
    subtitle: "Gestão na palma da sua mão onde você estiver.",
    badge: "iOS & Android",
    kpi: "App Nativo",
    gradientClass: "from-rose-900/80 via-pink-950/60 to-neutral-900",
    borderClass: "border-rose-500/30 hover:border-rose-500/80",
    glowClass: "shadow-rose-500/20",
    description: "Aplicativo completo para smartphones e tablets. Permite consultar estoque, aprovar ordens de compra e acompanhar vendas em tempo real de qualquer lugar.",
    features: [
      "Notificações em tempo real sobre vendas e alertas",
      "Leitura de código de barras pela câmera do celular",
      "Modo de atendimento móvel na loja física",
      "Painel resumido em cards com FaceID / Biometria",
    ],
    specs: {
      "Módulo": "Mobilidade",
      "Status": "App Store & Play Store",
      "Segurança": "Criptografia End-to-End",
      "Interface": "Design Touch Otimizado",
    },
  },
  {
    id: "gestao-fornecedores",
    category: "Compras",
    title: "Portal de Fornecedores",
    subtitle: "Histórico de cotações, prazos e compras.",
    badge: "Suprimentos",
    kpi: "140+ Parceiros",
    gradientClass: "from-sky-900/80 via-indigo-950/60 to-neutral-900",
    borderClass: "border-sky-500/30 hover:border-sky-500/80",
    glowClass: "shadow-sky-500/20",
    description: "Central de relacionamento e cotação de compras. Compare preços de fornecedores, acompanhe o prazo de entrega prometido vs. entregue e lance notas via XML.",
    features: [
      "Importação automática de notas fiscais via XML",
      "Tabela comparativa de cotações de fornecedores",
      "Métrica de pontualidade e conformidade de entregas",
      "Cadastro de códigos de fornecedores vinculados ao SKU",
    ],
    specs: {
      "Módulo": "Gestão de Fornecedores",
      "Status": "Integrado com SEFAZ",
      "Importação": "XML NF-e",
      "Histórico": "Permanente",
    },
  },
  {
    id: "seguranca-auditoria",
    category: "Segurança",
    title: "Permissões & Auditoria",
    subtitle: "Perfis de acesso personalizados e log detalhado.",
    badge: "Proteção",
    kpi: "LGPD OK",
    gradientClass: "from-slate-900/80 via-zinc-950/60 to-neutral-900",
    borderClass: "border-slate-500/30 hover:border-slate-500/80",
    glowClass: "shadow-slate-500/20",
    description: "Sistema completo de controle de acessos e auditoria. Proteja dados sensíveis limitando visualizações por função e rastreie todas as ações no sistema.",
    features: [
      "Perfis de acesso granulares (Caixa, Vendedor, Gerente, Admin)",
      "Registro detalhado de IP, horário e ação realizada",
      "Autenticação em duas etapas (2FA)",
      "Backups diários automatizados com retenção",
    ],
    specs: {
      "Módulo": "Segurança & Compliance",
      "Status": "Criptografia AES-256",
      "Conformidade": "LGPD",
      "Backup": "Automático Diário em Nuvem",
    },
  },
]

export function TiltedShowcase() {
  const [selectedItemIndex, setSelectedItemIndex] = useState<number | null>(null)

  const activeItem = selectedItemIndex !== null ? showcaseData[selectedItemIndex] : null

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (selectedItemIndex === null) return
      if (e.key === "Escape") setSelectedItemIndex(null)
      if (e.key === "ArrowRight") setSelectedItemIndex((prev) => (prev !== null ? (prev + 1) % showcaseData.length : 0))
      if (e.key === "ArrowLeft") setSelectedItemIndex((prev) => (prev !== null ? (prev - 1 + showcaseData.length) % showcaseData.length : 0))
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [selectedItemIndex])

  const track1 = [...showcaseData.slice(0, 4), ...showcaseData.slice(0, 4), ...showcaseData.slice(0, 4)]
  const track2 = [...showcaseData.slice(4, 8), ...showcaseData.slice(4, 8), ...showcaseData.slice(4, 8)]

  return (
    <div className="w-full relative overflow-hidden py-10">
      {/* Lateral gradient masks */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-24 sm:w-48 bg-gradient-to-r from-neutral-950 via-neutral-950/80 to-transparent z-20" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-24 sm:w-48 bg-gradient-to-l from-neutral-950 via-neutral-950/80 to-transparent z-20" />

      {/* Tilted Marquee Wrapper */}
      <div className="flex flex-col gap-5 -rotate-2.5 scale-104 w-[130vw] -ml-[15vw]">
        {/* Track 1 - Left */}
        <div className="flex gap-5 w-max animate-[rolarEsquerda_75s_linear_infinite]">
          {track1.map((item, idx) => (
            <ShowcaseCard key={`t1-${item.id}-${idx}`} item={item} onClick={() => setSelectedItemIndex(showcaseData.findIndex(s => s.id === item.id))} />
          ))}
        </div>

        {/* Track 2 - Right */}
        <div className="flex gap-5 w-max animate-[rolarDireita_75s_linear_infinite]">
          {track2.map((item, idx) => (
            <ShowcaseCard key={`t2-${item.id}-${idx}`} item={item} onClick={() => setSelectedItemIndex(showcaseData.findIndex(s => s.id === item.id))} />
          ))}
        </div>
      </div>

      {/* Modal Dialog */}
      {activeItem && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-in fade-in-0 duration-200"
          onClick={() => setSelectedItemIndex(null)}
        >
          <div
            className="relative w-full max-w-2xl bg-neutral-900 border border-neutral-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] text-white animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-neutral-950/50">
              <div className="flex items-center gap-3">
                <span className="px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-semibold uppercase tracking-wider">
                  {activeItem.category}
                </span>
                <span classText="text-xs text-neutral-500">|</span>
                <span className="text-xs text-neutral-400 font-medium">{activeItem.badge}</span>
              </div>
              <button
                onClick={() => setSelectedItemIndex(null)}
                className="w-8 h-8 rounded-lg bg-neutral-800/80 hover:bg-neutral-700 text-neutral-400 hover:text-white flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              <div className={`relative w-full h-44 sm:h-52 rounded-xl bg-gradient-to-br ${activeItem.gradientClass} border border-white/10 p-6 flex flex-col justify-between overflow-hidden shadow-inner`}>
                <div className="flex items-center justify-between z-10">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                  </div>
                  <span className="px-3 py-1 rounded-full bg-neutral-950/80 border border-white/10 text-xs font-semibold text-white tracking-wide">
                    {activeItem.kpi}
                  </span>
                </div>

                <div className="flex items-end justify-between z-10">
                  <div>
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">{activeItem.title}</h3>
                    <p className="text-xs sm:text-sm text-neutral-300 mt-1">{activeItem.subtitle}</p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">Visão Geral do Recurso</h4>
                <p className="text-sm text-neutral-300 leading-relaxed">{activeItem.description}</p>
              </div>

              <div>
                <h4 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-3">Principais Capacidades</h4>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {activeItem.features.map((feat, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-xs sm:text-sm text-neutral-300">
                      <span className="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mt-0.5 border border-emerald-500/30">
                        ✓
                      </span>
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-3">Especificações & Frequência</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {Object.entries(activeItem.specs).map(([key, val]) => (
                    <div key={key} className="bg-neutral-950/70 p-3 rounded-lg border border-white/5 flex flex-col gap-0.5">
                      <span className="text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{key}</span>
                      <span className="text-xs sm:text-sm font-medium text-neutral-200 truncate">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-white/10 bg-neutral-950/60 flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedItemIndex((prev) => (prev !== null ? (prev - 1 + showcaseData.length) % showcaseData.length : 0))}
                  className="px-3 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-xs font-medium text-neutral-300 hover:text-white transition-colors"
                >
                  ← Anterior
                </button>
                <button
                  onClick={() => setSelectedItemIndex((prev) => (prev !== null ? (prev + 1) % showcaseData.length : 0))}
                  className="px-3 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-xs font-medium text-neutral-300 hover:text-white transition-colors"
                >
                  Próximo →
                </button>
              </div>
              <button
                onClick={() => setSelectedItemIndex(null)}
                className="px-4 py-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-xs font-medium text-neutral-300 transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ShowcaseCard({ item, onClick }: { item: ShowcaseItem; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className={`w-[270px] h-[165px] shrink-0 rounded-xl p-4 flex flex-col justify-between backdrop-blur-md bg-neutral-900/90 border ${item.borderClass} shadow-xl ${item.glowClass} cursor-pointer relative overflow-hidden`}
    >
      <div className={`absolute inset-0 rounded-xl bg-gradient-to-br ${item.gradientClass} opacity-40 pointer-events-none`} />

      <div className="relative z-10 flex items-center justify-between">
        <span className="px-2 py-0.5 rounded-full bg-neutral-950/80 border border-white/10 text-[10px] font-medium text-neutral-300 tracking-wider">
          {item.category}
        </span>
      </div>

      <div className="relative z-10 my-2">
        <h4 className="text-sm font-bold text-white line-clamp-1">{item.title}</h4>
        <p className="text-[11px] text-neutral-400 line-clamp-1 mt-0.5">{item.subtitle}</p>
      </div>

      <div className="relative z-10 flex items-center justify-between pt-2 border-t border-white/[0.08]">
        <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          {item.kpi}
        </span>
        <span className="text-[10px] font-medium text-neutral-400 flex items-center gap-1">
          Detalhes →
        </span>
      </div>
    </div>
  )
}

export default TiltedShowcase
