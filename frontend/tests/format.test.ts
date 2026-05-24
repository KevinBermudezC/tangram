import { describe, expect, it } from "vitest";

import { relativeTime } from "@/lib/format";

describe("relativeTime()", () => {
  const now = new Date("2026-05-23T12:00:00Z");

  it("returns 'just now' for very recent times", () => {
    expect(relativeTime("2026-05-23T11:59:58Z", now)).toBe("just now");
  });

  it("formats seconds, minutes, and hours", () => {
    expect(relativeTime("2026-05-23T11:59:30Z", now)).toBe("30s ago");
    expect(relativeTime("2026-05-23T11:45:00Z", now)).toBe("15m ago");
    expect(relativeTime("2026-05-23T09:00:00Z", now)).toBe("3h ago");
  });

  it("formats days and 'yesterday'", () => {
    expect(relativeTime("2026-05-22T12:00:00Z", now)).toBe("yesterday");
    expect(relativeTime("2026-05-20T12:00:00Z", now)).toBe("3 days ago");
  });

  it("returns 'unknown' for an invalid date", () => {
    expect(relativeTime("not-a-date", now)).toBe("unknown");
  });
});
