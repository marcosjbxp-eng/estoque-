import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

export interface SoundToggleSquareProps {
  /** Estado inicial do som (true = mutado). Padrão: true */
  initialMuted?: boolean;
  /** Callback executado ao alternar o som */
  onToggle?: (isMuted: boolean) => void;
  /** Texto exibido quando mutado. Padrão: "Ouvir com som" */
  mutedText?: string;
  /** Texto exibido quando com som ativado. Padrão: "Som ativado" */
  activeText?: string;
  /** Classes Tailwind adicionais para estilização e posicionamento */
  className?: string;
}

/**
 * Componente SoundToggleSquare (Variante Square Radius - shadcn/ui style)
 * Design sóbrio com bordas arredondadas de 6px (rounded-md), focado em eficiência e legibilidade.
 */
export function SoundToggleSquare({
  initialMuted = true,
  onToggle,
  mutedText = "Ouvir com som",
  activeText = "Som ativado",
  className = "",
}: SoundToggleSquareProps) {
  const [isMuted, setIsMuted] = useState(initialMuted);

  const handleToggle = () => {
    const nextState = !isMuted;
    setIsMuted(nextState);
    if (onToggle) {
      onToggle(nextState);
    }
  };

  return (
    <button
      type="button"
      onClick={handleToggle}
      aria-label={isMuted ? "Ativar som do vídeo" : "Desativar som do vídeo"}
      title={isMuted ? mutedText : activeText}
      className={`
        inline-flex items-center gap-2 h-8 px-3
        rounded-md bg-zinc-900 text-zinc-100 
        border border-zinc-800 
        hover:bg-zinc-800/80 hover:border-zinc-700 hover:text-zinc-50
        active:scale-[0.98] 
        transition-all duration-150 ease-out 
        focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400 
        cursor-pointer select-none
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {isMuted ? (
        <VolumeX className="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-300 transition-colors" />
      ) : (
        <Volume2 className="w-3.5 h-3.5 text-zinc-300 transition-colors" />
      )}
      <span className="text-xs font-medium tracking-tight text-zinc-200">
        {isMuted ? mutedText : activeText}
      </span>
    </button>
  );
}

export default SoundToggleSquare;
