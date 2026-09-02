/** Minimal rail chip for inspect_* tool parts in the UI Message Stream. */

export function titleNodeType(type: string): string {
  return type
    .split("_")
    .map((part) => (part ? part[0].toUpperCase() + part.slice(1) : part))
    .join(" ");
}

interface ToolishPart {
  type: string;
  toolName?: string;
  state?: string;
  output?: unknown;
}

export function chipForToolPart(part: unknown): string | null {
  if (!part || typeof part !== "object" || !("type" in part)) {
    return null;
  }
  const toolPart = part as ToolishPart;
  const name =
    toolPart.type === "dynamic-tool"
      ? (toolPart.toolName ?? "")
      : toolPart.type.startsWith("tool-")
        ? toolPart.type.slice("tool-".length)
        : "";

  switch (name) {
    case "inspect_diagram":
      return toolPart.state === "output-available" ? "miró diagram" : "mirando diagram…";
    case "inspect_node": {
      const output = toolPart.output;
      if (
        output &&
        typeof output === "object" &&
        "label" in output &&
        typeof output.label === "string" &&
        output.label
      ) {
        const kind =
          "type" in output && typeof output.type === "string"
            ? titleNodeType(output.type)
            : "node";
        return `miró ${kind} · ${output.label}`;
      }
      return toolPart.state === "output-available" ? "miró nodo" : "mirando nodo…";
    }
    default:
      return null;
  }
}
