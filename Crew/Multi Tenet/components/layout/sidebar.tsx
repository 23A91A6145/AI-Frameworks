"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BookOpen,
  Bot,
  Building2,
  CreditCard,
  Hammer,
  LayoutDashboard,
  Plug,
  Settings,
  ShieldCheck,
  Ticket,
  Users,
  Workflow,
  Wrench,
  X,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useSession } from "@/lib/session";

type NavItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
};

const workspaceItems: NavItem[] = [
  { href: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
];

const aiItems: NavItem[] = [
  { href: "/app/knowledge", label: "Knowledge", icon: BookOpen, badge: "Vol 2" },
  { href: "/app/agents", label: "Agents", icon: Bot, badge: "Vol 2" },
  { href: "/app/flows", label: "Flows", icon: Workflow, badge: "Vol 2" },
  { href: "/app/tools", label: "Tools", icon: Wrench, badge: "Vol 3" },
  { href: "/app/mcp", label: "MCP", icon: Plug, badge: "Vol 3" },
];

const supportItems: NavItem[] = [
  { href: "/app/tickets", label: "Tickets", icon: Ticket, badge: "Vol 2" },
];

const manageItems: NavItem[] = [
  { href: "/app/analytics", label: "Analytics", icon: BarChart3, badge: "Vol 4" },
  { href: "/app/jobs", label: "Jobs", icon: Hammer, badge: "Vol 4" },
  { href: "/app/users", label: "Users", icon: Users },
  { href: "/app/billing", label: "Billing", icon: CreditCard, badge: "Vol 4" },
  { href: "/app/settings", label: "Settings", icon: Settings },
];

const adminItems: NavItem[] = [
  { href: "/admin", label: "Admin Console", icon: ShieldCheck, badge: "Vol 5" },
];

function NavList({ items }: { items: NavItem[] }) {
  const pathname = usePathname();
  return (
    <nav className="flex flex-col gap-0.5">
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            <span className="flex-1">{item.label}</span>
            {item.badge && (
              <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                {item.badge}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}

function Brand() {
  return (
    <div className="flex items-center gap-2.5 px-2 py-1">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-sm">
        <Building2 className="h-4 w-4" />
      </div>
      <div className="leading-tight">
        <p className="text-sm font-semibold tracking-tight">TenantDesk</p>
        <p className="text-[10px] uppercase tracking-widest text-muted-foreground">AI Support</p>
      </div>
    </div>
  );
}

function SidebarContent() {
  const { user } = useSession();
  return (
    <div className="flex h-full flex-col gap-6 overflow-y-auto px-4 py-6">
      <Brand />
      <NavList items={workspaceItems} />
      <div>
        <p className="mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          AI Platform
        </p>
        <NavList items={aiItems} />
      </div>
      <NavList items={supportItems} />
      <div>
        <p className="mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Manage
        </p>
        <NavList items={manageItems} />
      </div>
      {user?.is_super_admin && (
        <div>
          <p className="mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Platform
          </p>
          <NavList items={adminItems} />
        </div>
      )}
    </div>
  );
}

export function Sidebar({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  return (
    <>
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 border-r border-border bg-card lg:block">
        <SidebarContent />
      </aside>

      {open && (
        <div className="fixed inset-0 z-[80] lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={onClose} />
          <aside className="absolute inset-y-0 left-0 flex w-64 flex-col bg-card shadow-xl">
            <div className="flex items-center justify-between px-4 pt-4">
              <Brand />
              <button
                onClick={onClose}
                className="cursor-pointer rounded-md p-1 text-muted-foreground hover:bg-muted"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <SidebarContent />
          </aside>
        </div>
      )}
    </>
  );
}
