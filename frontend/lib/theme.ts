export type TangramTheme = "light" | "dark" | "system";

/** React Flow's `colorMode` — only `light` | `dark` (not `system`). */
export type FlowColorMode = "light" | "dark";

const ORDER: TangramTheme[] = ["light", "dark", "system"];

/**
 * Map next-themes `resolvedTheme` onto React Flow's colorMode.
 *
 * React Flow v12 defaults to `"light"` and treats `"system"` as a second OS
 * listener (`prefers-color-scheme`). Tangram's source of truth is the
 * next-themes class on `<html>`, so we never pass `"system"`.
 */
export function flowColorMode(
  resolvedTheme: string | undefined,
): FlowColorMode {
  return resolvedTheme === "dark" ? "dark" : "light";
}

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
