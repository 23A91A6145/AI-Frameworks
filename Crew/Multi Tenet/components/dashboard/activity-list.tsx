import {
  Building2,
  Settings,
  ShieldCheck,
  UserMinus,
  UserPlus,
  Users,
} from "lucide-react";

import { Activity } from "@/lib/api";
import { cn, timeAgo } from "@/lib/utils";
import { Avatar } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";

const ACTION_META: Record<string, { label: string; icon: React.ComponentType<{ className?: string }> }> = {
  "workspace.created": { label: "created this workspace", icon: Building2 },
  "workspace.updated": { label: "updated workspace settings", icon: Settings },
  "member.invited": { label: "invited a member", icon: UserPlus },
  "member.removed": { label: "removed a member", icon: UserMinus },
  "member.role_changed": { label: "changed a member's role", icon: ShieldCheck },
};

function activityText(item: Activity): string {
  const meta = ACTION_META[item.action];
  if (meta) return `${item.actor_name ?? "Someone"} ${meta.label}`;
  return item.action.replace(/[._]/g, " ");
}

export function ActivityList({ items, className }: { items: Activity[]; className?: string }) {
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-10 text-center">
        <Users className="h-8 w-8 text-muted-foreground/50" />
        <p className="text-sm text-muted-foreground">No activity yet.</p>
        <p className="text-xs text-muted-foreground/70">
          Invite a teammate or update your workspace to get started.
        </p>
      </div>
    );
  }

  return (
    <ul className={cn("space-y-1", className)}>
      {items.map((item) => {
        const meta = ACTION_META[item.action];
        const Icon = meta?.icon ?? Settings;
        return (
          <li key={item.id} className="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-muted/60">
            {item.actor_name ? (
              <Avatar name={item.actor_name} className="h-8 w-8 text-xs" />
            ) : (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                <Icon className="h-3.5 w-3.5 text-muted-foreground" />
              </div>
            )}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm">{activityText(item)}</p>
              {typeof item.metadata_json?.role === "string" && (
                <p className="truncate text-xs text-muted-foreground">
                  Role: {item.metadata_json.role}
                </p>
              )}
            </div>
            <span className="shrink-0 text-xs text-muted-foreground">{timeAgo(item.created_at)}</span>
          </li>
        );
      })}
    </ul>
  );
}

export function ActivityListSkeleton() {
  return (
    <div className="space-y-3">
      {[0, 1, 2, 3].map((i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <div className="flex-1 space-y-1.5">
            <Skeleton className="h-3.5 w-2/3" />
            <Skeleton className="h-3 w-1/3" />
          </div>
        </div>
      ))}
    </div>
  );
}
