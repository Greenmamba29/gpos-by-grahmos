import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useApp } from "@/context/AppContext";
import { Wordmark } from "@/components/brand";
import { DemoModeSwitcher } from "@/components/DemoMode";
import { DemoDrawer } from "@/components/DemoDrawer";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
  LayoutDashboard, GitPullRequestArrow, Library, CheckCircle2, Building2,
  GraduationCap, Award, BarChart3, Table2, Wifi, WifiOff, Sparkles, Search,
  PlusCircle, Workflow,
} from "lucide-react";
import { Switch } from "@/components/ui/switch";

const NAV = [
  { to: "/", label: "Grahmos Today", icon: LayoutDashboard, group: "Home" },
  { to: "/request", label: "New Request", icon: PlusCircle, group: "Home" },
  { to: "/decisions", label: "Decision Room", icon: GitPullRequestArrow, group: "Coordinate" },
  { to: "/approvals", label: "Approval Center", icon: CheckCircle2, group: "Coordinate" },
  { to: "/suppliers", label: "Supplier 360", icon: Building2, group: "Coordinate" },
  { to: "/memory", label: "Campus Memory", icon: Library, group: "Coordinate" },
  { to: "/operator", label: "Operator Workspace", icon: Table2, group: "Coordinate" },
  { to: "/flows", label: "Flow Ops", icon: Workflow, group: "Coordinate" },
  { to: "/students", label: "Student Work Board", icon: GraduationCap, group: "Learn & Earn" },
  { to: "/passport", label: "Skills Passport", icon: Award, group: "Learn & Earn" },
  { to: "/impact", label: "Impact Command Center", icon: BarChart3, group: "Measure" },
];

function Rail() {
  const groups = [...new Set(NAV.map((n) => n.group))];
  return (
    <aside className="hidden w-[264px] shrink-0 flex-col border-r border-[hsl(var(--shell-rail-border))] bg-[hsl(var(--shell-rail))] lg:flex">
      <div className="flex h-16 items-center px-5"><Wordmark /></div>
      <nav className="flex-1 overflow-y-auto thin-scroll px-3 pb-6">
        {groups.map((g) => (
          <div key={g} className="mb-4">
            <div className="px-2 pb-1.5 pt-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">{g}</div>
            {NAV.filter((n) => n.group === g).map((n) => (
              <NavLink key={n.to} to={n.to} end={n.to === "/"} data-testid={`nav-${n.label.toLowerCase().replace(/[^a-z]+/g,"-")}`}
                className={({ isActive }) => cn(
                  "relative flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[13px] font-medium transition-colors",
                  isActive ? "bg-[hsl(173_84%_95%)] text-[hsl(var(--g-navy-950))] before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:rounded-r before:bg-[hsl(var(--g-teal-600))]"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900")}>
                <n.icon className="h-4 w-4" /> {n.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  );
}

function Header({ onChanged }) {
  const { institution, online, setOnline, agentMode, toggleAgentMode } = useApp();
  const loc = useLocation();

  const doSync = async () => {
    const r = await api.offlineSync();
    setOnline(true);
    toast.success(r.message + ` (${r.applied.length} applied, ${r.deduped.length} deduped, ${r.blocked.length} blocked)`);
    onChanged?.();
  };

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-3 border-b border-border bg-white px-4 sm:px-6">
      <div className="hidden items-center gap-2 md:flex">
        <span className="rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-700">
          {institution?.context_label || "Howard University · powered by Grahmos"}
        </span>
      </div>
      <div className="relative hidden flex-1 max-w-sm md:block">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
        <input placeholder="Search cases, suppliers, policies…" data-testid="global-search"
          className="h-9 w-full rounded-lg border border-border bg-slate-50 pl-8 pr-3 text-xs text-slate-700 outline-none focus:border-[hsl(var(--g-teal-600))] focus:ring-2 focus:ring-[hsl(173_84%_90%)]" />
      </div>
      <div className="ml-auto flex items-center gap-2.5">
        <div className="hidden items-center gap-2 rounded-lg border border-border px-2.5 py-1.5 sm:flex" title="Grahmos Assist reasoning mode">
          <Sparkles className={cn("h-3.5 w-3.5", agentMode === "live" ? "text-[hsl(var(--g-teal-600))]" : "text-slate-400")} />
          <span className="text-[11px] font-medium text-slate-600">Live AI</span>
          <Switch checked={agentMode === "live"} data-testid="agent-mode-toggle"
            onCheckedChange={(v) => { toggleAgentMode(v ? "live" : "seeded"); toast.info(v ? "Grahmos Assist: Live AI (Claude Sonnet 4.5)" : "Grahmos Assist: Seeded findings"); }} />
        </div>
        <button onClick={doSync} data-testid="online-toggle"
          className={cn("flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[11px] font-medium transition-colors",
            online ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-amber-300 bg-amber-50 text-amber-900 hover:bg-amber-100")}>
          {online ? <Wifi className="h-3.5 w-3.5" /> : <WifiOff className="h-3.5 w-3.5" />}
          {online ? "Online" : "Reconnect & Sync"}
        </button>
        <DemoModeSwitcher />
        <DemoDrawer onChanged={onChanged} />
      </div>
    </header>
  );
}

export function Shell({ children }) {
  const { loading } = useApp();
  const [tick, setTick] = React.useState(0);
  const onChanged = () => setTick((t) => t + 1);
  return (
    <div className="flex min-h-screen bg-background">
      <Rail />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onChanged={onChanged} />
        <main key={tick} className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          {loading ? null : children}
        </main>
      </div>
    </div>
  );
}
