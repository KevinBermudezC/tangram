export type TangramTheme = "light" | "dark" | "system";

const ORDER: TangramTheme[] = ["light", "dark", "system"];

/** Next theme in the light → dark → system loop. */
export function cycleTheme(current: TangramTheme | undefined): TangramTheme {
  const resolved: TangramTheme =
    current === "light" || current === "dark" || current === "system"
      ? current
      : "system";
  const idx = ORDER.indexOf(resolved);
  return ORDER[(idx + 1) % ORDER.length]!;
}

export function themeLabel(theme: TangramTheme | undefined): string {
  switch (theme) {
    case "light":
      return "Light";
    case "dark":
      return "Dark";
    case "system":
    default:
      return "System";
  }
}
