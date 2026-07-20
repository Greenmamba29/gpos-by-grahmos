import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { PageHeader, StatusBadge, RiskBadge, Loading, StageStepper, EvidenceChip, fmtMoney, fmtDay } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { Sparkles, ShieldCheck, AlertTriangle, GraduationCap, ScrollText, ArrowRight } from "lucide-react";
import { CaseLifecycle } from "@/components/CaseLifecycle";

export default function DecisionRoom() {
  const { caseId } = useParams();
  const nav = useNavigate();
  const [cases, setCases] = useState([]);
  const [active, setActive] = useState(caseId || "case_founderday");
  const [c, setC] = useState(null);
  const [dec, setDec] = useState(null);
  const [tl, setTl] = useState(null);
  const [reviewed, setReviewed] = useState(false);
  const [rationale, setRationale] = useState("");

  const load = async (id) => {
    setC(null);
    const [cc, tt] = await Promise.all([api.case(id), api.timeline(id)]);
    setC(cc); setTl(tt);
    try { setDec(await api.decision(id)); } catch { setDec(null); }
  };
  useEffect(() => { api.cases().then(setCases); }, []);
  useEffect(() => { load(active); setReviewed(false); setRationale(""); }, [active]);

  const authorize = async () => {
    if (!rationale.trim()) { toast.error("A decision rationale is required."); return; }
    nav("/approvals");
    toast.success("Recommendation accepted — routed to Approval Center for SoD-checked gates.");
  };

  if (!c) return <Loading />;

  return (
    <div className="mx-auto max-w-[1280px]">
      <PageHeader title="Decision Room" subtitle="Coordinate a single case — recommendation and authorized decision are kept separate.">
        <Select value={active} onValueChange={setActive}>
          <SelectTrigger className="h-9 w-[280px] text-xs" data-testid="decision-case-select"><SelectValue /></SelectTrigger>
          <SelectContent>{cases.map((x) => <SelectItem key={x.id} value={x.id} className="text-xs">{x.title}</SelectItem>)}</SelectContent>
        </Select>
      </PageHeader>

      <Card className="mb-5 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div><div className="text-base font-semibold text-slate-900">{c.title}</div>
            <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground"><StatusBadge status={c.state} /><RiskBadge risk={c.risk} /><span>Needed by {fmtDay(c.needed_by)}</span></div></div>
          <div className="text-right"><div className="font-mono text-lg font-semibold tabular-nums text-slate-900">{fmtMoney(c.amount)}</div><div className="text-[11px] text-muted-foreground">Channel: {c.channel}</div></div>
        </div>
        <Separator className="my-3" />
        <StageStepper stages={tl.stages} current={c.state} stageMeta={tl.stage_meta} />
      </Card>

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Request summary */}
        <Card className="p-4">
          <div className="text-sm font-semibold text-slate-900">Request Summary</div>
          <p className="mt-2 rounded-lg bg-slate-50 p-3 text-xs italic leading-5 text-slate-600">“{c.request?.raw}”</p>
          <dl className="mt-3 space-y-2 text-xs">
            <div className="flex justify-between"><dt className="text-muted-foreground">Requester</dt><dd className="font-medium text-slate-800">{c.requester?.name}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Owner</dt><dd className="font-medium text-slate-800">{c.owner?.name}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Budget</dt><dd className="font-mono text-slate-800">{fmtMoney(c.request?.normalized?.budget_amount)}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Location</dt><dd className="text-slate-800">{c.request?.normalized?.location || "—"}</dd></div>
          </dl>
          {c.request?.missing_fields?.length > 0 && (
            <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-2.5">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-amber-900"><AlertTriangle className="h-3.5 w-3.5" /> Missing material facts</div>
              <ul className="mt-1 list-inside list-disc text-[11px] text-amber-800">{c.request.missing_fields.map((m) => <li key={m}>{m.replace(/_/g," ")}</li>)}</ul>
            </div>
          )}
        </Card>

        {/* Agent recommendation (TEAL) */}
        <Card className="overflow-hidden" data-testid="recommendation-panel">
          <div className="flex items-center justify-between border-b border-border bg-[hsl(173_84%_95%)] px-4 py-2.5">
            <div className="flex items-center gap-2 text-sm font-semibold text-[hsl(var(--g-teal-700))]"><Sparkles className="h-4 w-4" /> Recommendation</div>
            <span className="rounded-full border border-[hsl(173_60%_80%)] bg-white px-2 py-0.5 text-[10px] font-medium text-[hsl(var(--g-teal-700))]">Prepared by Grahmos Assist</span>
          </div>
          <div className="p-4">
            {dec ? (<>
              <div className="text-sm font-semibold text-slate-900">{dec.recommended_supplier?.name}</div>
              <p className="mt-1.5 text-xs leading-5 text-slate-600">{dec.rationale}</p>
              <div className="mt-3 space-y-1.5">
                {dec.options?.map((o) => (
                  <div key={o.supplier_id} className={cn("flex items-center justify-between rounded-md px-2.5 py-1.5 text-xs", o.supplier_id === dec.recommendation ? "bg-[hsl(173_84%_97%)] ring-1 ring-[hsl(173_60%_82%)]" : "bg-slate-50")}>
                    <span className="text-slate-700">{o.supplier?.name}</span>
                    <span className="font-mono font-semibold tabular-nums text-slate-900">{o.weighted}</span>
                  </div>
                ))}
              </div>
              {dec.vs_last_year && <div className="mt-3 text-[11px] text-slate-500">vs last year: {dec.vs_last_year.cost_delta_pct}% cost, +{dec.vs_last_year.attendees_delta} attendees</div>}
              <div className="mt-3 flex flex-wrap gap-1.5">
                <EvidenceChip label="Prepared by Grahmos Assist" kind="assist" />
                <EvidenceChip label="Evidence from Accio" kind="accio" />
              </div>
              {dec.unknowns?.length > 0 && (
                <div className="mt-3 rounded-lg border border-[hsl(270_60%_88%)] bg-[hsl(270_74%_97%)] p-2.5">
                  <div className="text-[11px] font-semibold text-[hsl(var(--g-purple-700))]">Unknowns / Review</div>
                  <ul className="mt-1 list-inside list-disc text-[11px] text-[hsl(var(--g-purple-700))]">{dec.unknowns.map((u,i) => <li key={i}>{u}</li>)}</ul>
                </div>
              )}
              {dec.dissent?.length > 0 && (
                <div className="mt-2 text-[11px] text-slate-500">Dissent: {dec.dissent.map((d) => `${d.who} — ${d.why}`).join("; ")}</div>
              )}
            </>) : <div className="text-xs text-muted-foreground">Sourcing not yet complete for this case. Grahmos will prepare a comparison at Review Ready.</div>}
          </div>
        </Card>

        {/* Authorized decision (NAVY) */}
        <Card className="overflow-hidden" data-testid="authorization-panel">
          <div className="flex items-center justify-between border-b border-border bg-[hsl(var(--g-navy-950))] px-4 py-2.5">
            <div className="flex items-center gap-2 text-sm font-semibold text-white"><ShieldCheck className="h-4 w-4" /> Authorized Decision</div>
            <span className="rounded-full bg-white/15 px-2 py-0.5 text-[10px] font-medium text-white">Human accountability</span>
          </div>
          <div className="p-4">
            <p className="text-xs text-slate-600">A recommendation does not authorize spend. Review the evidence, then record an accountable decision. Approvals are enforced with separation-of-duties in the Approval Center.</p>
            <label className="mt-3 flex items-start gap-2 text-xs text-slate-700">
              <input type="checkbox" checked={reviewed} onChange={(e) => setReviewed(e.target.checked)} data-testid="evidence-reviewed-check" className="mt-0.5" />
              I have reviewed the evidence, unknowns, and dissent.
            </label>
            <Textarea value={rationale} onChange={(e) => setRationale(e.target.value)} data-testid="decision-rationale"
              placeholder="Decision rationale (required)…" className="mt-3 h-24 text-xs" />
            <Button disabled={!reviewed} onClick={authorize} data-testid="authorize-button"
              className="mt-3 w-full bg-[hsl(var(--g-navy-950))] hover:bg-[hsl(var(--g-navy-900))]">
              Accept recommendation & route for approval <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </Button>
            <p className="mt-2 text-center text-[10px] text-muted-foreground">SoD gates: Facilities → Finance → Procurement</p>
          </div>
        </Card>
      </div>

      {/* Case lifecycle: meeting, contract, order & logistics, buy/make/repair, override */}
      <CaseLifecycle caseObj={c} onChange={() => load(active)} />

      {/* Audit timeline */}
      <div className="mt-5">
        <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-900"><ScrollText className="h-4 w-4" /> Audit Trail · Evidence Lineage</div>
        <Card className="p-2">
          <div className="max-h-72 space-y-1 overflow-y-auto thin-scroll">
            {tl.events.slice().reverse().map((e) => (
              <div key={e.id} className="flex items-center gap-3 rounded-md px-3 py-2 text-xs hover:bg-slate-50">
                <span className="font-mono text-[10px] text-slate-400">#{e.seq}</span>
                <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-[hsl(var(--g-navy-900))]">{e.type}</span>
                <span className="text-slate-600">{e.detail?.note || e.detail?.reason || ""}</span>
                <span className="ml-auto text-[10px] text-slate-400">{e.actor} · {fmtDay(e.ts)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
