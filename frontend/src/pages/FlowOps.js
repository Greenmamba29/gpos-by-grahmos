import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, Loading, fmtDate } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Workflow, RefreshCw, CheckCircle2, Clock, Pause, CircleDot } from "lucide-react";

const STATUS = {
  OK: { c: "text-emerald-700 bg-emerald-50 border-emerald-200", i: CheckCircle2 },
  WAITING: { c: "text-amber-800 bg-amber-50 border-amber-200", i: Clock },
  IDLE: { c: "text-slate-500 bg-slate-50 border-slate-200", i: Pause },
};

export default function FlowOps() {
  const [flows, setFlows] = useState(null);
  const [busy, setBusy] = useState(null);
  const load = async () => setFlows(await api.flows());
  useEffect(() => { load(); }, []);
  if (!flows) return <Loading />;

  const replay = async (f) => {
    setBusy(f.id);
    const r = await api.replayFlow(f.id);
    await load(); setBusy(null);
    toast.success(`${f.name} replayed idempotently · ${r.runs} runs`);
  };

  return (
    <div className="mx-auto max-w-[1180px]">
      <PageHeader title="Flow Ops" subtitle="Grahmos Workflows — versioned, observable, replayable orchestration. Runs are idempotent and reference case IDs." />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {flows.map((f) => {
          const s = STATUS[f.status] || STATUS.IDLE;
          const Icon = s.i;
          return (
            <Card key={f.id} className="p-4" data-testid={`flow-${f.id}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-[hsl(214_45%_96%)] text-[hsl(var(--g-navy-800))]"><Workflow className="h-4 w-4" /></span>
                  <div><div className="font-mono text-[11px] text-slate-400">{f.id}</div><div className="text-sm font-semibold text-slate-900">{f.name}</div></div>
                </div>
                <span className={cn("inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium", s.c)}><Icon className="h-3 w-3" />{f.status}</span>
              </div>
              <div className="mt-3 flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Trigger: <span className="font-mono text-slate-600">{f.trigger}</span></span>
                <span>v{f.version}</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[11px] text-muted-foreground">
                <span className="flex items-center gap-1"><CircleDot className="h-3 w-3" />{f.runs} runs</span>
                <span>last {fmtDate(f.last_run)}</span>
              </div>
              <Button size="sm" variant="outline" className="mt-3 w-full" disabled={busy === f.id} onClick={() => replay(f)} data-testid={`replay-${f.id}`}>
                <RefreshCw className={cn("mr-1 h-3.5 w-3.5", busy === f.id && "animate-spin")} /> Replay (idempotent)
              </Button>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
