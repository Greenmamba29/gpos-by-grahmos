import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, Loading, EmptyState, fmtDay } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Search, FileText, ScrollText, Building2, Handshake, ShieldCheck } from "lucide-react";

const ICON = { Policies: ShieldCheck, Contracts: Handshake, Decisions: ScrollText, Suppliers: Building2, Evidence: FileText, All: FileText };

export default function CampusMemory() {
  const [data, setData] = useState(null);
  const [q, setQ] = useState("");
  const [col, setCol] = useState("All");
  const [sel, setSel] = useState(null);

  const load = async () => setData(await api.campusMemory(q, col));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [q, col]);
  if (!data) return <Loading />;

  return (
    <div className="mx-auto max-w-[1180px]">
      <PageHeader title="Campus Memory" subtitle="Searchable institutional memory — policies, decisions, contracts, supplier history, and evidence." />
      <div className="grid gap-5 lg:grid-cols-[220px_1fr]">
        <div className="space-y-1">
          {data.collections.map((c) => {
            const Icon = ICON[c] || FileText;
            return (
              <button key={c} onClick={() => setCol(c)} data-testid={`memory-col-${c}`}
                className={cn("flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  col === c ? "bg-[hsl(173_84%_95%)] text-[hsl(var(--g-navy-950))]" : "text-slate-600 hover:bg-slate-100")}>
                <Icon className="h-4 w-4" /> {c}
              </button>
            );
          })}
        </div>
        <div>
          <div className="relative mb-3">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input value={q} onChange={(e) => setQ(e.target.value)} data-testid="memory-search"
              placeholder="Search policies, decisions, suppliers, evidence…"
              className="h-11 w-full rounded-xl border border-border bg-white pl-10 pr-3 text-sm outline-none focus:border-[hsl(var(--g-teal-600))] focus:ring-2 focus:ring-[hsl(173_84%_90%)]" />
          </div>
          {data.docs.length === 0 ? <EmptyState title="No results" hint="Try a different search or collection." /> : (
            <div className="space-y-2">
              {data.docs.map((d) => (
                <Card key={d.id} onClick={() => setSel(d)} data-testid={`memory-doc-${d.id}`} className="cursor-pointer p-4 hover:bg-slate-50">
                  <div className="flex items-start justify-between gap-3">
                    <div><div className="text-sm font-semibold text-slate-900">{d.title}</div>
                      <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-600">{d.body}</p></div>
                    <Badge variant="outline" className="shrink-0 text-[10px]">{d.collection}</Badge>
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                    {d.tags.map((t) => <span key={t} className="rounded bg-slate-100 px-1.5 py-0.5">#{t}</span>)}
                    <span className="ml-auto">Updated {fmtDay(d.updated)}</span>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
      <Sheet open={!!sel} onOpenChange={(o) => !o && setSel(null)}>
        <SheetContent className="w-full overflow-y-auto thin-scroll sm:max-w-[520px]">
          {sel && (<>
            <SheetHeader><SheetTitle>{sel.title}</SheetTitle></SheetHeader>
            <div className="mt-4 space-y-3">
              <Badge variant="outline">{sel.collection}</Badge>
              <p className="text-sm leading-6 text-slate-700">{sel.body}</p>
              <div className="rounded-lg bg-slate-50 p-3 text-xs">
                <div className="font-semibold text-slate-700">Provenance</div>
                <div className="mt-1 text-slate-500">Updated {fmtDay(sel.updated)} · {sel.linked_cases?.length || 0} linked case(s)</div>
              </div>
            </div>
          </>)}
        </SheetContent>
      </Sheet>
    </div>
  );
}
