import { useState, useEffect, useCallback } from "react";
import {
  LayoutGrid,
  KeyRound,
  BarChart3,
  Plus,
  Copy,
  Check,
  Trash2,
  RotateCw,
  ChevronRight,
  Users,
  LogOut,
  Loader2,
  AlertCircle,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  CartesianGrid,
} from "recharts";

// ============================================================================
// API CLIENT — matches your FastAPI backend exactly (app/auth, app/workspaces,
// app/api_keys, app/analytics routers). Change API_BASE to your deployed URL.
// ============================================================================

const API_BASE = "http://localhost:8000"; // e.g. https://devport-api-production.up.railway.app

function useApi() {
  const [accessToken, setAccessToken] = useState(() => localStorage_getSafe("dp_access_token"));
  const [refreshToken, setRefreshToken] = useState(() => localStorage_getSafe("dp_refresh_token"));

  // NOTE: DevPort artifacts can't use real localStorage — this is a safe in-memory
  // shim. When you paste this into your own project (outside the artifacts
  // environment), swap localStorage_getSafe/Set for real window.localStorage calls
  // so the session survives a page refresh.
  function localStorage_getSafe() {
    return null;
  }

  const setTokens = (access, refresh) => {
    setAccessToken(access);
    setRefreshToken(refresh);
  };

  const clearTokens = () => {
    setAccessToken(null);
    setRefreshToken(null);
  };

  const request = useCallback(
    async (path, options = {}) => {
      const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
      if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

      const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

      if (res.status === 401 && refreshToken && !options._retried) {
        // access token expired — try the refresh flow once
        const refreshRes = await fetch(`${API_BASE}/auth/refresh?refresh_token=${refreshToken}`, {
          method: "POST",
        });
        if (refreshRes.ok) {
          const data = await refreshRes.json();
          setTokens(data.access_token, data.refresh_token);
          return request(path, {
            ...options,
            headers: { ...headers, Authorization: `Bearer ${data.access_token}` },
            _retried: true,
          });
        }
        clearTokens();
        throw new Error("Session expired — please sign in again");
      }

      if (!res.ok) {
        let detail = `Request failed (${res.status})`;
        try {
          const body = await res.json();
          detail = body.detail || detail;
        } catch (_) {}
        throw new Error(detail);
      }

      if (res.status === 204) return null;
      return res.json();
    },
    [accessToken, refreshToken]
  );

  return { accessToken, setTokens, clearTokens, request, isAuthed: !!accessToken };
}

// ============================================================================
// Shared UI atoms
// ============================================================================

function Badge({ active }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${
        active ? "bg-emerald-500/10 text-emerald-400" : "bg-neutral-700/40 text-neutral-500"
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${active ? "bg-emerald-400" : "bg-neutral-600"}`} />
      {active ? "Active" : "Revoked"}
    </span>
  );
}

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-5">
      <div className="text-[13px] text-neutral-500 font-medium">{label}</div>
      <div className="mt-2 text-3xl font-semibold text-white font-mono tracking-tight">{value}</div>
      {sub && <div className="mt-1 text-xs text-neutral-500">{sub}</div>}
    </div>
  );
}

function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="bg-red-500/[0.06] border border-red-500/20 rounded-lg px-3.5 py-2.5 mb-4 flex items-start gap-2.5">
      <AlertCircle size={15} className="text-red-400 shrink-0 mt-0.5" />
      <span className="text-red-300 text-sm flex-1">{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-400/60 hover:text-red-400 text-xs">
          Dismiss
        </button>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 size={20} className="text-neutral-600 animate-spin" />
    </div>
  );
}

// ============================================================================
// Login / Register — POST /auth/login, POST /auth/register
// ============================================================================

function LoginScreen({ api, onAuthed }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submit = async () => {
    setError(null);
    setLoading(true);
    try {
      if (mode === "register") {
        // POST /auth/register expects { email, password } -> UserResponse
        await api.request("/auth/register", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
      }
      // POST /auth/login expects { email, password } -> Token { access_token, refresh_token, token_type }
      const data = await api.request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      api.setTokens(data.access_token, data.refresh_token);
      onAuthed();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0D10] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2.5 mb-8 justify-center">
          <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center">
            <span className="font-mono font-bold text-white text-sm">D</span>
          </div>
          <span className="text-white font-semibold text-lg tracking-tight">DevPort</span>
        </div>

        <div className="bg-[#111418] border border-white/[0.06] rounded-2xl p-7">
          <h1 className="text-white text-lg font-semibold mb-1">
            {mode === "login" ? "Sign in" : "Create account"}
          </h1>
          <p className="text-neutral-500 text-sm mb-5">
            {mode === "login" ? "Access your workspaces and API keys." : "Start managing your APIs."}
          </p>

          <ErrorBanner message={error} onDismiss={() => setError(null)} />

          <div className="space-y-3">
            <div>
              <label className="text-xs font-medium text-neutral-400 mb-1.5 block">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full bg-[#0B0D10] border border-white/[0.08] rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-neutral-400 mb-1.5 block">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••"
                onKeyDown={(e) => e.key === "Enter" && submit()}
                className="w-full bg-[#0B0D10] border border-white/[0.08] rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>
          </div>

          <button
            onClick={submit}
            disabled={loading || !email || !password}
            className="w-full mt-5 bg-blue-500 hover:bg-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-white text-sm font-medium py-2.5 rounded-lg flex items-center justify-center gap-2"
          >
            {loading && <Loader2 size={14} className="animate-spin" />}
            {mode === "login" ? "Sign in" : "Create account"}
          </button>

          <button
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError(null);
            }}
            className="w-full mt-3 text-neutral-500 hover:text-neutral-300 text-xs transition-colors"
          >
            {mode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
          </button>
        </div>

        <p className="text-center text-neutral-600 text-xs mt-6 font-mono">
          {API_BASE}/auth/login
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// Workspaces — GET/POST /workspaces/
// ============================================================================

function WorkspacesView({ api, onSelect, selectedId }) {
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNew, setShowNew] = useState(false);
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // GET /workspaces/ -> list[WorkspaceResponse] { id, name, owner_id, created_at }
      const data = await api.request("/workspaces/");
      setWorkspaces(data);
      if (data.length && !selectedId) onSelect(data[0].id);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    load();
  }, [load]);

  const createWorkspace = async () => {
    if (!name.trim()) return;
    setCreating(true);
    setError(null);
    try {
      // POST /workspaces/ expects { name } -> WorkspaceResponse
      const ws = await api.request("/workspaces/", {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      setWorkspaces([ws, ...workspaces]);
      setName("");
      setShowNew(false);
      onSelect(ws.id);
    } catch (e) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-white">Workspaces</h1>
          <p className="text-sm text-neutral-500 mt-1">Teams and companies using your APIs.</p>
        </div>
        <button
          onClick={() => setShowNew(!showNew)}
          className="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-400 transition-colors text-white text-sm font-medium px-3.5 py-2 rounded-lg"
        >
          <Plus size={15} /> New workspace
        </button>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {showNew && (
        <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-4 mb-5 flex items-center gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Workspace name"
            onKeyDown={(e) => e.key === "Enter" && createWorkspace()}
            className="flex-1 bg-[#0B0D10] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white placeholder-neutral-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
          <button
            onClick={createWorkspace}
            disabled={creating}
            className="bg-blue-500 hover:bg-blue-400 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          >
            {creating && <Loader2 size={13} className="animate-spin" />}
            Create
          </button>
        </div>
      )}

      {workspaces.length === 0 ? (
        <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-10 text-center">
          <p className="text-neutral-500 text-sm">No workspaces yet. Create one to get started.</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {workspaces.map((ws) => (
            <button
              key={ws.id}
              onClick={() => onSelect(ws.id)}
              className={`flex items-center justify-between text-left bg-[#111418] border rounded-xl p-4 transition-colors ${
                selectedId === ws.id
                  ? "border-blue-500/50 ring-1 ring-blue-500/20"
                  : "border-white/[0.06] hover:border-white/[0.12]"
              }`}
            >
              <div className="flex items-center gap-3.5">
                <div className="w-9 h-9 rounded-lg bg-white/[0.04] flex items-center justify-center">
                  <LayoutGrid size={16} className="text-neutral-400" />
                </div>
                <div>
                  <div className="text-white text-sm font-medium">{ws.name}</div>
                  <div className="text-neutral-500 text-xs mt-0.5">
                    Created {new Date(ws.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
              <ChevronRight size={16} className="text-neutral-600" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// API Keys — GET/POST /workspaces/{id}/api-keys/, POST .../revoke, .../rotate
// ============================================================================

function ApiKeysView({ api, workspaceId }) {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNew, setShowNew] = useState(false);
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);
  const [revealedKey, setRevealedKey] = useState(null);
  const [copied, setCopied] = useState(false);

  const load = useCallback(async () => {
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    try {
      // GET /workspaces/{id}/api-keys/ -> list[ApiKeyResponse]
      const data = await api.request(`/workspaces/${workspaceId}/api-keys/`);
      setKeys(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [api, workspaceId]);

  useEffect(() => {
    load();
  }, [load]);

  const createKey = async () => {
    if (!name.trim()) return;
    setCreating(true);
    setError(null);
    try {
      // POST /workspaces/{id}/api-keys/ expects { name } -> ApiKeyCreateResponse (includes raw_key ONCE)
      const created = await api.request(`/workspaces/${workspaceId}/api-keys/`, {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      setRevealedKey(created.raw_key);
      setName("");
      setShowNew(false);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  };

  const revokeKey = async (keyId) => {
    setError(null);
    try {
      // POST /workspaces/{id}/api-keys/{key_id}/revoke -> ApiKeyResponse
      await api.request(`/workspaces/${workspaceId}/api-keys/${keyId}/revoke`, { method: "POST" });
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const rotateKey = async (keyId) => {
    setError(null);
    try {
      // POST /workspaces/{id}/api-keys/{key_id}/rotate -> ApiKeyCreateResponse (new raw_key ONCE)
      const rotated = await api.request(`/workspaces/${workspaceId}/api-keys/${keyId}/rotate`, {
        method: "POST",
      });
      setRevealedKey(rotated.raw_key);
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const copyKey = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(revealedKey);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (!workspaceId) {
    return (
      <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-10 text-center">
        <p className="text-neutral-500 text-sm">Select a workspace first.</p>
      </div>
    );
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-white">API Keys</h1>
          <p className="text-sm text-neutral-500 mt-1">Credentials for machine-to-machine access.</p>
        </div>
        <button
          onClick={() => setShowNew(!showNew)}
          className="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-400 transition-colors text-white text-sm font-medium px-3.5 py-2 rounded-lg"
        >
          <Plus size={15} /> Generate key
        </button>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {revealedKey && (
        <div className="bg-amber-500/[0.06] border border-amber-500/20 rounded-xl p-4 mb-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-amber-400 text-xs font-semibold uppercase tracking-wide">
              Save this key now — it won't be shown again
            </span>
          </div>
          <div className="flex items-center gap-2 bg-[#0B0D10] rounded-lg px-3 py-2.5 border border-white/[0.06]">
            <code className="text-sm font-mono text-white flex-1 overflow-x-auto whitespace-nowrap">
              {revealedKey}
            </code>
            <button
              onClick={copyKey}
              className="text-neutral-400 hover:text-white transition-colors shrink-0"
            >
              {copied ? <Check size={15} className="text-emerald-400" /> : <Copy size={15} />}
            </button>
          </div>
          <button
            onClick={() => setRevealedKey(null)}
            className="text-neutral-500 hover:text-neutral-300 text-xs mt-2.5 transition-colors"
          >
            Dismiss
          </button>
        </div>
      )}

      {showNew && (
        <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-4 mb-5 flex items-center gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Key name (e.g. Production)"
            onKeyDown={(e) => e.key === "Enter" && createKey()}
            className="flex-1 bg-[#0B0D10] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-white placeholder-neutral-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
          <button
            onClick={createKey}
            disabled={creating}
            className="bg-blue-500 hover:bg-blue-400 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          >
            {creating && <Loader2 size={13} className="animate-spin" />}
            Generate
          </button>
        </div>
      )}

      {keys.length === 0 ? (
        <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-10 text-center">
          <p className="text-neutral-500 text-sm">No API keys yet for this workspace.</p>
        </div>
      ) : (
        <div className="bg-[#111418] border border-white/[0.06] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.06] text-neutral-500 text-xs">
                <th className="text-left font-medium px-4 py-3">Name</th>
                <th className="text-left font-medium px-4 py-3">Prefix</th>
                <th className="text-left font-medium px-4 py-3">Status</th>
                <th className="text-left font-medium px-4 py-3">Last used</th>
                <th className="text-right font-medium px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {keys.map((k) => (
                <tr key={k.id} className="border-b border-white/[0.04] last:border-0">
                  <td className="px-4 py-3 text-white font-medium">{k.name}</td>
                  <td className="px-4 py-3 font-mono text-neutral-400 text-xs">{k.key_prefix}…</td>
                  <td className="px-4 py-3">
                    <Badge active={k.is_active} />
                  </td>
                  <td className="px-4 py-3 text-neutral-500 text-xs">
                    {k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : "Never"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 justify-end">
                      {k.is_active && (
                        <>
                          <button
                            title="Rotate"
                            onClick={() => rotateKey(k.id)}
                            className="p-1.5 text-neutral-500 hover:text-blue-400 hover:bg-white/[0.04] rounded-md transition-colors"
                          >
                            <RotateCw size={14} />
                          </button>
                          <button
                            title="Revoke"
                            onClick={() => revokeKey(k.id)}
                            className="p-1.5 text-neutral-500 hover:text-red-400 hover:bg-white/[0.04] rounded-md transition-colors"
                          >
                            <Trash2 size={14} />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Analytics — GET /workspaces/{id}/analytics/
// ============================================================================

function AnalyticsView({ api, workspaceId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!workspaceId) return;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        // GET /workspaces/{id}/analytics/ -> WorkspaceAnalytics
        // { total_requests, avg_latency_ms, top_endpoints[], daily_usage[] }
        const result = await api.request(`/workspaces/${workspaceId}/analytics/`);
        setData(result);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [api, workspaceId]);

  if (!workspaceId) {
    return (
      <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-10 text-center">
        <p className="text-neutral-500 text-sm">Select a workspace first.</p>
      </div>
    );
  }

  if (loading) return <Spinner />;
  if (error) return <ErrorBanner message={error} />;
  if (!data) return null;

  // daily_usage comes back newest-first from the backend; reverse for a left-to-right chart
  const dailyChart = [...data.daily_usage].reverse().map((d) => ({
    date: new Date(d.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    requests: d.request_count,
  }));

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-white">Analytics</h1>
        <p className="text-sm text-neutral-500 mt-1">Usage for this workspace.</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="Total requests" value={data.total_requests.toLocaleString()} />
        <StatCard label="Avg latency" value={`${data.avg_latency_ms}ms`} sub="across all endpoints" />
        <StatCard label="Tracked endpoints" value={data.top_endpoints.length} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-5">
          <div className="text-sm font-medium text-white mb-4">Requests per day</div>
          {dailyChart.length === 0 ? (
            <p className="text-neutral-600 text-sm py-16 text-center">No usage data yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={dailyChart}>
                <CartesianGrid stroke="#ffffff08" vertical={false} />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#6b7280" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ background: "#0B0D10", border: "1px solid #ffffff14", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "#fff" }}
                />
                <Line type="monotone" dataKey="requests" stroke="#3B82F6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-[#111418] border border-white/[0.06] rounded-xl p-5">
          <div className="text-sm font-medium text-white mb-4">Top endpoints</div>
          {data.top_endpoints.length === 0 ? (
            <p className="text-neutral-600 text-sm py-16 text-center">No requests logged yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={data.top_endpoints.map((e) => ({ endpoint: e.endpoint, requests: e.request_count }))}
                layout="vertical"
                margin={{ left: 10 }}
              >
                <CartesianGrid stroke="#ffffff08" horizontal={false} />
                <XAxis type="number" stroke="#6b7280" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis
                  type="category"
                  dataKey="endpoint"
                  stroke="#6b7280"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  width={90}
                />
                <Tooltip
                  contentStyle={{ background: "#0B0D10", border: "1px solid #ffffff14", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "#fff" }}
                />
                <Bar dataKey="requests" fill="#3B82F6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// App shell
// ============================================================================

export default function DevPortDashboard() {
  const api = useApi();
  const [page, setPage] = useState("workspaces");
  const [selectedWs, setSelectedWs] = useState(null);
  const [workspaceName, setWorkspaceName] = useState("");

  // Keep the sidebar's workspace label in sync without an extra request —
  // WorkspacesView already fetched the list, so just track the selected name here.
  useEffect(() => {
    setWorkspaceName("");
  }, [selectedWs]);

  if (!api.isAuthed) {
    return <LoginScreen api={api} onAuthed={() => setPage("workspaces")} />;
  }

  const nav = [
    { id: "workspaces", label: "Workspaces", icon: LayoutGrid },
    { id: "keys", label: "API Keys", icon: KeyRound },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-[#0B0D10] flex font-sans">
      {/* Sidebar */}
      <aside className="w-60 border-r border-white/[0.06] flex flex-col shrink-0">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <div className="w-7 h-7 rounded-md bg-blue-500 flex items-center justify-center">
            <span className="font-mono font-bold text-white text-xs">D</span>
          </div>
          <span className="text-white font-semibold text-sm tracking-tight">DevPort</span>
        </div>

        <div className="px-3 mt-2 flex-1">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = page === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setPage(item.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium mb-0.5 transition-colors ${
                  active
                    ? "bg-blue-500/10 text-blue-400"
                    : "text-neutral-500 hover:text-neutral-300 hover:bg-white/[0.03]"
                }`}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </div>

        <div className="px-3 pb-4">
          {selectedWs && (
            <div className="px-3 py-2.5 rounded-lg bg-white/[0.02] mb-2">
              <div className="text-xs text-neutral-500">Workspace</div>
              <div className="text-sm text-white font-medium mt-0.5">#{selectedWs}</div>
            </div>
          )}
          <button
            onClick={() => api.clearTokens()}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-neutral-500 hover:text-neutral-300 hover:bg-white/[0.03] transition-colors"
          >
            <LogOut size={15} /> Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 max-w-5xl overflow-y-auto">
        {page === "workspaces" && (
          <WorkspacesView api={api} selectedId={selectedWs} onSelect={setSelectedWs} />
        )}
        {page === "keys" && <ApiKeysView api={api} workspaceId={selectedWs} />}
        {page === "analytics" && <AnalyticsView api={api} workspaceId={selectedWs} />}
      </main>
    </div>
  );
}
