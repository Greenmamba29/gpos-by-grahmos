import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { PageHeader, RiskBadge, EvidenceChip } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Calendar, Monitor, Wrench, FlaskConical, ArrowRight, Sparkles, AlertTriangle, Copy, FileText, HelpCircle } from "lucide-react";

const LANE_ICON = { EVENT: Calendar, IT_SAAS: Monitor, FACILITIES: Wrench, CLASSROOM_LAB: FlaskConical };

export default function RequestHub() {
  const [lanes, setLanes] = useState([]);
  const [lane, setLane] = useState(null);
  const [form, setForm] = useState({ title: "", raw_text: "", budget_amount: "", needed_by: "", location: "", quantity: "" });
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();

  useEffect(() => { api.requestTemplates().then((r) => setLanes(r.lanes)); }, []);

  const buildBody = () => ({ lane: lane.key, title: form.title || form.raw_text.slice(0, 48),
    raw_text: form.raw_text, budget_amount: form.budget_amount ? Number(form.budget_amount) : null,
    needed_by: form.needed_by || null, location: form.location || null, quantity: form.quantity || null });

  const doPreview = async () => {
    if (!form.raw_text.trim()) { toast.error("Describe your need in plain language first."); return; }
    setBusy(true); setPreview(await api.requestPreview(buildBody())); setBusy(false);
  };
  const submit = async () => {
    setBusy(true);
    const r = await api.createRequest(buildBody());
    setBusy(false);
    toast.success(`Request created — case is ${r.case.state.replace(/_/g," ")}`);
    nav(`/decisions/${r.case.id}`);
  };

  return (
    <div className="mx-auto max-w-[1080px]">
      <PageHeader title="Request Hub" subtitle="Describe what you need in plain language — Grahmos turns it into a governed, evidence-backed case." />

      {!lane ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {lanes.map((l) => {
            const Icon = LANE_ICON[l.key] || Calendar;
            return (
              <Card key={l.key} onClick={() => setLane(l)} data-testid={`lane-${l.key}`}
                className="cursor-pointer p-5 transition-transform hover:-translate-y-0.5">
                <div className="flex items-center gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-[hsl(173_84%_95%)] text-[hsl(var(--g-teal-700))]"><Icon className="h-5 w-5" /></span>
                  <div><div className="text-sm font-semibold text-slate-900">{l.label}</div>
                    <div className="text-[11px] text-muted-foreground">{l.why}</div></div>
                </div>
              </Card>
            );
          })}
          <Card className="flex items-center gap-3 border-dashed p-5 text-muted-foreground">
            <HelpCircle className="h-5 w-5" /> <span className="text-xs">Not sure? Start with a description and Grahmos will help categorize.</span>
          </Card>
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[1fr_360px]">
          <Card className="p-5">
            <button onClick={() => { setLane(null); setPreview(null); }} className="text-[11px] text-[hsl(var(--g-teal-700))] hover:underline">← Change category</button>
            <div className="mt-2 flex items-center gap-2 text-sm font-semibold text-slate-900">{lane.label}</div>
            <div className="mt-4 space-y-3">
              <div>
                <label className="text-[11px] font-medium text-slate-600">Describe your need (plain language)</label>
                <Textarea data-testid="request-raw" value={form.raw_text} onChange={(e) => setForm({ ...form, raw_text: e.target.value })}
                  placeholder="e.g. We need AV, catering, and 150 chairs for Founder Day on Oct 10. Budget about $18k." className="mt-1 h-24 text-sm" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="text-[11px] font-medium text-slate-600">Short title</label>
                  <Input data-testid="request-title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1 text-sm" placeholder="Founder Day event" /></div>
                <div><label className="text-[11px] font-medium text-slate-600">Budget (USD)</label>
                  <Input data-testid="request-budget" type="number" value={form.budget_amount} onChange={(e) => setForm({ ...form, budget_amount: e.target.value })} className="mt-1 text-sm" placeholder="18000" /></div>
                <div><label className="text-[11px] font-medium text-slate-600">Needed by</label>
                  <Input data-testid="request-needed" type="date" value={form.needed_by} onChange={(e) => setForm({ ...form, needed_by: e.target.value })} className="mt-1 text-sm" /></div>
                {lane.key === "EVENT" && <div><label className="text-[11px] font-medium text-slate-600">Location</label>
                  <Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} className="mt-1 text-sm" placeholder="Blackburn Center" /></div>}
                <div><label className="text-[11px] font-medium text-slate-600">Quantity / item</label>
                  <Input value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} className="mt-1 text-sm" placeholder="150 chairs" /></div>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <div className="text-[11px] font-semibold text-slate-600">Decision-critical questions</div>
                <div className="mt-1 text-[11px] text-slate-500">{lane.questions.join(" · ")}</div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={doPreview} disabled={busy} data-testid="request-preview-button"><Sparkles className="mr-1 h-3.5 w-3.5" /> Ask Grahmos to normalize</Button>
                <Button onClick={submit} disabled={busy || !form.raw_text.trim()} data-testid="request-submit-button" className="bg-[hsl(var(--g-navy-950))] hover:bg-[hsl(var(--g-navy-900))]">Submit request <ArrowRight className="ml-1 h-3.5 w-3.5" /></Button>
              </div>
            </div>
          </Card>

          <Card className="h-fit p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900"><Sparkles className="h-4 w-4 text-[hsl(var(--g-teal-600))]" /> Request Preview</div>
            {!preview ? <p className="mt-2 text-xs text-muted-foreground">Grahmos will normalize your request and surface missing facts, duplicates, and existing contracts before you submit.</p> : (
              <div className="mt-3 space-y-3 text-xs">
                <div className="flex items-center justify-between"><span className="text-muted-foreground">Category</span><span className="font-medium">{preview.category.replace(/_/g," ")}</span></div>
                <div className="flex items-center justify-between"><span className="text-muted-foreground">Risk</span><RiskBadge risk={preview.risk} /></div>
                {preview.missing_fields.length > 0 && (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 p-2.5"><div className="flex items-center gap-1 text-[11px] font-semibold text-amber-900"><AlertTriangle className="h-3 w-3" /> Missing material facts</div>
                    <ul className="mt-1 list-inside list-disc text-[11px] text-amber-800">{preview.missing_fields.map((m) => <li key={m}>{m}</li>)}</ul>
                    <div className="mt-1 text-[10px] text-amber-700">Case will enter NEEDS_INFO — sourcing won’t start until resolved.</div></div>
                )}
                {preview.duplicate_suggestions.length > 0 && (
                  <div className="rounded-lg border border-slate-200 bg-white p-2.5"><div className="flex items-center gap-1 text-[11px] font-semibold text-slate-700"><Copy className="h-3 w-3" /> Possible duplicate demand</div>
                    <ul className="mt-1 text-[11px] text-slate-600">{preview.duplicate_suggestions.map((d) => <li key={d}>• {d}</li>)}</ul></div>
                )}
                {preview.existing_contracts.length > 0 && (
                  <div className="rounded-lg border border-[hsl(173_60%_82%)] bg-[hsl(173_84%_97%)] p-2.5"><div className="flex items-center gap-1 text-[11px] font-semibold text-[hsl(var(--g-teal-700))]"><FileText className="h-3 w-3" /> Existing contract available</div>
                    <ul className="mt-1 text-[11px] text-[hsl(var(--g-teal-700))]">{preview.existing_contracts.map((d) => <li key={d}>• {d}</li>)}</ul></div>
                )}
                <EvidenceChip label="Normalized by Grahmos Assist" kind="assist" />
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
