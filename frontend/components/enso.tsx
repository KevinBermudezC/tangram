interface EnsoProps {
  /** Pixel size of the square. */
  size?: number;
  className?: string;
}

/**
 * Ensō (円相) — the zen brush circle, drawn in a single open stroke. Used as a
 * loading mark: it rotates slowly, and the gap in the ring keeps it feeling
 * hand-painted rather than mechanical. Stroke uses the accent (shu) so it
 * reads as a vermilion ink mark on the washi background.
 */
export function Enso({ size = 32, className }: EnsoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      aria-hidden
      className={className}
      style={{ animation: "enso-spin 2.4s cubic-bezier(0.5, 0.1, 0.4, 0.95) infinite" }}
    >
      {/* ~315° arc, open at the top-right, with tapering round caps to mimic a
          brush lifting off the paper. */}
      <path
        d="M30 6.6 A19 19 0 1 0 41 19"
        stroke="var(--color-accent)"
        strokeWidth="3.6"
        strokeLinecap="round"
      />
    </svg>
  );
}
