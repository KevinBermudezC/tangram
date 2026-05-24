/**
 * Human-friendly relative time, e.g. "12s ago", "2h ago", "3 days ago".
 *
 * Library cards show when a diagram was last touched. We format on the client
 * from the backend's ISO `updatedAt` rather than storing a label, so it stays
 * correct as time passes.
 */
export function relativeTime(iso: string, now: Date = new Date()): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "unknown";

  const seconds = Math.round((now.getTime() - then) / 1000);
  if (seconds < 5) return "just now";
  if (seconds < 60) return `${seconds}s ago`;

  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.round(hours / 24);
  if (days === 1) return "yesterday";
  if (days < 7) return `${days} days ago`;
  if (days < 14) return "last week";

  const weeks = Math.round(days / 7);
  if (weeks < 5) return `${weeks} weeks ago`;

  return new Date(iso).toLocaleDateString();
}
