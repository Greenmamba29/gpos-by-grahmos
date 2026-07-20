import React, { useState } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, SheetDescription } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useApp } from "@/context/AppContext";
import { api } from "@/lib/api";
import { fmtDate } from "@/components/shared";
import { toast } from "sonner";
import { RotateCcw, SkipForward, ScrollText, AlertTriangle, ShieldCheck, Play } from "lucide-react";

const STAGES = ["DRAFT","NEEDS_INFO","TRIAGED","POLICY_PLANNED","SOURCING","REVIEW_READY","APPROVAL_PENDING","APPROVED","ORDERED","IN_TRANSIT","RECEIVED","CLOSED"];
const EXCEPTIONS = [
  { key: "missing_cert", label: "Missing supplier certification" },
  { key: "over_threshold", label: "Quote above approval threshold" },
  { key: "approver_unavailable", label: "Approver unavailable" },
  { key: "carrier_delay", label: "Carrier delay" },
  { key: "offline_pending", label: "Offline action pending sync" },
];

export function DemoDrawer({ onChanged }) {
  const { reset } = useApp();
  const [open, setOpen] = useState(false);
  const [stage, setStage] = useState("SOURCING");
  const [audit, setAudit] = useState(null);
  const [busy, setBusy] = useState(false);

  const doReset = async () => { setBusy(true); await reset(); setBusy(false); toast.success("Demo reset to seeded state"); onChanged?.(); };
  const doJump = async () => { setBusy(true); await api.jump("case_founderday", stage); setBusy(false); toast.success(`Founder Day jumped to ${stage.replace(/_/g," ")}`); onChanged?.(); };
  const showAudit = async () => { const a = await api.audit("case_founderday"); setAudit(a); };
  const trigger = async (k) => { await api.triggerException(k, "case_founderday"); toast.warning(`Exception injected: ${k.replace(/_/g," ")}`); onChanged?.(); };

  return (
    <Sheet open={open} onOpenChange={(o) => { setOpen(o); if (o) showAudit(); }}>
      <SheetTrigger asChild>
        <button data-testid="demo-drawer-open" className="flex items-center gap-2 rounded-lg bg-[hsl(var(--g-navy-950))] px-3 py-1.5 text-xs font-medium text-white hover:bg-[hsl(var(--g-navy-900))] transition-colors">
          <Play className="h-3.5 w-3.5" /> Demo Controls
        </button>
      </SheetTrigger>
      <SheetContent className="w-full overflow-y-auto thin-scroll sm:max-w-[460px]">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2"><Play className="h-4 w-4 text-[hsl(var(--g-teal-600))]" /> Golden Demo Controls</SheetTitle>
          <SheetDescription>Founder Day event procurement — deterministic, replayable demo.</SheetDescription>
        </SheetHeader>

        <div className="mt-5 space-y-5">
          <div className="rounded-lg border border-border p-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-900"><RotateCcw className="h-3.5 w-3.5" /> Reset Demo</div>
            <p className="mt-1 text-[11px] text-muted-foreground">Restore all seeded cases, approvals, and audit trail.</p>
            <Button size="sm" variant="outline" className="mt-2" disabled={busy} onClick={doReset} data-testid="demo-reset-button">Reset to seeded state</Button>
          </div>

          <div className="rounded-lg border border-border p-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-900"><SkipForward className="h-3.5 w-3.5" /> Jump to Stage</div>
            <div className="mt-2 flex gap-2">
              <Select value={stage} onValueChange={setStage}>
                <SelectTrigger className="h-9 text-xs" data-testid="demo-jump-select"><SelectValue /></SelectTrigger>
                <SelectContent>{STAGES.map((s) => <SelectItem key={s} value={s} className="text-xs">{s.replace(/_/g," ")}</SelectItem>)}</SelectContent>
              </Select>
              <Button size="sm" disabled={busy} onClick={doJump} data-testid="demo-jump-button">Jump</Button>
            </div>
          </div>

          <div className="rounded-lg border border-border p-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-900"><AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> Inject Controlled Exception</div>
            <div className="mt-2 grid gap-1.5">
              {EXCEPTIONS.map((e) => (
                <button key={e.key} onClick={() => trigger(e.key)} data-testid={`demo-exc-${e.key}`}
                  className="rounded-md border border-border px-2.5 py-1.5 text-left text-[11px] text-slate-700 hover:bg-amber-50 hover:border-amber-200 transition-colors">{e.label}</button>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-900"><ScrollText className="h-3.5 w-3.5" /> Audit Trail</div>
              {audit && <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${audit.chain_valid ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-800"}`}><ShieldCheck className="h-3 w-3" /> {audit.chain_valid ? "Chain verified" : "Tampered"}</span>}
            </div>
            <div className="mt-2 max-h-64 space-y-1.5 overflow-y-auto thin-scroll" data-testid="demo-audit-list">
              {audit?.events?.slice().reverse().map((e) => (
                <div key={e.id} className="rounded-md bg-slate-50 px-2 py-1.5 text-[10px]">
                  <div className="flex items-center justify-between"><span className="font-mono font-medium text-[hsl(var(--g-navy-900))]">{e.type}</span><span className="font-mono text-slate-400">#{e.seq}</span></div>
                  <div className="text-slate-500">{e.actor} · {fmtDate(e.ts)}</div>
                </div>
              ))}
              {!audit?.events?.length && <div className="text-[11px] text-muted-foreground">No events yet.</div>}
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
