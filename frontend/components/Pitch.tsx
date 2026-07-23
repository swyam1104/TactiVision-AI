import React from "react";

interface PitchProps {
  children?: React.ReactNode;
  className?: string;
  onClick?: (x: number, y: number) => void;
}

export default function Pitch({ children, className = "", onClick }: PitchProps) {
  const handlePitchClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!onClick) return;
    
    // Get SVG element bounds to calculate relative coordinates
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;
    
    // Convert click coordinates to StatsBomb 120x80 coordinates
    const sbX = (clickX / rect.width) * 120;
    const sbY = (clickY / rect.height) * 80;
    
    onClick(roundToDecimal(sbX, 1), roundToDecimal(sbY, 1));
  };

  const roundToDecimal = (num: number, decimals: number) => {
    const factor = Math.pow(10, decimals);
    return Math.round(num * factor) / factor;
  };

  return (
    <div className={`relative w-full aspect-[120/80] bg-pitch-dark rounded-xl border border-border overflow-hidden select-none shadow-2xl ${className}`}>
      <svg
        viewBox="0 0 120 80"
        className="w-full h-full cursor-crosshair"
        onClick={handlePitchClick}
      >
        {/* Grass background with subtle gradient */}
        <defs>
          <radialGradient id="pitchGrad" cx="50%" cy="50%" r="75%">
            <stop offset="0%" stopColor="#153e20" />
            <stop offset="100%" stopColor="#0b2411" />
          </radialGradient>
        </defs>
        <rect width="120" height="80" fill="url(#pitchGrad)" />

        {/* Pitch outer boundary */}
        <rect
          x="0"
          y="0"
          width="120"
          height="80"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />

        {/* Halfway line */}
        <line
          x1="60"
          y1="0"
          x2="60"
          y2="80"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />

        {/* Center circle */}
        <circle
          cx="60"
          cy="40"
          r="9.15"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />
        <circle cx="60" cy="40" r="0.5" fill="var(--pitch-lines)" />

        {/* Penalty Box Left */}
        <rect
          x="0"
          y="18"
          width="18"
          height="44"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />
        {/* Six-Yard Box Left */}
        <rect
          x="0"
          y="30"
          width="6"
          height="20"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />
        {/* Penalty Spot Left */}
        <circle cx="12" cy="40" r="0.5" fill="var(--pitch-lines)" />
        {/* Penalty Arc Left */}
        <path
          d="M 18,30.8 A 9.15,9.15 0 0,1 18,49.2"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />

        {/* Penalty Box Right */}
        <rect
          x="102"
          y="18"
          width="18"
          height="44"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />
        {/* Six-Yard Box Right */}
        <rect
          x="114"
          y="30"
          width="6"
          height="20"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />
        {/* Penalty Spot Right */}
        <circle cx="108" cy="40" r="0.5" fill="var(--pitch-lines)" />
        {/* Penalty Arc Right */}
        <path
          d="M 102,30.8 A 9.15,9.15 0 0,0 102,49.2"
          fill="none"
          stroke="var(--pitch-lines)"
          strokeWidth="0.8"
        />

        {/* Goalposts Left */}
        <line x1="0" y1="36" x2="0" y2="44" stroke="#ffffff" strokeWidth="1.5" />
        {/* Goalposts Right */}
        <line x1="120" y1="36" x2="120" y2="44" stroke="#ffffff" strokeWidth="1.5" />

        {/* Child visual elements */}
        {children}
      </svg>
    </div>
  );
}
