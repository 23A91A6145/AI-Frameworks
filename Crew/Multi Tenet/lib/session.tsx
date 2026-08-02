"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import {
  apiFetch,
  clearTokens,
  getAccessToken,
  type User,
  type Workspace,
} from "@/lib/api";

type SessionValue = {
  user: User | null;
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  loading: boolean;
  setActiveWorkspace: (workspace: Workspace) => void;
  refresh: () => Promise<void>;
  createWorkspace: (name: string, slug?: string) => Promise<Workspace>;
  logout: () => void;
};

const SessionContext = createContext<SessionValue>({
  user: null,
  workspaces: [],
  activeWorkspace: null,
  loading: true,
  setActiveWorkspace: () => {},
  refresh: async () => {},
  createWorkspace: async () => {
    throw new Error("not ready");
  },
  logout: () => {},
});

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspaceState] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const [me, ws] = await Promise.all([
      apiFetch<User>("/api/v1/auth/me"),
      apiFetch<Workspace[]>("/api/v1/workspaces"),
    ]);
    setUser(me);
    setWorkspaces(ws);

    const stored = window.localStorage.getItem("td_active_ws");
    const match = ws.find((w) => w.slug === stored) ?? ws[0] ?? null;
    setActiveWorkspaceState(match);
    if (match) window.localStorage.setItem("td_active_ws", match.slug);
  }, []);

  useEffect(() => {
    if (!getAccessToken()) {
      router.replace("/login");
      return;
    }
    refresh()
      .catch(() => {
        clearTokens();
        router.replace("/login");
      })
      .finally(() => setLoading(false));
  }, [refresh, router]);

  const setActiveWorkspace = useCallback((workspace: Workspace) => {
    setActiveWorkspaceState(workspace);
    window.localStorage.setItem("td_active_ws", workspace.slug);
  }, []);

  const createWorkspace = useCallback(
    async (name: string, slug?: string) => {
      const workspace = await apiFetch<Workspace>("/api/v1/workspaces", {
        method: "POST",
        body: JSON.stringify({ name, slug: slug || undefined }),
      });
      await refresh();
      setActiveWorkspace(workspace);
      return workspace;
    },
    [refresh, setActiveWorkspace],
  );

  const logout = useCallback(() => {
    clearTokens();
    router.replace("/login");
  }, [router]);

  const value = useMemo(
    () => ({
      user,
      workspaces,
      activeWorkspace,
      loading,
      setActiveWorkspace,
      refresh,
      createWorkspace,
      logout,
    }),
    [user, workspaces, activeWorkspace, loading, setActiveWorkspace, refresh, createWorkspace, logout],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export const useSession = () => useContext(SessionContext);
