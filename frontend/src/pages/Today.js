import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useApp } from "@/context/AppContext";
import { KpiTile, PageHeader, SectionTitle, StatusBadge, RiskBadge, Loading, fmtMoney, fmtDay, EvidenceChip } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { CheckCircle2, Clock, FolderKanban, GraduationCap, Sparkles, TrendingUp, Search, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

const FINDING_ICON = { sourcing: Search, decision: Sparkles, savings: TrendingUp };

export default function Today() {
  const { me } = useApp();
  const [data, setData] = useState(null);
  const nav = useNavigate();
  useEffect(() => { api.today().then(setData); }, [me]);
  if (!data) return <Loading />;
  const k = data.kpis;

  return (
    <div className="mx-auto max-w-[1280px]">
      <PageHeader title="Grahmos Today"
        subtitle={`Welcome back, ${data.actor?.name?.split(" ")[0]} — here's what needs your attention.`} />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <KpiTile testid="kpi-pending" label="Pending approvals" value={k.pending_approvals} icon={CheckCircle2} accent="teal" />
        <KpiTile testid="kpi-slas" label="At-risk SLAs" value={k.at_risk_slas} icon={Clock} accent="amber" />
        <KpiTile testid="kpi-active" label="Active procurements" value={k.active_cases} icon={FolderKanban} accent="navy" />
        <KpiTile testid="kpi-hours" label="Student hours (wk)" value={k.student_hours_week} icon={GraduationCap} accent="purple" />
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <SectionTitle>My Queue · Active Procurements</SectionTitle>
          <Card className="overflow-hidden">
            <table className="w-full text-sm">
              <thead className="border-b border-border bg-slate-50 text-left text-[11px] uppercase tracking-wide text-slate-500">
                <tr><th className="px-4 py-2.5 font-medium">Case</th><th className="px-3 py-2.5 font-medium">Stage</th><th className="px-3 py-2.5 font-medium">Amount</th><th className="px-3 py-2.5 font-medium">Needed by</th></tr>
              </thead>
              <tbody>
                {data.my_queue.map((c) => (
                  <tr key={c.id} onClick={() => nav(`/decisions/${c.id}`)} data-testid={`today-case-${c.id}`}
                    className="cursor-pointer border-b border-border last:border-0 hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900">{c.title}</div>
                      <div className="mt-0.5 flex items-center gap-2 text-[11px] text-muted-foreground"><RiskBadge risk={c.risk} /> {c.lane.replace(/_/g," ")}</div>
                    </td>
                    <td className="px-3 py-3"><StatusBadge status={c.state} /></td>
                    <td className="px-3 py-3 font-mono text-xs tabular-nums text-slate-700">{fmtMoney(c.amount)}</td>
                    <td className="px-3 py-3 text-xs text-slate-600">{fmtDay(c.needed_by)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <SectionTitle right={<span className="text-[11px] text-muted-foreground">Channel entry points</span>}><span className="mt-6 block">Notifications</span></SectionTitle>
          <Card className="divide-y divide-border">
            {data.notifications.map((n) => (
              <button key={n.id} onClick={() => nav(n.deeplink.screen === "supplier360" ? "/suppliers" : n.deeplink.screen === "approvals" ? "/approvals" : "/students")}
                className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-slate-50">
                <span className="grid h-8 w-8 place-items-center rounded-lg bg-slate-100 text-slate-500"><MessageSquare className="h-4 w-4" /></span>
                <div className="flex-1"><div className="text-sm text-slate-800">{n.text}</div>
                  <div className="text-[11px] text-muted-foreground">via {n.channel} · deep-links into Grahmos</div></div>
                {n.unread && <span className="h-2 w-2 rounded-full bg-[hsl(var(--g-teal-500))]" />}
              </button>
            ))}
          </Card>
        </div>

        <div>
          <SectionTitle>Agent Findings</SectionTitle>
          <div className="space-y-3">
            {data.agent_findings.map((f, i) => {
              const Icon = FINDING_ICON[f.kind] || Sparkles;
              return (
                <Card key={i} onClick={() => nav(f.kind === "sourcing" ? "/suppliers" : `/decisions/${f.case_id}`)}
                  className="cursor-pointer p-4 transition-transform hover:-translate-y-0.5" data-testid={`finding-${i}`}>
                  <div className="flex items-start gap-2.5">
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-[hsl(173_84%_95%)] text-[hsl(var(--g-teal-700))]"><Icon className="h-4 w-4" /></span>
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-slate-900">{f.title}</div>
                      <p className="mt-1 text-xs leading-5 text-slate-600">{f.detail}</p>
                      <div className="mt-2"><EvidenceChip label={f.evidence} kind={f.evidence.includes("Accio") ? "accio" : "assist"} /></div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          <SectionTitle><span className="mt-6 block">Student Assignments</span></SectionTitle>
          <div className="space-y-2">
            {data.student_assignments.map((t) => (
              <Card key={t.id} onClick={() => nav("/students")} className="cursor-pointer p-3 hover:bg-slate-50">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium text-slate-900">{t.title}</div>
                  <StatusBadge status={t.status} />
                </div>
                <div className="mt-1 text-[11px] text-muted-foreground">{t.competency} · ${t.pay_rate}/hr</div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
