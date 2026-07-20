import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, KpiTile, Loading, fmtMoney } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Clock, DollarSign, Truck, GraduationCap, ShieldCheck, Briefcase } from "lucide-react";

export default function ImpactCenter() {
  const [d, setD] = useState(null);
  useEffect(() => { api.impact().then(setD); }, []);
  if (!d) return <Loading />;
  const k = d.kpis;

  return (
    <div className="mx-auto max-w-[1280px]">
      <PageHeader title="Impact Command Center" subtitle="Cycle time, savings, supplier performance, paid hours, and employment conversions." />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <KpiTile label="Savings YTD" value={fmtMoney(k.savings_ytd)} delta={k.savings_delta_pct} icon={DollarSign} accent="teal" testid="impact-savings" />
        <KpiTile label="Avg cycle time" value={`${k.avg_cycle_time_days}d`} delta={k.cycle_time_delta} icon={Clock} accent="navy" testid="impact-cycle" />
        <KpiTile label="On-time delivery" value={`${Math.round(k.on_time_delivery*100)}%`} icon={Truck} accent="teal" testid="impact-ontime" />
        <KpiTile label="Paid student hours" value={k.paid_student_hours} icon={GraduationCap} accent="purple" testid="impact-hours" />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <Card className="p-4">
          <div className="mb-3 text-sm font-semibold text-slate-900">Cycle time trend (days)</div>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={d.cycle_trend} margin={{ left: -18, right: 8, top: 8 }}>
              <CartesianGrid stroke="hsl(220 16% 90%)" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(222 14% 42%)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(222 14% 42%)" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid hsl(220 16% 88%)" }} />
              <Line type="monotone" dataKey="days" stroke="hsl(173 80% 33%)" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
        <Card className="p-4">
          <div className="mb-3 text-sm font-semibold text-slate-900">Savings by lane</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={d.savings_by_lane} margin={{ left: -6, right: 8, top: 8 }}>
              <CartesianGrid stroke="hsl(220 16% 90%)" vertical={false} />
              <XAxis dataKey="lane" tick={{ fontSize: 10, fill: "hsl(222 14% 42%)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(222 14% 42%)" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid hsl(220 16% 88%)" }} formatter={(v) => fmtMoney(v)} />
              <Bar dataKey="savings" fill="hsl(214 45% 26%)" radius={[6,6,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_320px]">
        <Card className="overflow-hidden">
          <div className="border-b border-border px-4 py-2.5 text-sm font-semibold text-slate-900">Supplier performance</div>
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-slate-50 text-left text-[11px] uppercase tracking-wide text-slate-500"><tr><th className="px-4 py-2 font-medium">Supplier</th><th className="px-3 py-2 font-medium">Score</th><th className="px-3 py-2 font-medium">On-time</th></tr></thead>
            <tbody>{d.supplier_perf.map((s) => (
              <tr key={s.supplier} className="border-b border-border last:border-0">
                <td className="px-4 py-2.5 text-slate-800">{s.supplier}</td>
                <td className="px-3 py-2.5 font-mono tabular-nums">{s.score}</td>
                <td className="px-3 py-2.5 font-mono tabular-nums">{Math.round(s.on_time*100)}%</td>
              </tr>))}</tbody>
          </table>
        </Card>
        <div className="space-y-3">
          <KpiTile label="Employment conversions" value={k.employment_conversions} icon={Briefcase} accent="purple" />
          <KpiTile label="Policy violations prevented" value={k.policy_violations_prevented} icon={ShieldCheck} accent="navy" />
        </div>
      </div>
    </div>
  );
}
