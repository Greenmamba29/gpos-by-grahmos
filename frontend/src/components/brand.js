import React from "react";

// Grahmos shield mark — constant across the product
export function GrahmosShield({ size = 28, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 44" fill="none"
      className={className} aria-label="Grahmos">
      <path d="M20 2 L36 8 V22 C36 33 29 40 20 42 C11 40 4 33 4 22 V8 Z"
        fill="hsl(214 63% 12%)" stroke="hsl(173 84% 41%)" strokeWidth="1.5" />
      <path d="M25 15.5 C23.5 14 21.8 13.3 20 13.3 C16 13.3 13 16.3 13 20.3 C13 24.3 16 27.3 20 27.3 C23 27.3 25.4 25.6 26.4 23 L20 23 V20 L29 20 C29 25.6 25 30.5 20 30.5 C14.4 30.5 10 26 10 20.3 C10 14.6 14.4 10.1 20 10.1 C22.8 10.1 25.3 11.2 27.1 13 Z"
        fill="white" />
    </svg>
  );
}

export function Wordmark({ collapsed = false }) {
  return (
    <div className="flex items-center gap-2.5">
      <GrahmosShield size={30} />
      {!collapsed && (
        <div className="leading-tight">
          <div className="text-[15px] font-bold tracking-[-0.01em] text-[hsl(var(--g-navy-950))]">GPOS</div>
          <div className="text-[10px] font-medium uppercase tracking-[0.14em] text-[hsl(var(--g-teal-700))]">by Grahmos</div>
        </div>
      )}
    </div>
  );
}
