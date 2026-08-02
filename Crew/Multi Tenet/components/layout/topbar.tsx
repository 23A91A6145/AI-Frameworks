"use client";

import Link from "next/link";
import { Bell, LogOut, Menu, Moon, Search, Settings, Sun, UserRound } from "lucide-react";

import { useSession } from "@/lib/session";
import { useTheme } from "@/components/theme";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Dropdown, DropdownItem } from "@/components/ui/dropdown";
import { WorkspaceSwitcher } from "@/components/layout/workspace-switcher";

export function Topbar({ onMenu }: { onMenu: () => void }) {
  const { user, logout, workspaces } = useSession();
  const { theme, toggle } = useTheme();

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur md:px-8">
      <button
        onClick={onMenu}
        className="cursor-pointer rounded-md p-2 text-muted-foreground hover:bg-muted lg:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>

      {workspaces.length > 0 && <WorkspaceSwitcher />}

      <div className="relative ml-auto hidden max-w-xs flex-1 md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          placeholder="Search…"
          className="h-9 w-full rounded-md border border-border bg-card pl-9 pr-3 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <div className="ml-auto flex items-center gap-1 md:ml-0">
        <button
          onClick={toggle}
          className="cursor-pointer rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>

        <button
          className="relative cursor-pointer rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-destructive" />
        </button>

        <Dropdown
          trigger={
            <button className="flex cursor-pointer items-center gap-2 rounded-full p-0.5 hover:ring-2 hover:ring-ring">
              <Avatar name={user?.full_name ?? "?"} />
            </button>
          }
        >
          <div className="border-b border-border px-3 py-2.5">
            <p className="truncate text-sm font-semibold">{user?.full_name}</p>
            <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
          </div>
          <div className="mt-1.5 space-y-0.5">
            <DropdownItem icon={<UserRound className="h-4 w-4" />}>
              <Link href="/app/settings" className="block w-full">
                Profile
              </Link>
            </DropdownItem>
            <DropdownItem icon={<Settings className="h-4 w-4" />}>
              <Link href="/app/settings" className="block w-full">
                Settings
              </Link>
            </DropdownItem>
            <div className="my-1 h-px bg-border" />
            <DropdownItem icon={<LogOut className="h-4 w-4" />} danger onClick={logout}>
              Log out
            </DropdownItem>
          </div>
        </Dropdown>
      </div>
    </header>
  );
}
