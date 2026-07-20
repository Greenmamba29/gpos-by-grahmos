import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, Loading } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Award, CheckCircle2, Clock, Briefcase, ShieldCheck } from "lucide-react";

export default function SkillsPassport() {
  const [data, setData] = useState(null);
  useEffect(() => { api.passport("u_student").then(setData); }, []);
  if (!data) return <Loading />;

  return (
    <div className="mx-auto max-w-[1080px]">
      <PageHeader title="Skills Passport & Career Launch" subtitle="Verified skills, paid hours, and matched employment opportunities." />
      <Card className="mb-5 overflow-hidden">
        <div className="flex items-center gap-4 bg-[hsl(270_74%_97%)] p-5">
          <span className="grid h-16 w-16 place-items-center rounded-full bg-[hsl(var(--g-navy-950))] text-lg font-semibold text-white">{data.learner?.avatar}</span>
          <div><div className="text-lg font-semibold text-slate-900">{data.learner?.name}</div>
            <div className="text-xs text-muted-foreground">{data.learner?.title} · {data.learner?.department}</div>
            <div className="mt-1 flex items-center gap-3 text-[11px] text-[hsl(var(--g-purple-700))]"><span className="flex items-center gap-1"><Clock className="h-3 w-3" />{data.total_hours}h paid</span><span className="flex items-center gap-1"><Award className="h-3 w-3" />{data.competencies.filter((c)=>c.verified).length} verified</span></div></div>
        </div>
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        <div>
          <div className="mb-2 text-sm font-semibold text-slate-900">Skills Passport</div>
          <div className="space-y-2">
            {data.competencies.map((c) => (
              <Card key={c.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-900">{c.name}
                    {c.verified && <Badge variant="outline" className="h-5 border-emerald-200 bg-emerald-50 px-1.5 text-[10px] text-emerald-700"><ShieldCheck className="mr-0.5 h-2.5 w-2.5" />Verified</Badge>}</div>
                  <span className="text-[11px] font-medium text-[hsl(var(--g-purple-700))]">{c.level}</span>
                </div>
                <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground"><span>{c.hours}h logged</span><span>{c.evidence_refs.length} evidence artifact(s)</span></div>
              </Card>
            ))}
          </div>
        </div>
        <div>
          <div className="mb-2 text-sm font-semibold text-slate-900">Career Launch · Matched Opportunities</div>
          <div className="space-y-2">
            {data.opportunities.map((j) => (
              <Card key={j.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div><div className="flex items-center gap-2 text-sm font-semibold text-slate-900"><Briefcase className="h-4 w-4 text-slate-400" />{j.title}</div>
                    <div className="text-[11px] text-muted-foreground">{j.employer} · {j.type} · {j.pay}</div></div>
                  <div className="text-right"><div className="text-sm font-semibold text-[hsl(var(--g-purple-700))]">{j.match}%</div><div className="text-[10px] text-muted-foreground">match</div></div>
                </div>
                <Progress value={j.match} className="mt-2 h-1.5" />
                <div className="mt-2 flex flex-wrap gap-1">{j.skills.map((s) => <span key={s} className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-600">{s}</span>)}</div>
                <Button size="sm" variant="outline" className="mt-3" data-testid={`apply-${j.id}`}>View & apply</Button>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
