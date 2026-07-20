import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { PageHeader, StatusBadge, Loading, fmtMoney, fmtDate, EmptyState } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { Inbox, HelpCircle, Search, Timer, AlertTriangle, Truck, GraduationCap, WifiOff } from "lucide-react";

const VIEW_ICON = { my_queue: Inbox, needs_info: HelpCircle, sourcing: Search, approval_aging: Timer, exceptions: AlertTriangle, in_transit: Truck, student_tasks: GraduationCap, offline_conflicts: WifiOff };

export default function OperatorWorkspace() {
  const [views, setViews] = useState([]);
  const [active, setActive] = useState("my_queue");
  const [data, setData] = useState(null);
  const nav = useNavigate();

  useEffect(() => { api.operatorViews().then((r) => setViews(r.views)); }, []);
  useEffect(() => { setData(null); api.operatorView(active).then(setData); }, [active]);

  return (
    <div className="mx-auto max-w-[1280px]">
      <PageHeader title="Operator Workspace" subtitle="Airtable-style saved views · filter, inspect, and act with policy-gated controls." />
      <div className="grid gap-5 lg:grid-cols-[240px_1fr]">
        <div className="space-y-1">
          {views.map((v) => {
            const Icon = VIEW_ICON[v.key] || Inbox;
            return (
              <button key={v.key} onClick={() => setActive(v.key)} data-testid={`view-${v.key}`}
                className={cn("flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active === v.key ? "bg-[hsl(173_84%_95%)] text-[hsl(var(--g-navy-950))]" : "text-slate-600 hover:bg-slate-100")}>
                <Icon className="h-4 w-4" /> <span className="flex-1 text-left">{v.label}</span>
                <span className="rounded-full bg-slate-100 px-1.5 text-[10px] font-semibold text-slate-600">{v.count}</span>
              </button>
            );
          })}
        </div>
        <div>
          {!data ? <Loading /> : <ViewTable kind={data.kind} rows={data.rows} nav={nav} />}
        </div>
      </div>
    </div>
  );
}

function ViewTable({ kind, rows, nav }) {
  if (!rows?.length) return <EmptyState title="Nothing here" hint="Try another saved view, or inject a demo exception." />;
  if (kind === "cases") return (
    <Card className="overflow-hidden">
      <table className="w-full text-sm">
        <thead className="border-b border-border bg-slate-50 text-left text-[11px] uppercase tracking-wide text-slate-500"><tr><th className="px-4 py-2.5 font-medium">Case</th><th className="px-3 py-2.5 font-medium">Stage</th><th className="px-3 py-2.5 font-medium">Amount</th><th className="px-3 py-2.5 font-medium">SLA due</th></tr></thead>
        <tbody>{rows.map((c) => (
          <tr key={c.id} onClick={() => nav(`/decisions/${c.id}`)} className="cursor-pointer border-b border-border last:border-0 hover:bg-slate-50">
            <td className="px-4 py-3 font-medium text-slate-900">{c.title}</td>
            <td className="px-3 py-3"><StatusBadge status={c.state} /></td>
            <td className="px-3 py-3 font-mono text-xs tabular-nums">{fmtMoney(c.amount)}</td>
            <td className="px-3 py-3 text-xs text-slate-600">{fmtDate(c.sla_due)}</td>
          </tr>))}</tbody>
      </table>
    </Card>
  );
  if (kind === "exceptions") return (
    <div className="space-y-2">{rows.map((e) => (
      <Card key={e.id} className="border-l-2 border-l-amber-400 p-3.5">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-900"><AlertTriangle className="h-4 w-4 text-amber-600" />{e.label}</div>
        <p className="mt-1 text-xs text-slate-600">{e.detail}</p>
        <div className="mt-1 text-[11px] text-muted-foreground">{fmtDate(e.ts)}</div>
      </Card>))}</div>
  );
  if (kind === "tasks") return (
    <div className="space-y-2">{rows.map((t) => (
      <Card key={t.id} className="flex items-center justify-between p-3.5"><div><div className="text-sm font-medium text-slate-900">{t.title}</div><div className="text-[11px] text-muted-foreground">{t.competency} · ${t.pay_rate}/hr · {t.hours_logged}h logged</div></div><StatusBadge status={t.status} /></Card>))}</div>
  );
  if (kind === "offline") return (
    <div className="space-y-2">{rows.map((o) => (
      <Card key={o.id} className="p-3.5"><div className="flex items-center justify-between"><div className="font-mono text-xs text-slate-800">{o.action} · {o.payload}</div><StatusBadge status={o.status} /></div>
        <div className="mt-1 text-[11px] text-muted-foreground">idempotency: <span className="font-mono">{o.idempotency_key}</span> · policy {o.policy_version}</div>
        {["PENDING", "CONFLICT_STALE_POLICY"].includes(o.status) && (
          <div className="mt-2 flex gap-2">
            <Button size="sm" variant="outline" data-testid={`resolve-apply-${o.id}`}
              onClick={async () => { await api.resolveConflict(o.id, "refresh_and_apply"); toast.success("Refreshed policy & applied"); window.location.reload(); }}>Refresh & apply</Button>
            <Button size="sm" variant="outline" data-testid={`resolve-discard-${o.id}`}
              onClick={async () => { await api.resolveConflict(o.id, "discard"); toast.success("Discarded"); window.location.reload(); }}>Discard</Button>
          </div>)}
      </Card>))}</div>
  );
  return null;
}
