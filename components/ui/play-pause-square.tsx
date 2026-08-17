import React, { useState } from 'react';
import { Play, Pause } from 'lucide-react';

export interface PlayPauseSquareProps {
  /** Estado inicial de reprodução (padrão: false / pausado) */
  initialPlaying?: boolean;
  /** Callback disparado ao alternar o estado de reprodução */
  onToggle?: (isPlaying: boolean) => void;
  /** Classes Tailwind extras para customização */
  className?: string;
}

export function PlayPauseSquare({
  initialPlaying = false,
  onToggle,
  className = "",
}: PlayPauseSquareProps) {
  const [isPlaying, setIsPlaying] = useState(initialPlaying);

  const handleToggle = () => {
    const nextState = !isPlaying;
    setIsPlaying(nextState);
    onToggle?.(nextState);
  };

  return (
    <button
      type="button"
      onClick={handleToggle}
      aria-label={isPlaying ? "Pausar vídeo" : "Reproduzir vídeo"}
      title={isPlaying ? "Pausar" : "Reproduzir"}
      className={`
        inline-flex items-center justify-center h-8 w-8
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
      {isPlaying ? (
        <Pause className="w-4 h-4 text-zinc-300 transition-colors fill-zinc-300/20" />
      ) : (
        <Play className="w-4 h-4 text-zinc-300 transition-colors fill-zinc-300 translate-x-[0.5px]" />
      )}
    </button>
  );
}

export default PlayPauseSquare;
