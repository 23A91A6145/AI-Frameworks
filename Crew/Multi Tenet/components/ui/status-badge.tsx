"use client";

import { Badge } from "@/components/ui/badge";

const STATUS_META: Record<string, { label: string; variant: "default" | "secondary" | "success" | "warning" | "destructive" | "outline" }> = {
  // knowledge documents
  ready: { label: "Ready", variant: "success" },
  processing: { label: "Processing", variant: "warning" },
  queued: { label: "Queued", variant: "secondary" },
  failed: { label: "Failed", variant: "destructive" },
  // tickets
  new: { label: "New", variant: "default" },
  open: { label: "Open", variant: "default" },
  pending: { label: "Pending", variant: "warning" },
  resolved: { label: "Resolved", variant: "success" },
  closed: { label: "Closed", variant: "secondary" },
  escalated: { label: "Escalated", variant: "destructive" },
  // ticket priority
  low: { label: "Low", variant: "secondary" },
  medium: { label: "Medium", variant: "default" },
  high: { label: "High", variant: "warning" },
  urgent: { label: "Urgent", variant: "destructive" },
  // flow runs
  running: { label: "Running", variant: "default" },
  awaiting_approval: { label: "Awaiting approval", variant: "warning" },
  approved: { label: "Approved", variant: "success" },
  rejected: { label: "Rejected", variant: "destructive" },
  completed: { label: "Completed", variant: "success" },
  // agents / engine
  enabled: { label: "Enabled", variant: "success" },
  disabled: { label: "Disabled", variant: "secondary" },
};

export function StatusBadge({
  status,
  className,
}: {
  status: string;
  className?: string;
}) {
  const meta = STATUS_META[status] ?? { label: status, variant: "secondary" as const };
  return (
    <Badge variant={meta.variant} className={className}>
      {meta.label}
    </Badge>
  );
}
