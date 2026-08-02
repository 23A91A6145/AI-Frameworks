"use client";

import { useCallback, useEffect, useState } from "react";
import { Copy, KeyRound, Pause, Play } from "lucide-react";

import { apiFetch, type WidgetConfig } from "@/lib/api";
import { useSession } from "@/lib/session";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

export function WidgetSettings() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [config, setConfig] = useState<WidgetConfig | null>(null);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!activeWorkspace) return;
    setConfig(await apiFetch<WidgetConfig>(`/api/v1/workspaces/${activeWorkspace.slug}/widget/config`));
  }, [activeWorkspace]);

  useEffect(() => {
    load().catch(() => {});
  }, [load]);

  const act = async (action: "enable" | "rotate" | "disable") => {
    if (!activeWorkspace) return;
    setBusy(true);
    try {
      const res = await apiFetch<{ enabled: boolean; token: string }>(
        `/api/v1/workspaces/${activeWorkspace.slug}/widget/${action}`,
        { method: "POST", body: "{}" },
      );
      toast({
        title: `Widget ${action === "disable" ? "disabled" : action === "rotate" ? "token rotated" : "enabled"}`,
        variant: "success",
      });
      setConfig({ ...(config ?? { widget_url: "" }), widget_enabled: res.enabled, widget_token: res.token });
    } catch (err) {
      toast({ title: "Widget update failed", description: String(err), variant: "error" });
    } finally {
      setBusy(false);
    }
  };

  const copy = async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(key);
      setTimeout(() => setCopied(null), 1500);
    } catch {
      toast({ title: "Copy failed", variant: "error" });
    }
  };

  const embed = config?.widget_token
    ? `<script src="http://localhost:3000/widget.js" data-widget-src="${config.widget_url}" data-base="http://localhost:8000" data-token="${config.widget_token}"></script>`
    : "";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2">
            <KeyRound className="h-5 w-5 text-primary" /> Public widget
          </CardTitle>
          {config && (
            <Badge variant={config.widget_enabled ? "success" : "secondary"}>
              {config.widget_enabled ? "Live" : "Disabled"}
            </Badge>
          )}
        </div>
        <CardDescription>
          Embed AI chat on your own site. Guests chat with your knowledge base via the public API
          using the widget token.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!config ? (
          <Skeleton className="h-20 w-full" />
        ) : (
          <>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" onClick={() => act("enable")} disabled={busy || config.widget_enabled}>
                {busy ? <Spinner /> : <Play className="h-4 w-4" />}
                Enable
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => act("rotate")}
                disabled={busy || !config.widget_token}
              >
                Rotate token
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => act("disable")}
                disabled={busy || !config.widget_enabled}
              >
                <Pause className="h-4 w-4" />
                Disable
              </Button>
            </div>

            {config.widget_token && (
              <>
                <div className="rounded-lg border p-3">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                      Widget token
                    </span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copy(config.widget_token!, "token")}
                    >
                      <Copy className="h-3.5 w-3.5" /> {copied === "token" ? "Copied" : "Copy"}
                    </Button>
                  </div>
                  <code className="block break-all rounded bg-muted/50 p-2 text-[11px] text-muted-foreground">
                    {config.widget_token}
                  </code>
                </div>

                <div className="rounded-lg border p-3">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                      Embed snippet
                    </span>
                    <Button size="sm" variant="ghost" onClick={() => copy(embed, "embed")}>
                      <Copy className="h-3.5 w-3.5" /> {copied === "embed" ? "Copied" : "Copy"}
                    </Button>
                  </div>
                  <pre className="overflow-x-auto rounded bg-muted/50 p-2 text-[11px] leading-relaxed text-muted-foreground">
                    {embed}
                  </pre>
                </div>
              </>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
