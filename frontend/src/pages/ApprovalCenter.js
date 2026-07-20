import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useApp } from "@/context/AppContext";
import { PageHeader, StatusBadge, Loading, EvidenceChip, fmtMoney, EmptyState } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { ShieldCheck, ShieldAlert, Clock, ArrowRight, Lock } from "lucide-react";

const GATE_ORDER = ["FACILITIES", "FINANCE", "PROCUREMENT"];

export default function ApprovalCenter() {
  const { me, refreshMe } = useApp();
  const [rows, setRows] = useState([]);
  const [sel, setSel] = useState(null);
  const [rationale, setRationale] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => setRows(await api.approvals({ case_id: "case_founderday" }));
  useEffect(() => { load(); }, [me]);

  const decide = async (decision) => {
    setBusy(true);
    try {
      const r = await api.decideApproval(sel.id, decision, rationale);
      toast.success(`${sel.gate} gate ${decision.toLowerCase()}${r.all_gates_cleared ? " — all gates cleared, case Approved" : ""}`);
      setSel(null); setRationale(""); await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Blocked by policy");
    } finally { setBusy(false); }
  };

  const slaStyle = (s) => s === "AT_RISK" ? "border-l-red-500" : s === "PENDING" ? "border-l-amber-400" : s === "APPROVED" ? "border-l-[hsl(var(--g-teal-600))]" : "border-l-slate-300";
  const isMine = sel && me && sel.approver_id === me.id;
  const sodConflict = sel && me && me.id === sel.case?.requester_id;

  return (
    <div className="mx-auto max-w-[1180px]">
      <PageHeader title="Approval Center" subtitle={`Personal approval queue · acting as ${me?.name} (${me?.title})`} />
      <div className="mb-3 flex items-center gap-3 text-[11px] text-muted-foreground">
        <span className="flex items-center gap-1"><span className="h-3 w-1 rounded bg-[hsl(var(--g-teal-600))]" /> On track</span>
        <span className="flex items-center gap-1"><span className="h-3 w-1 rounded bg-amber-400" /> Due soon</span>
        <span className="flex items-center gap-1"><span className="h-3 w-1 rounded bg-red-500" /> Overdue / at risk</span>
      </div>

      <Card className="overflow-hidden">
        <table className="w-full text-sm">
          <thead className="border-b border-border bg-slate-50 text-left text-[11px] uppercase tracking-wide text-slate-500">
            <tr><th className="px-4 py-2.5 font-medium">Gate</th><th className="px-3 py-2.5 font-medium">Case</th><th className="px-3 py-2.5 font-medium">Amount</th><th className="px-3 py-2.5 font-medium">Approver</th><th className="px-3 py-2.5 font-medium">Status</th><th className="px-3 py-2.5"></th></tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id} data-testid={`approval-row-${a.gate}`} className={cn("border-b border-l-2 border-border last:border-b-0 hover:bg-slate-50", slaStyle(a.status))}>
                <td className="px-4 py-3"><div className="font-medium text-slate-900">{a.gate}</div><div className="text-[11px] text-muted-foreground">Step {a.order} of 3</div></td>
                <td className="px-3 py-3 text-xs text-slate-700">{a.case?.title}</td>
                <td className="px-3 py-3 font-mono text-xs tabular-nums">{fmtMoney(a.case?.amount)}</td>
                <td className="px-3 py-3 text-xs">{a.approver?.name}<div className="text-[11px] text-muted-foreground">≤ {fmtMoney(a.approver?.authority_threshold)}</div></td>
                <td className="px-3 py-3"><StatusBadge status={a.status} /></td>
                <td className="px-3 py-3 text-right">
                  <Button size="sm" variant="outline" disabled={a.status === "BLOCKED"} onClick={() => { setSel(a); setRationale(""); }} data-testid={`review-${a.gate}`}>
                    {a.status === "BLOCKED" ? <><Lock className="mr-1 h-3 w-3" /> Locked</> : "Review"}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Sheet open={!!sel} onOpenChange={(o) => !o && setSel(null)}>
        <SheetContent className="w-full overflow-y-auto thin-scroll sm:max-w-[480px]">
          {sel && (<>
            <SheetHeader><SheetTitle className="flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-[hsl(var(--g-teal-600))]" /> {sel.gate} Approval</SheetTitle></SheetHeader>
            <div className="mt-4 space-y-4">
              <div className="rounded-lg bg-slate-50 p-3 text-xs">
                <div className="font-medium text-slate-900">{sel.case?.title}</div>
                <div className="mt-1 font-mono tabular-nums text-slate-700">{fmtMoney(sel.case?.amount)}</div>
              </div>

              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Policy Path</div>
                <div className="mt-2 flex items-center gap-1">
                  {GATE_ORDER.map((g, i) => (
                    <React.Fragment key={g}>
                      <span className={cn("rounded-md px-2 py-1 text-[10px] font-medium", g === sel.gate ? "bg-[hsl(var(--g-navy-950))] text-white" : "bg-slate-100 text-slate-500")}>{g}</span>
                      {i < 2 && <ArrowRight className="h-3 w-3 text-slate-300" />}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              <div className={cn("rounded-lg border p-3", sodConflict || !isMine ? "border-red-200 bg-red-50" : "border-emerald-200 bg-emerald-50")}>
                <div className={cn("flex items-center gap-1.5 text-[11px] font-semibold", sodConflict || !isMine ? "text-red-800" : "text-emerald-800")}>
                  {sodConflict || !isMine ? <ShieldAlert className="h-3.5 w-3.5" /> : <ShieldCheck className="h-3.5 w-3.5" />} Separation of Duties
                </div>
                <p className={cn("mt-1 text-[11px]", sodConflict || !isMine ? "text-red-700" : "text-emerald-700")}>
                  {sodConflict ? "You are the requester — you cannot self-approve above threshold."
                    : !isMine ? `This gate is assigned to ${sel.approver?.name}. Switch to that role in Demo Mode to approve.`
                    : "You are the assigned approver and within your authority threshold."}
                </p>
              </div>

              <div className="flex flex-wrap gap-1.5"><EvidenceChip label="Prepared by Grahmos Assist" kind="assist" /><EvidenceChip label="policy://policy-v3" kind="policy" /></div>

              <Textarea value={rationale} onChange={(e) => setRationale(e.target.value)} data-testid="approval-rationale" placeholder="Rationale / conditions…" className="h-20 text-xs" />
              <Separator />
              <div className="flex gap-2">
                <Button className="flex-1 bg-[hsl(var(--g-teal-600))] hover:bg-[hsl(var(--g-teal-700))]" disabled={busy} onClick={() => decide("APPROVED")} data-testid="approve-button">Approve</Button>
                <Button variant="outline" className="flex-1" disabled={busy} onClick={() => decide("REJECTED")} data-testid="reject-button">Reject</Button>
              </div>
            </div>
          </>)}
        </SheetContent>
      </Sheet>
    </div>
  );
}
