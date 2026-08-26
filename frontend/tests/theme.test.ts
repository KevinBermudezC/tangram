import { describe, expect, it } from "vitest";

import { cycleTheme, type TangramTheme } from "@/lib/theme";

describe("cycleTheme", () => {
  it("cycles light → dark → system → light", () => {
    const order: TangramTheme[] = ["light", "dark", "system"];
    expect(cycleTheme("light")).toBe("dark");
    expect(cycleTheme("dark")).toBe("system");
    expect(cycleTheme("system")).toBe("light");
    // Full loop
    let t: TangramTheme = "light";
    for (let i = 0; i < 3; i++) t = cycleTheme(t);
    expect(t).toBe("light");
    expect(order).toContain("system");
  });

  it("treats undefined as system (first visit / unresolved)", () => {
    expect(cycleTheme(undefined)).toBe("light");
  });
});
