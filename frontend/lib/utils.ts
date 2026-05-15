import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Standard shadcn-style class merger. `clsx` handles conditional values;
 * `tailwind-merge` resolves Tailwind conflicts (so a later `px-3` wins over
 * an earlier `p-2`).
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
