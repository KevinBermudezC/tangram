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

  it("lets .dark override every editor-chrome token those utilities read", async () => {
    const css = await compileThemeCss();
    const darkOverrides: Array<[string, string]> = [
      ["--color-page", "#121212"],
      ["--color-card", "#1a1a1a"],
      ["--color-canvas", "#141414"],
      ["--color-sidebar", "#0e0e0e"],
      ["--color-chat", "#161616"],
      ["--color-ink-strong", "#f2f2f0"],
      ["--color-ink-faint", "#6e6e68"],
      ["--color-line-strong", "#3c3c38"],
    ];
    for (const [variable, value] of darkOverrides) {
      expect(css, `.dark must override ${variable}`).toMatch(
        new RegExp(`\\.dark\\s*\\{[^}]*${variable}:\\s*${value}`),
      );
    }
  });

  it("wires React Flow colorMode from next-themes resolvedTheme, not the OS", () => {
    const src = readFileSync(path.join(frontendRoot, "components/DiagramCanvas.tsx"), "utf8");
    expect(src).toContain("const { resolvedTheme } = useTheme()");
    expect(src).toContain("flowColorMode(resolvedTheme, mounted)");
    expect(src).toContain("colorMode={colorMode}");
    const withoutComments = src
      .replace(/\/\*[\s\S]*?\*\//g, "")
      .replace(/\/\/.*$/gm, "");
    expect(withoutComments).not.toMatch(/colorMode=["']system["']/);
    expect(withoutComments).not.toContain("#9a958c");
    expect(withoutComments).not.toContain("#b9b2a6");
  });

  it("keeps inverted ink readable on the AI panel (no light-only peach + ink-strong)", () => {
    const src = readFileSync(
      path.join(frontendRoot, "components/editor/chat-panel.tsx"),
      "utf8",
    );
    expect(src).not.toMatch(/bg-ink-strong[^"'`]*text-ink-on-accent/);
    expect(src).not.toContain("#fdebdf");
    expect(src).not.toContain("--bg-msg-user");
    expect(src).not.toContain("text-[#a12525]");
  });
});
