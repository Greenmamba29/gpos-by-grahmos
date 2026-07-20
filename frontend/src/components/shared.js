import React from "react";
import { cn } from "@/lib/utils";
import { ShieldCheck, FileText, Sparkles, Link2 } from "lucide-react";

export const fmtMoney = (n, cur = "USD") =>
  n == null ? "—" : new Intl.NumberFormat("en-US", { style: "currency", currency: cur, maximumFractionDigits: 0 }).format(n);

export const fmtDate = (s) => {
  if (!s) return "—";
  try { return new Date(s).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }); }
  catch { return s; }
};
export const fmtDay = (s) => {
  if (!s) return "—";
  try { return new Date(s).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }); }
  catch { return s; }
};

const STATUS_STYLES = {
  DRAFT: "bg-slate-100 text-slate-700 border-slate-200",
  NEEDS_INFO: "bg-amber-50 text-amber-900 border-amber-200",
  TRIAGED: "bg-slate-100 text-slate-700 border-slate-200",
  POLICY_PLANNED: "bg-slate-100 text-slate-700 border-slate-200",
  SOURCING: "bg-[hsl(173_84%_95%)] text-[hsl(var(--g-teal-700))] border-[hsl(173_60%_85%)]",
  REVIEW_READY: "bg-[hsl(173_84%_95%)] text-[hsl(var(--g-teal-700))] border-[hsl(173_60%_85%)]",
  APPROVAL_PENDING: "bg-amber-50 text-amber-900 border-amber-200",
  APPROVED: "bg-emerald-50 text-emerald-900 border-emerald-200",
  ORDERED: "bg-indigo-50 text-indigo-900 border-indigo-200",
  IN_TRANSIT: "bg-indigo-50 text-indigo-900 border-indigo-200",
  RECEIVED: "bg-emerald-50 text-emerald-900 border-emerald-200",
  CLOSED: "bg-slate-100 text-slate-600 border-slate-200",
  PENDING: "bg-amber-50 text-amber-900 border-amber-200",
  BLOCKED: "bg-slate-100 text-slate-500 border-slate-200",
  AT_RISK: "bg-red-50 text-red-900 border-red-200",
  REJECTED: "bg-red-50 text-red-900 border-red-200",
};

export function StatusBadge({ status, className }) {
  const label = (status || "").replace(/_/g, " ");
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium capitalize",
      STATUS_STYLES[status] || "bg-slate-100 text-slate-700 border-slate-200", className)}>
      {label.toLowerCase()}
    </span>
  );
}

export function RiskBadge({ risk }) {
  const map = { LOW: "text-emerald-700 bg-emerald-50 border-emerald-200",
    MEDIUM: "text-amber-800 bg-amber-50 border-amber-200",
    HIGH: "text-red-800 bg-red-50 border-red-200" };
  return <span className={cn("inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide", map[risk] || map.MEDIUM)}>{risk}</span>;
}

const CHIP_ICON = { accio: Link2, assist: Sparkles, evidence: FileText, policy: ShieldCheck };
export function EvidenceChip({ label, kind = "evidence", onClick }) {
  const Icon = CHIP_ICON[kind] || FileText;
  return (
    <button onClick={onClick} data-testid="evidence-chip"
      className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px] text-slate-700 hover:bg-slate-50 transition-colors">
      <Icon className="h-3 w-3 text-[hsl(var(--g-teal-600))]" />
      <span className="font-mono">{label}</span>
    </button>
  );
}

export function KpiTile({ label, value, delta, icon: Icon, accent = "teal", testid }) {
  const accents = {
    teal: "text-[hsl(var(--g-teal-700))] bg-[hsl(173_84%_95%)]",
    navy: "text-[hsl(var(--g-navy-900))] bg-slate-100",
    purple: "text-[hsl(var(--g-purple-700))] bg-[hsl(270_74%_96%)]",
    amber: "text-amber-800 bg-amber-50",
  };
  return (
    <div data-testid={testid} className="group rounded-xl border border-border bg-card p-4 shadow-[var(--shadow-elev-1)] transition-transform hover:-translate-y-0.5">
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        {Icon && <span className={cn("grid h-7 w-7 place-items-center rounded-lg", accents[accent])}><Icon className="h-4 w-4" /></span>}
      </div>
      <div className="mt-2 text-2xl font-semibold tracking-[-0.02em] tabular-nums text-foreground">{value}</div>
      {delta != null && (
        <div className={cn("mt-1 text-[11px] font-medium", delta < 0 ? "text-emerald-600" : "text-slate-500")}>
          {delta > 0 ? "+" : ""}{delta}{typeof delta === "number" && Math.abs(delta) < 100 ? "" : ""} vs last period
        </div>
      )}
    </div>
  );
}

export function SectionTitle({ children, right }) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h2 className="text-sm font-semibold text-slate-900">{children}</h2>
      {right}
    </div>
  );
}

export function PageHeader({ title, subtitle, children }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold tracking-[-0.02em] text-foreground sm:text-[28px]">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

export function Loading({ label = "Loading…" }) {
  return (
    <div className="flex items-center gap-2 p-8 text-sm text-muted-foreground">
      <span className="h-3 w-3 animate-spin rounded-full border-2 border-slate-300 border-t-[hsl(var(--g-teal-600))]" />
      {label}
    </div>
  );
}

export function EmptyState({ title, hint, action }) {
  return (
    <div className="grid place-items-center rounded-xl border border-dashed border-border bg-card p-10 text-center">
      <div className="text-sm font-medium text-slate-800">{title}</div>
      {hint && <div className="mt-1 text-xs text-muted-foreground">{hint}</div>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}

// Case state-machine stepper
export function StageStepper({ stages, current, stageMeta, compact = false }) {
  const curIdx = stages.indexOf(current);
  return (
    <div className={cn("flex items-center gap-1 overflow-x-auto thin-scroll", compact ? "py-1" : "py-2")}>
      {stages.map((s, i) => {
        const done = i < curIdx, active = i === curIdx;
        return (
          <div key={s} className="flex items-center">
            <div className={cn("flex items-center gap-1.5 whitespace-nowrap rounded-md px-2 py-1 text-[11px] font-medium",
              active ? "bg-[hsl(var(--g-navy-950))] text-white" :
              done ? "text-[hsl(var(--g-teal-700))]" : "text-slate-400")}>
              <span className={cn("h-1.5 w-1.5 rounded-full", active ? "bg-[hsl(var(--g-teal-500))]" : done ? "bg-[hsl(var(--g-teal-600))]" : "bg-slate-300")} />
              {(stageMeta?.[s]?.label) || s}
            </div>
            {i < stages.length - 1 && <span className="mx-0.5 h-px w-3 bg-slate-200" />}
          </div>
        );
      })}
    </div>
  );
}
