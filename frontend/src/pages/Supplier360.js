import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, RiskBadge, Loading, EvidenceChip, fmtMoney } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { MapPin, Star, ShieldCheck, AlertTriangle, TrendingUp } from "lucide-react";

export default function Supplier360() {
  const [rows, setRows] = useState([]);
  const [sel, setSel] = useState(null);
  useEffect(() => { api.caseSuppliers("case_founderday").then(setRows); }, []);
  if (!rows.length) return <Loading />;

  const best = Math.min(...rows.map((r) => r.quote.total_usd));

  return (
    <div className="mx-auto max-w-[1280px]">
      <PageHeader title="Supplier 360" subtitle="Grahmos found 4 qualified suppliers · landed-cost normalized across quotes (incl. 1 EUR conversion)." />
      <Card className="overflow-x-auto thin-scroll">
        <table className="w-full min-w-[860px] text-sm">
          <thead className="border-b border-border bg-slate-50 text-left text-[11px] uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2.5 font-medium">Supplier</th>
              <th className="px-3 py-2.5 font-medium">Landed cost (USD)</th>
              <th className="px-3 py-2.5 font-medium">Lead time</th>
              <th className="px-3 py-2.5 font-medium">Validity</th>
              <th className="px-3 py-2.5 font-medium">Certifications</th>
              <th className="px-3 py-2.5 font-medium">Perf.</th>
              <th className="px-3 py-2.5 font-medium">Risk</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ supplier: s, quote: q }) => (
              <tr key={s.id} onClick={() => setSel({ s, q })} data-testid={`supplier-row-${s.id}`} className="cursor-pointer border-b border-border last:border-0 hover:bg-slate-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 font-medium text-slate-900">{s.name}</div>
                  <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                    <MapPin className="h-3 w-3" />{s.location}
                    {s.local && <Badge variant="outline" className="h-4 px-1 text-[9px]">Local</Badge>}
                    {s.diverse && <Badge variant="outline" className="h-4 border-[hsl(270_60%_82%)] px-1 text-[9px] text-[hsl(var(--g-purple-700))]">Diverse</Badge>}
                  </div>
                </td>
                <td className="px-3 py-3">
                  <span className={cn("font-mono text-xs font-semibold tabular-nums", q.total_usd === best ? "text-emerald-700" : "text-slate-800")}>{fmtMoney(q.total_usd)}</span>
                  {q.currency !== "USD" && <div className="text-[10px] text-slate-400">{q.total} {q.currency} @ {q.fx_rate} · {q.fx_source}</div>}
                </td>
                <td className="px-3 py-3 text-xs text-slate-700">{q.lead_time_days}d</td>
                <td className="px-3 py-3 text-xs text-slate-700">{q.validity_days}d</td>
                <td className="px-3 py-3">
                  {s.certifications.length ? s.certifications.map((c) => <Badge key={c} variant="outline" className="mr-1 h-5 px-1.5 text-[10px]"><ShieldCheck className="mr-0.5 h-2.5 w-2.5" />{c}</Badge>)
                    : <span className="text-[11px] text-red-600">none verified</span>}
                  {s.unknowns?.length > 0 && <div className="mt-0.5 flex items-center gap-1 text-[10px] text-amber-700"><AlertTriangle className="h-2.5 w-2.5" />{s.unknowns.join(", ")}</div>}
                </td>
                <td className="px-3 py-3"><span className="font-mono text-xs tabular-nums text-slate-700">{s.performance}</span></td>
                <td className="px-3 py-3"><RiskBadge risk={s.risk} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Sheet open={!!sel} onOpenChange={(o) => !o && setSel(null)}>
        <SheetContent className="w-full overflow-y-auto thin-scroll sm:max-w-[500px]">
          {sel && (<>
            <SheetHeader><SheetTitle>{sel.s.name}</SheetTitle></SheetHeader>
            <div className="mt-4 space-y-4 text-sm">
              <div className="flex items-center gap-2 text-xs text-muted-foreground"><MapPin className="h-3.5 w-3.5" />{sel.s.location} · on-time {(sel.s.on_time_rate*100).toFixed(0)}%</div>
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-lg bg-slate-50 p-3"><div className="text-[11px] text-muted-foreground">Landed cost</div><div className="font-mono text-base font-semibold tabular-nums">{fmtMoney(sel.q.total_usd)}</div></div>
                <div className="rounded-lg bg-slate-50 p-3"><div className="text-[11px] text-muted-foreground">Performance</div><div className="font-mono text-base font-semibold tabular-nums">{sel.s.performance}/100</div></div>
              </div>
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Quote line items</div>
                <div className="mt-2 space-y-1">
                  {sel.q.line_items.map((li, i) => (
                    <div key={i} className="flex items-center justify-between rounded-md bg-slate-50 px-2.5 py-1.5 text-xs">
                      <span className="text-slate-700">{li.item} ×{li.qty}</span>
                      <span className="font-mono tabular-nums text-slate-800">{fmtMoney(li.unit)}</span>
                    </div>
                  ))}
                  <div className="flex items-center justify-between px-2.5 pt-1 text-[11px] text-muted-foreground"><span>Shipping / taxes</span><span className="font-mono">{fmtMoney(sel.q.shipping)} / {fmtMoney(sel.q.taxes)}</span></div>
                </div>
              </div>
              {sel.q.fx_source && <div className="rounded-lg border border-slate-200 bg-white p-2.5 text-[11px] text-slate-600">Currency normalized from {sel.q.currency} using <b>{sel.q.fx_source}</b> @ {sel.q.fx_rate} on {sel.q.fx_ts}.</div>}
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Evidence</div>
                <div className="mt-2 flex flex-wrap gap-1.5">{sel.q.evidence_refs.map((e) => <EvidenceChip key={e} label={e} kind={e.includes("accio") ? "accio" : "evidence"} />)}</div>
              </div>
            </div>
          </>)}
        </SheetContent>
      </Sheet>
    </div>
  );
}
