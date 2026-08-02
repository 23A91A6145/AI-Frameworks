"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";

import { apiFetch, setTokens, type AuthResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";

export function DemoButton({ className, size }: { className?: string; size?: "sm" | "lg" }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const open = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<AuthResponse>("/api/v1/auth/demo", {
        method: "POST",
        auth: false,
      });
      setTokens(data.access_token, data.refresh_token);
      router.push("/app/dashboard");
    } catch {
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button onClick={open} disabled={loading} size={size} className={className}>
      {loading ? <Spinner /> : <Sparkles className="h-4 w-4" />}
      {loading ? "Opening demo…" : "Open live demo"}
    </Button>
  );
}
