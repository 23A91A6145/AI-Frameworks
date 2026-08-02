"use client";

import { useState } from "react";

import { useSession } from "@/lib/session";
import { FullScreenLoader } from "@/components/ui/spinner";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { loading } = useSession();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (loading) return <FullScreenLoader />;

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar open={mobileOpen} onClose={() => setMobileOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenu={() => setMobileOpen(true)} />
        <main className="flex-1 px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}
