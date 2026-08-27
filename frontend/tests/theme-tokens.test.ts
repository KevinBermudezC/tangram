import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import postcss from "postcss";
import tailwindcss from "@tailwindcss/postcss";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const globalsPath = path.join(frontendRoot, "app/globals.css");

const SEMANTIC_UTILITIES = [
  { utility: "bg-page", property: "background-color", variable: "--color-page" },
  { utility: "bg-card", property: "background-color", variable: "--color-card" },
  { utility: "bg-sidebar", property: "background-color", variable: "--color-sidebar" },
  { utility: "bg-canvas", property: "background-color", variable: "--color-canvas" },
  { utility: "bg-chat", property: "background-color", variable: "--color-chat" },
  { utility: "text-ink-strong", property: "color", variable: "--color-ink-strong" },
  { utility: "border-line", property: "border-color", variable: "--color-line" },
] as const;

async function compileThemeCss(): Promise<string> {
  const classes = SEMANTIC_UTILITIES.map((u) => u.utility).join(" ");
  const input = `@import "./app/globals.css";\n@source inline("${classes}");\n`;
  const result = await postcss([tailwindcss()]).process(input, {
    from: path.join(frontendRoot, "theme-tokens.check.css"),
  });
  return result.css;
}

function utilityBlock(css: string, className: string): string {
  const escaped = className.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = css.match(new RegExp(`\\.${escaped}\\s*\\{[^}]+\\}`));
  expect(match, `expected compiled CSS to contain .${className}`).toBeTruthy();
  return match![0];
}

describe("semantic color tokens", () => {
  it("declares a class-based dark variant so next-themes html.dark is honored", () => {
    const source = readFileSync(globalsPath, "utf8");
    expect(source).toMatch(/@custom-variant\s+dark\s*\(\s*&:where\(\.dark,\s*\.dark\s+\*\)\s*\)/);
  });

  it("compiles surface/ink utilities as var() references, not inlined light hex", async () => {
    const css = await compileThemeCss();

    for (const { utility, property, variable } of SEMANTIC_UTILITIES) {
      const block = utilityBlock(css, utility);
      expect(block, `${utility} must use ${variable}`).toContain(`var(${variable})`);
      expect(block, `${utility} must not inline a hex ${property}`).not.toMatch(
        new RegExp(`${property}\\s*:\\s*#`),
      );
    }
  });

  it("lets .dark override the page token used by those utilities", async () => {
    const css = await compileThemeCss();
    expect(css).toMatch(/\.dark\s*\{[^}]*--color-page:\s*#121212/);
    expect(css).toMatch(/\.dark\s*\{[^}]*--color-sidebar:\s*#0e0e0e/);
    expect(css).toMatch(/\.dark\s*\{[^}]*--color-ink-strong:\s*#f2f2f0/);
  });
});
