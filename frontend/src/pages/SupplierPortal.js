import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useApp } from "@/context/AppContext";
import { PageHeader, Loading, StatusBadge, RiskBadge, EvidenceChip, fmtMoney } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Store, FileCheck2, FileX2, MinusCircle, MapPin, ShieldCheck, AlertTriangle, Package } from "lucide-react";

const DOC_STATUS = {
  on_file: { c: "text-emerald-700 bg-emerald-50 border-emerald-200", i: FileCheck2, label: "On file" },
  missing: { c: "text-red-700 bg-red-50 border-red-200", i: FileX2, label: "Missing" },
  not_applicable: { c: "text-slate-500 bg-slate-50 border-slate-200", i: MinusCircle, label: "N/A" },
};

export default function SupplierPortal() {
  const { me } = useApp();
  const [data, setData] = useState(null);

  useEffect(() => {
    // If impersonating a supplier, map to seeded supplier; else default to Capital Event Group
    const sid = me?.role === "supplier" ? "sup_capital" : "sup_capital";
    api.supplierPortal(sid).then(setData);
  }, [me]);

  if (!data) return <Loading />;
  const s = data.supplier;

  return (
    <div className="mx-auto max-w-[1080px]">
      <PageHeader title="Supplier Portal"
        subtitle="A focused supplier view of engagements, required documents, and quote status. Grahmos remains the system of record." />

      <Card className="mb-5 overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-slate-50 p-5">
          <div className="flex items-center gap-3">
            <span className="grid h-12 w-12 place-items-center rounded-xl bg-[hsl(var(--g-navy-950))] text-white"><Store className="h-5 w-5" /></span>
            <div>
              <div className="text-base font-semibold text-slate-900">{s.name}</div>
              <div className="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3" />{s.location} · on-time {(s.on_time_rate * 100).toFixed(0)}% · performance {s.performance}/100
              </div>
            </div>
          </div>
          <RiskBadge risk={s.risk} />
        </div>
      </Card>

      <div className="grid gap-5 lg:grid-cols-[1fr_340px]">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-900"><Package className="h-4 w-4" /> My Engagements</div>
          {data.engagements.length === 0 ? (
            <Card className="p-6 text-center text-sm text-muted-foreground">No active engagements.</Card>
          ) : (
            <div className="space-y-2">
              {data.engagements.map(({ case: c, quote: q, quote_status, selected }) => (
                <Card key={c.id} className="p-4" data-testid={`engagement-${c.id}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold text-slate-900">{c.title}</div>
                      <div className="mt-1 flex items-center gap-2 text-[11px] text-muted-foreground">
                        <StatusBadge status={c.state} />
                        <span className="font-mono">{fmtMoney(q.total_usd)}</span>
                        <span>lead {q.lead_time_days}d</span>
                      </div>
                    </div>
                    <span className={cn("rounded-full border px-2 py-0.5 text-[11px] font-medium",
                      selected ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-amber-200 bg-amber-50 text-amber-900")}>
                      {quote_status}
                    </span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {q.evidence_refs.map((e) => <EvidenceChip key={e} label={e} kind={e.includes("accio") ? "accio" : "evidence"} />)}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-900"><ShieldCheck className="h-4 w-4" /> Required Documents</div>
          <Card className="divide-y divide-border">
            {data.documents.filter((d) => d.required !== false || d.status !== "not_applicable").map((d, i) => {
              const st = DOC_STATUS[d.status] || DOC_STATUS.not_applicable;
              const Icon = st.i;
              return (
                <div key={i} className="flex items-center justify-between px-4 py-3">
                  <div className="text-xs text-slate-700">{d.name}{d.required === true && <span className="ml-1 text-red-500">*</span>}</div>
                  <span className={cn("inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium", st.c)}>
                    <Icon className="h-3 w-3" />{st.label}
                  </span>
                </div>
              );
            })}
          </Card>
          {data.unknowns.length > 0 && (
            <Card className="mt-3 border-amber-200 bg-amber-50 p-3">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-amber-900"><AlertTriangle className="h-3.5 w-3.5" /> Open items</div>
              <ul className="mt-1 list-inside list-disc text-[11px] text-amber-800">{data.unknowns.map((u) => <li key={u}>{u.replace(/_/g, " ")}</li>)}</ul>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
