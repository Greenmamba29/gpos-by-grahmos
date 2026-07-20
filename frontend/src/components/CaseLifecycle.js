import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { EvidenceChip, fmtMoney } from "@/components/shared";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import {
  CalendarClock, FileSignature, PackageCheck, Truck, Boxes, ShieldOff,
  Check, Send, Wrench, Hammer, ShoppingCart,
} from "lucide-react";

const CLAUSE_STYLE = {
  acceptable: "bg-emerald-50 text-emerald-800 border-emerald-200",
  deviation: "bg-amber-50 text-amber-900 border-amber-200",
  missing: "bg-red-50 text-red-900 border-red-200",
  legal_review: "bg-[hsl(270_74%_96%)] text-[hsl(var(--g-purple-700))] border-[hsl(270_60%_88%)]",
};

export function CaseLifecycle({ caseObj, onChange }) {
  const id = caseObj.id;
  const [meeting, setMeeting] = useState(null);
  const [contract, setContract] = useState(null);
  const [bmr, setBmr] = useState(null);
  const [checklist, setChecklist] = useState(false);
  const [ovr, setOvr] = useState({ reason: "", policy_id: "policy-v3#4.2", expiry: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.getMeeting(id).then(setMeeting);
    api.contract(id).then(setContract).catch(() => {});
    api.bmr(id).then(setBmr).catch(() => setBmr(null));
  }, [id]);

  const act = async (fn, msg) => {
    setBusy(true);
    try { await fn(); toast.success(msg); onChange?.(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Blocked"); }
    finally { setBusy(false); }
  };

  const state = caseObj.state;

  return (
    <div className="mt-5">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-900">
        <Boxes className="h-4 w-4" /> Case Lifecycle
      </div>
      <Card className="p-4">
        <Tabs defaultValue={bmr ? "bmr" : "meeting"}>
          <TabsList className="flex flex-wrap">
            {bmr && <TabsTrigger value="bmr" data-testid="lc-tab-bmr"><Wrench className="mr-1 h-3.5 w-3.5" />Buy / Make / Repair</TabsTrigger>}
            <TabsTrigger value="meeting" data-testid="lc-tab-meeting"><CalendarClock className="mr-1 h-3.5 w-3.5" />Meeting</TabsTrigger>
            <TabsTrigger value="contract" data-testid="lc-tab-contract"><FileSignature className="mr-1 h-3.5 w-3.5" />Contract</TabsTrigger>
            <TabsTrigger value="logistics" data-testid="lc-tab-logistics"><Truck className="mr-1 h-3.5 w-3.5" />Order & Logistics</TabsTrigger>
            <TabsTrigger value="override" data-testid="lc-tab-override"><ShieldOff className="mr-1 h-3.5 w-3.5" />Override</TabsTrigger>
          </TabsList>

          {/* Buy / Make / Repair */}
          {bmr && (
            <TabsContent value="bmr" className="mt-4">
              <div className="grid gap-3 sm:grid-cols-3">
                {[["buy", ShoppingCart, "Buy new"], ["repair", Wrench, "Repair"], ["microfactory", Hammer, "Microfactory (3D print)"]].map(([k, Icon, label]) => (
                  <div key={k} className={cn("rounded-lg border p-3", bmr[k].risk === "REVIEW_REQUIRED" ? "border-amber-300 bg-amber-50" : "border-border")}>
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-900"><Icon className="h-3.5 w-3.5" />{label}</div>
                    <div className="mt-2 font-mono text-lg font-semibold tabular-nums">{fmtMoney(bmr[k].cost)}</div>
                    <div className="text-[11px] text-muted-foreground">{bmr[k].time_days}d · risk {bmr[k].risk.toLowerCase().replace(/_/g," ")}</div>
                    {bmr[k].note && <div className="mt-1 text-[10px] text-amber-700">{bmr[k].note}</div>}
                  </div>
                ))}
              </div>
              <p className="mt-3 text-[11px] text-muted-foreground">Grahmos recommends <b>Repair</b> (best cost/time within low risk). Microfactory requires a safety/engineering review before selection.</p>
            </TabsContent>
          )}

          {/* Meeting */}
          <TabsContent value="meeting" className="mt-4">
            {!meeting || meeting.status === "NONE" ? (
              <div className="text-center">
                <p className="text-xs text-muted-foreground">No supplier clarification meeting yet.</p>
                <Button size="sm" className="mt-2" disabled={busy} data-testid="meeting-propose"
                  onClick={() => act(async () => setMeeting(await api.proposeMeeting(id)), "Grahmos proposed 3 windows")}>Propose windows</Button>
              </div>
            ) : (
              <div>
                <div className="text-xs text-slate-600">{meeting.agenda}</div>
                <div className="mt-3 space-y-2">
                  {meeting.windows.map((w) => (
                    <div key={w.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-xs">
                      <span className="text-slate-700">{w.label}</span>
                      {meeting.status === "SENT" ? (meeting.chosen_window === w.id && <span className="flex items-center gap-1 text-emerald-700"><Check className="h-3 w-3" />Sent</span>)
                        : <Button size="sm" variant="outline" disabled={busy} data-testid={`meeting-send-${w.id}`}
                            onClick={() => act(() => api.sendMeeting(id, w.id, true), "Invite sent after consent")}><Send className="mr-1 h-3 w-3" />Send (consent)</Button>}
                    </div>
                  ))}
                </div>
                <p className="mt-2 text-[10px] text-muted-foreground">Invites are only sent after explicit consent (send_authorized). {meeting.invite_id && `Provider id: ${meeting.invite_id}`}</p>
              </div>
            )}
          </TabsContent>

          {/* Contract */}
          <TabsContent value="contract" className="mt-4">
            {contract && (<>
              <div className="mb-2 flex items-center justify-between"><span className="text-xs text-muted-foreground">Clause matrix vs institutional playbook</span><EvidenceChip label="Prepared by Grahmos Assist" kind="assist" /></div>
              <div className="space-y-1.5">
                {contract.clauses.map((c, i) => (
                  <div key={i} className={cn("flex items-start justify-between gap-3 rounded-md border px-3 py-2 text-xs", CLAUSE_STYLE[c.status])}>
                    <div><div className="font-medium">{c.clause}</div>{c.note && <div className="mt-0.5 text-[11px] opacity-80">{c.note}</div>}</div>
                    <span className="shrink-0 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase">{c.status.replace(/_/g," ")}</span>
                  </div>
                ))}
              </div>
            </>)}
          </TabsContent>

          {/* Order & Logistics */}
          <TabsContent value="logistics" className="mt-4">
            <div className="space-y-3">
              <StepRow done={["ORDERED","IN_TRANSIT","RECEIVED","CLOSED"].includes(state)} label="Order handoff (mock ERP PO)"
                action={state === "APPROVED" && <Button size="sm" disabled={busy} data-testid="order-button" onClick={() => act(() => api.order(id), "Mock PO created; supplier confirmed (sandbox)")}>Create PO</Button>}
                extra={caseObj.po_ref && <span className="font-mono text-[11px] text-slate-500">{caseObj.po_ref}</span>} />
              <StepRow done={["IN_TRANSIT","RECEIVED","CLOSED"].includes(state)} label="In transit (carrier tracking)"
                action={state === "ORDERED" && <Button size="sm" disabled={busy} data-testid="ship-button" onClick={() => act(() => api.shipAdvance(id), "Logistics tracking active")}>Advance shipment</Button>} />
              <StepRow done={["RECEIVED","CLOSED"].includes(state)} label="Receiving (evidence-gated)"
                action={state === "IN_TRANSIT" && (
                  <div className="flex items-center gap-2">
                    <label className="flex items-center gap-1 text-[11px]"><Checkbox checked={checklist} onCheckedChange={setChecklist} data-testid="receive-checklist" /> checklist confirmed</label>
                    <Button size="sm" disabled={busy || !checklist} data-testid="receive-button" onClick={() => act(() => api.receive(id, true), "Delivery accepted with evidence")}>Receive</Button>
                  </div>)} />
              <StepRow done={state === "CLOSED"} label="Close + learn (update memory)"
                action={state === "RECEIVED" && <Button size="sm" disabled={busy} data-testid="close-button" onClick={() => act(() => api.closeCase(id), "Case closed \u2014 memory updated")}>Close case</Button>} />
            </div>
          </TabsContent>

          {/* Override */}
          <TabsContent value="override" className="mt-4">
            <div className="rounded-lg border border-red-200 bg-red-50 p-3">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-red-900"><ShieldOff className="h-3.5 w-3.5" /> Policy override</div>
              <p className="mt-1 text-[11px] text-red-700">Every override is recorded immutably and requires a reason, policy citation, and expiry.</p>
              <div className="mt-3 grid gap-2 sm:grid-cols-3">
                <Input placeholder="Reason" value={ovr.reason} onChange={(e) => setOvr({ ...ovr, reason: e.target.value })} data-testid="override-reason" className="text-xs" />
                <Input placeholder="Policy id" value={ovr.policy_id} onChange={(e) => setOvr({ ...ovr, policy_id: e.target.value })} className="text-xs" />
                <Input type="date" value={ovr.expiry} onChange={(e) => setOvr({ ...ovr, expiry: e.target.value })} data-testid="override-expiry" className="text-xs" />
              </div>
              <Button size="sm" variant="outline" className="mt-2 border-red-300 text-red-800" disabled={busy || !ovr.reason || !ovr.expiry} data-testid="override-button"
                onClick={() => act(() => api.override(id, ovr), "Override recorded (immutable audit event)")}>Record override</Button>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
}

function StepRow({ done, label, action, extra }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border px-3 py-2.5">
      <div className="flex items-center gap-2 text-xs">
        <span className={cn("grid h-5 w-5 place-items-center rounded-full text-white", done ? "bg-[hsl(var(--g-teal-600))]" : "bg-slate-300")}>
          {done ? <Check className="h-3 w-3" /> : <PackageCheck className="h-3 w-3" />}
        </span>
        <span className={cn("font-medium", done ? "text-slate-500 line-through" : "text-slate-800")}>{label}</span>
        {extra}
      </div>
      {action}
    </div>
  );
}
