"use client";

import { useCallback, useEffect, useState } from "react";
import { Send, Webhook } from "lucide-react";

import { apiFetch } from "@/lib/api";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

type WebhookConfig = {
  webhook_url: string;
  webhook_secret: string;
  webhook_events: string[];
};

const EVENT_LABELS: Record<string, string> = {
  "ticket.created": "Ticket created",
  "ticket.ai_handled": "AI handled",
  "flow.approved": "Flow approved",
};

export function WebhookSettings() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [config, setConfig] = useState<WebhookConfig | null>(null);
  const [url, setUrl] = useState("");
  const [secret, setSecret] = useState("");
  const [events, setEvents] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [testing, setTesting] = useState(false);

  const load = useCallback(async () => {
    if (!activeWorkspace) return;
    const cfg = await apiFetch<WebhookConfig>(
      `/api/v1/workspaces/${activeWorkspace.slug}/webhooks`,
    );
    setConfig(cfg);
    setUrl(cfg.webhook_url);
    setSecret(cfg.webhook_secret);
    setEvents(cfg.webhook_events);
  }, [activeWorkspace]);

  useEffect(() => {
    load().catch(() => {});
  }, [load]);

  const save = async () => {
    if (!activeWorkspace || !url.trim()) return;
    setBusy(true);
    try {
      await apiFetch(`/api/v1/workspaces/${activeWorkspace.slug}/webhooks`, {
        method: "POST",
        body: JSON.stringify({ url: url.trim(), secret: secret.trim(), events }),
      });
      toast({ title: "Webhook saved", variant: "success" });
      await load();
    } catch (error) {
      toast({
        title: "Could not save webhook",
        description: error instanceof Error ? error.message : undefined,
        variant: "error",
      });
    } finally {
      setBusy(false);
    }
  };

  const test = async () => {
    if (!activeWorkspace) return;
    setTesting(true);
    try {
      const res = await apiFetch<{ delivered: boolean; status?: number; error?: string }>(
        `/api/v1/workspaces/${activeWorkspace.slug}/webhooks/test`,
        { method: "POST", body: "{}" },
      );
      if (res.delivered) {
        toast({ title: `Ping delivered (HTTP ${res.status})`, variant: "success" });
      } else {
        toast({ title: "Ping failed", description: res.error, variant: "error" });
      }
    } catch (error) {
      toast({
        title: "Ping request failed",
        description: error instanceof Error ? error.message : undefined,
        variant: "error",
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2">
            <Webhook className="h-5 w-5 text-primary" /> Outbound webhooks
          </CardTitle>
          {config && (
            <Badge variant={config.webhook_url ? "success" : "secondary"}>
              {config.webhook_url ? "Configured" : "Not set"}
            </Badge>
          )}
        </div>
        <CardDescription>
          Notify your own systems (Slack, Zapier, CRM, a custom endpoint) when tickets are created
          or handled by the AI crew. Payloads are HMAC-signed with your secret.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!config ? (
          <Skeleton className="h-20 w-full" />
        ) : (
          <>
            <div>
              <Label htmlFor="wh-url">Webhook URL</Label>
              <Input
                id="wh-url"
                placeholder="https://your-app.example.com/hooks/tenantdesk"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="wh-secret">Signing secret (optional)</Label>
              <Input
                id="wh-secret"
                placeholder="random string — sent as X-Webhook-Signature"
                value={secret}
                onChange={(e) => setSecret(e.target.value)}
              />
            </div>
            <div>
              <span className="block text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Events
              </span>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {Object.entries(EVENT_LABELS).map(([key, label]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() =>
                      setEvents((prev) =>
                        prev.includes(key) ? prev.filter((e) => e !== key) : [...prev, key],
                      )
                    }
                    className={`rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors ${
                      events.includes(key)
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/70"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={save} disabled={busy || !url.trim()}>
                {busy ? <Spinner /> : <Send className="h-4 w-4" />}
                Save webhook
              </Button>
              <Button variant="outline" onClick={test} disabled={testing || !config.webhook_url}>
                {testing ? <Spinner /> : "Send test ping"}
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
