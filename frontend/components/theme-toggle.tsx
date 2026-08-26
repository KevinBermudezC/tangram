"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { cycleTheme, themeLabel, type TangramTheme } from "@/lib/theme";

interface ThemeToggleProps {
  className?: string;
}

/**
 * Cycles light → dark → system. Renders a stable placeholder until mounted
 * so SSR / hydration don't flash the wrong icon.
 */
export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const current = (theme as TangramTheme | undefined) ?? "system";
  const label = mounted ? themeLabel(current) : "Theme";
  const next = cycleTheme(mounted ? current : undefined);

  return (
    <Button
      variant="ghost"
      size="icon"
      className={className}
      aria-label={`Theme: ${label}. Click for ${themeLabel(next)}.`}
      title={`Theme: ${label}`}
      disabled={!mounted}
      onClick={() => setTheme(cycleTheme(current))}
    >
      {!mounted || current === "system" ? (
        <Monitor size={14} />
      ) : current === "dark" ? (
        <Moon size={14} />
      ) : (
        <Sun size={14} />
      )}
    </Button>
  );
}
