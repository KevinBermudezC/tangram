import {
  Database,
  Globe,
  HardDrive,
  Layers,
  Monitor,
  Server,
  ShieldCheck,
  Zap,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import type { NodeType } from "@/types/tangram";

const ICONS: Record<NodeType, LucideIcon> = {
  frontend: Monitor,
  backend: Server,
  database: Database,
  auth: ShieldCheck,
  storage: HardDrive,
  external_service: Globe,
  queue: Layers,
  cache: Zap,
};

interface NodeIconProps {
  type: NodeType;
  size?: number;
  className?: string;
}

export function NodeIcon({ type, size = 16, className }: NodeIconProps) {
  const Icon = ICONS[type];
  return <Icon size={size} className={className} strokeWidth={1.6} />;
}
