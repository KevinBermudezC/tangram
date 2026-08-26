import { describe, expect, it } from "vitest";

import { cycleTheme } from "@/lib/theme";

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
