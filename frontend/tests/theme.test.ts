import { describe, expect, it } from "vitest";

import { cycleTheme, flowColorMode } from "@/lib/theme";

describe("cycleTheme", () => {
  it("cycles light → dark → system → light", () => {
    expect(cycleTheme("light")).toBe("dark");
    expect(cycleTheme("dark")).toBe("system");
    expect(cycleTheme("system")).toBe("light");
  });

  it("falls back undefined to system, then advances one step to light", () => {
    expect(cycleTheme(undefined)).toBe(cycleTheme("system"));
    expect(cycleTheme(undefined)).toBe("light");
  });
});

describe("flowColorMode", () => {
  it("maps next-themes resolvedTheme to React Flow colorMode", () => {
    expect(flowColorMode("dark")).toBe("dark");
    expect(flowColorMode("light")).toBe("light");
  });

  it("does not follow the OS: undefined (pre-hydration) stays light, not system", () => {
    expect(flowColorMode(undefined)).toBe("light");
    expect(flowColorMode("system")).toBe("light");
  });
});
