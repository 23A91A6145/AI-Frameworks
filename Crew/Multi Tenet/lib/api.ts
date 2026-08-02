const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type User = {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string | null;
  is_super_admin: boolean;
  created_at: string;
};

export type Membership = {
  organization_id: string;
  organization_name: string;
  organization_slug: string;
  role: string;
  status: string;
};

export type Workspace = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  plan: string;
  created_at: string;
  member_count: number;
  your_role: string;
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string | null;
  token_type: string;
  user: User;
  memberships: Membership[];
};

export type ForgotPasswordResult = {
  message: string;
  reset_link?: string;
};

export type ResetPasswordResult = {
  message: string;
};

export async function requestPasswordReset(email: string): Promise<ForgotPasswordResult> {
  return apiFetch<ForgotPasswordResult>("/api/v1/auth/forgot-password", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(token: string, password: string): Promise<ResetPasswordResult> {
  return apiFetch<ResetPasswordResult>("/api/v1/auth/reset-password", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ token, password }),
  });
}

export type Member = {
  user: User;
  role: string;
  status: string;
  joined_at: string;
};

export type Activity = {
  id: string;
  action: string;
  entity_type: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
  actor_name: string | null;
};

export type DailyCount = { date: string; count: number };

export type WorkspaceStats = {
  id: string;
  name: string;
  slug: string;
  plan: string;
  your_role: string;
  member_count: number;
  total_activity: number;
  activity_7d: DailyCount[];
};

// ── Volume 2 · Knowledge ──────────────────────────────────────────────

export type KnowledgeDocument = {
  id: string;
  filename: string;
  source_type: "upload" | "url" | "faq";
  file_type: string;
  source_url: string | null;
  size_bytes: number;
  status: "queued" | "processing" | "ready" | "failed";
  error: string | null;
  chunk_count: number;
  created_at: string;
  updated_at: string;
  tags: string[];
};

export type KnowledgeHit = {
  id: string;
  document_id: string;
  chunk_index: number;
  text: string;
  score: number;
  filename: string;
  source_type: string;
};

export type KnowledgeSearchResult = {
  query: string;
  hits: KnowledgeHit[];
};

export type TagOut = { name: string; count: number };

// ── Volume 2 · Tickets ────────────────────────────────────────────────

export type TicketMessage = {
  id: string;
  ticket_id: string;
  sender: "user" | "ai" | "system";
  sender_user_id: string | null;
  sender_name: string | null;
  content: string;
  meta_json: Record<string, unknown>;
  created_at: string;
};

export type Ticket = {
  id: string;
  subject: string;
  body: string;
  status: "new" | "open" | "pending" | "resolved" | "closed" | "escalated";
  priority: "low" | "medium" | "high" | "urgent";
  classification: string | null;
  ai_summary: string | null;
  created_by_id: string | null;
  created_by_name: string | null;
  assigned_agent_id: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
};

export type TicketDetail = Ticket & { messages: TicketMessage[] };

export type FlowRun = {
  id: string;
  flow_key: "ticket" | "escalation" | "feedback";
  status: "running" | "awaiting_approval" | "approved" | "rejected" | "completed" | "failed";
  current_step: string;
  input_data: Record<string, unknown>;
  checkpoint: Record<string, unknown>;
  output_data: Record<string, unknown>;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type TicketHandleResult = {
  ticket: TicketDetail;
  flow_run: FlowRun | null;
  draft: string;
  classification: string;
  priority: string;
  escalate: boolean;
  engine: string;
  sources: { text: string; score: number; filename: string }[];
  awaiting_approval: boolean;
};

// ── Volume 4 · Analytics ─────────────────────────────────────────────

export type KpiSummary = {
  requests_month: number;
  request_limit: number;
  request_percent: number;
  tokens_month: number;
  est_cost_month: number;
  tickets_open: number;
  tickets_created_7d: number;
  tickets_resolved_7d: number;
  resolution_rate_7d: number;
  knowledge_docs: number;
  knowledge_chunks: number;
  active_agents: number;
  plan: string;
};

export type UsageKind = { kind: string; calls: number; tokens: number };

export type UsageSeries = {
  daily_requests: DailyCount[];
  daily_tokens: DailyCount[];
  by_kind: UsageKind[];
  total_requests: number;
  total_tokens: number;
};

export type TicketMetrics = {
  daily_created: DailyCount[];
  by_status: { status: string; count: number }[];
  by_priority: { priority: string; count: number }[];
  by_classification: { classification: string; count: number }[];
  avg_resolution_hours: number;
  total: number;
};

export type KnowledgeGrowth = {
  daily_added: DailyCount[];
  daily_chunks: DailyCount[];
  by_source: { source: string; count: number }[];
};

export type AgentFlowMetric = {
  flow: string;
  total: number;
  completed: number;
  awaiting_approval: number;
  rejected: number;
  failed: number;
};

export type AgentPerformance = {
  flows: AgentFlowMetric[];
  engine_distribution: { engine: string; count: number }[];
  total_runs: number;
};

export type AnalyticsOverview = {
  summary: KpiSummary;
  usage: UsageSeries;
  tickets: TicketMetrics;
  knowledge: KnowledgeGrowth;
  agents: AgentPerformance;
};

// ── Volume 4 · Billing ───────────────────────────────────────────────

export type UsageItem = {
  key: string;
  label: string;
  used: number;
  limit: number;
  unit: string;
  note: string;
  unlimited: boolean;
  percent: number;
  remaining: number | string;
};

export type PlanInfo = {
  key: string;
  name: string;
  price_month: number;
  description: string;
  requests_per_month: number;
  knowledge_docs: number;
  seats: number;
  storage_mb: number;
  advanced_analytics: boolean;
};

export type BillingSummary = {
  plan: string;
  plan_details: Record<string, unknown>;
  period_start: string;
  period_end: string;
  items: UsageItem[];
  all_plans: PlanInfo[];
};

// ── Volume 4 · Jobs ──────────────────────────────────────────────────

export type Job = {
  id: string;
  job_type: string;
  status: string;
  label: string | null;
  current_step: string;
  total_steps: number;
  progress: number;
  input_data: Record<string, unknown>;
  checkpoint: Record<string, unknown>;
  result: Record<string, unknown>;
  error: string | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  finished_at: string | null;
};

// ── Volume 4 · Public widget ─────────────────────────────────────────

export type WidgetConfig = {
  widget_enabled: boolean;
  widget_token: string | null;
  widget_url: string;
};

// ── Volume 3 · MCP servers & tools ───────────────────────────────────

export type McpResource = {
  uri: string;
  name: string;
  mimeType: string;
  description: string;
};

export type McpServer = {
  id: string;
  name: string;
  description?: string | null;
  resources: McpResource[];
  tools: { name: string; description: string; parameters?: Record<string, unknown> }[];
};

export type McpCallResult = {
  success: boolean;
  result?: Record<string, unknown>;
  error?: string;
};

export type ToolDefinition = {
  name: string;
  description: string;
  category: string;
  parameters: Record<string, unknown>;
};

export type ToolResult = {
  success: boolean;
  result?: Record<string, unknown>;
  error?: string;
};

// ── Volume 5 · Platform admin ────────────────────────────────────────

export type AdminOverview = {
  users: number;
  workspaces: number;
  memberships: number;
  activities: number;
  plans: Record<string, { requests_per_month: number; knowledge_docs: number; seats: number }>;
};

export type AdminWorkspace = {
  id: string;
  name: string;
  slug: string;
  plan: string;
  created_at: string;
  member_count: number;
};

// ── Volume 2 · Agents ─────────────────────────────────────────────────

export type AgentConfig = {
  id: string;
  key: string;
  name: string;
  role_description: string | null;
  llm_model: string | null;
  enabled: boolean;
  config: Record<string, unknown>;
  updated_at: string;
};

export type EngineStatus = {
  engine: string;
  crewai_available: boolean;
  llm_configured: boolean;
  llm_provider: string;
  llm_model: string;
  llm_base_url: string;
  embeddings_provider: string;
  vector_store: string;
  notes: string;
};

const ACCESS_KEY = "td_access";
const REFRESH_KEY = "td_refresh";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

export function setTokens(access: string, refresh: string | null): void {
  window.localStorage.setItem(ACCESS_KEY, access);
  if (refresh) window.localStorage.setItem(REFRESH_KEY, refresh);
  else window.localStorage.removeItem(REFRESH_KEY);
}

export function clearTokens(): void {
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

async function refreshAccessToken(): Promise<boolean> {
  const refresh = typeof window !== "undefined" ? window.localStorage.getItem(REFRESH_KEY) : null;
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const body = await res.json();
    setTokens(body.access_token, body.refresh_token ?? null);
    return true;
  } catch {
    return false;
  }
}

function redirectToLogin(): void {
  clearTokens();
  if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
    window.location.href = "/login";
  }
}

function canRetryBody(body: unknown): boolean {
  // Strings, FormData and Blobs can be sent more than once; ReadableStreams cannot.
  return (
    body === undefined || body === null || typeof body === "string" || body instanceof FormData || body instanceof Blob
  );
}

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function formatDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (typeof item === "string" ? item : item?.msg ?? JSON.stringify(item)))
      .join("; ");
  }
  return "Request failed";
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { auth?: boolean } = {},
): Promise<T> {
  const { auth = true, headers, ...rest } = options;
  const requestHeaders: Record<string, string> = {
    ...(headers as Record<string, string> | undefined),
  };

  if (!requestHeaders["Content-Type"]) requestHeaders["Content-Type"] = "application/json";

  if (auth) {
    const token = getAccessToken();
    if (token) requestHeaders.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...rest, headers: requestHeaders });

  if (res.status === 204) return undefined as T;

  const contentType = res.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json") ? await res.json() : null;

  if (!res.ok) {
    if (res.status === 401 && auth) {
      // The access token may simply be expired — try the refresh token once
      // before bouncing the user to the login page.
      const refreshed = canRetryBody(rest.body) && (await refreshAccessToken());
      if (refreshed) {
        const token = getAccessToken();
        if (token) requestHeaders.Authorization = `Bearer ${token}`;
        const retry = await fetch(`${API_URL}${path}`, { ...rest, headers: requestHeaders });
        if (retry.status === 204) return undefined as T;
        const retryContent = retry.headers.get("content-type") ?? "";
        const retryBody = retryContent.includes("application/json") ? await retry.json() : null;
        if (!retry.ok) {
          redirectToLogin();
          throw new ApiError(
            retry.status,
            retryBody ? formatDetail(retryBody.detail) : "Request failed",
          );
        }
        return retryBody as T;
      }
      redirectToLogin();
    }
    throw new ApiError(res.status, body ? formatDetail(body.detail) : "Request failed");
  }

  return body as T;
}

// Multipart upload for knowledge documents (no JSON Content-Type).
export async function apiUpload<T>(
  path: string,
  formData: FormData,
  onProgress?: (percent: number) => void,
): Promise<T> {
  const token = getAccessToken();
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (res.status === 204) return undefined as T;

  const contentType = res.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json") ? await res.json() : null;

  if (!res.ok) {
    if (res.status === 401) {
      if (await refreshAccessToken()) {
        const token = getAccessToken();
        if (token) {
          const retry = await fetch(`${API_URL}${path}`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: formData,
          });
          if (retry.status === 204) return undefined as T;
          const retryContent = retry.headers.get("content-type") ?? "";
          const retryBody = retryContent.includes("application/json") ? await retry.json() : null;
          if (!retry.ok) {
            redirectToLogin();
            throw new ApiError(
              retry.status,
              retryBody ? formatDetail(retryBody.detail) : "Upload failed",
            );
          }
          return retryBody as T;
        }
      }
      redirectToLogin();
    }
    throw new ApiError(res.status, body ? formatDetail(body.detail) : "Upload failed");
  }

  if (onProgress) onProgress(100);
  return body as T;
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
