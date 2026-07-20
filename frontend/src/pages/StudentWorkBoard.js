import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useApp } from "@/context/AppContext";
import { PageHeader, Loading, StatusBadge, EvidenceChip } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { GraduationCap, Clock, DollarSign, User, CheckCircle2, Lock, BookOpen, Award } from "lucide-react";

export default function StudentWorkBoard() {
  const { me } = useApp();
  const [task, setTask] = useState(null);
  const [answers, setAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = async () => { const t = await api.studentTask("lt_quote_validation"); setTask(t); };
  useEffect(() => { load(); }, [me]);
  if (!task) return <Loading />;

  const doneCount = task.stages.filter((s) => s.done).length;
  const pct = Math.round((doneCount / task.stages.length) * 100);
  const isSupervisor = me?.role === "supervisor";

  const accept = async () => { setBusy(true); await api.acceptTask(task.id); await load(); setBusy(false); toast.success("Assignment accepted — micro-lesson unlocked"); };
  const submitQuiz = async () => {
    setBusy(true);
    const arr = task.quiz.map((_, i) => answers[i] ?? -1);
    const r = await api.submitQuiz(task.id, arr);
    setQuizResult(r); await load(); setBusy(false);
    r.passed ? toast.success(r.note) : toast.error(r.note);
  };
  const attest = async () => { setBusy(true); try { await api.attestTask(task.id, "Proficient", 2.0); await load(); toast.success("Competency attested · paid hours recorded"); } catch (e) { toast.error(e?.response?.data?.detail || "Blocked"); } setBusy(false); };

  return (
    <div className="mx-auto max-w-[1080px]">
      <PageHeader title="Student Work Board" subtitle="Paid, supervised procurement work — learn a skill, then apply it to a real case." />
      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <Card className="p-5">
          <div className="flex items-start justify-between">
            <div><div className="flex items-center gap-2 text-base font-semibold text-slate-900"><GraduationCap className="h-5 w-5 text-[hsl(var(--g-purple-600))]" />{task.title}</div>
              <p className="mt-1 text-xs text-slate-600">{task.goal}</p></div>
            <StatusBadge status={task.status} />
          </div>
          <div className="mt-3"><Progress value={pct} className="h-2" /><div className="mt-1 text-[11px] text-muted-foreground">{doneCount}/{task.stages.length} stages · {pct}%</div></div>
          <Separator className="my-4" />

          {task.status === "AVAILABLE" && (
            <div className="space-y-3">
              <div className="rounded-lg bg-[hsl(270_74%_97%)] p-3 text-xs text-[hsl(var(--g-purple-700))]"><b>Prerequisite:</b> intro to procurement basics (auto-satisfied for demo).</div>
              <Button onClick={accept} disabled={busy} data-testid="accept-task-button" className="bg-[hsl(var(--g-purple-600))] hover:bg-[hsl(var(--g-purple-700))]">Accept paid assignment (${task.pay_rate}/hr)</Button>
            </div>
          )}

          {["IN_PROGRESS","AWAITING_SUPERVISOR","COMPLETED"].includes(task.status) && (
            <div className="space-y-4">
              <div className="rounded-lg border border-border p-3">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-900"><BookOpen className="h-3.5 w-3.5 text-[hsl(var(--g-purple-600))]" /> Micro-lesson</div>
                <p className="mt-1 text-xs leading-5 text-slate-600">Landed cost = price + shipping + taxes + duties − substitutions. A quote’s <b>validity</b> is how long the price is guaranteed. To compare multiple currencies, normalize with an FX source + timestamp.</p>
              </div>

              <div className="rounded-lg border border-border p-3">
                <div className="text-xs font-semibold text-slate-900">Knowledge check</div>
                <div className="mt-2 space-y-3">
                  {task.quiz.map((qq, i) => (
                    <div key={i}>
                      <div className="text-xs font-medium text-slate-800">{i+1}. {qq.q}</div>
                      <div className="mt-1.5 grid gap-1.5">
                        {qq.options.map((opt, j) => (
                          <button key={j} onClick={() => setAnswers({ ...answers, [i]: j })} disabled={task.status !== "IN_PROGRESS"}
                            data-testid={`quiz-${i}-opt-${j}`}
                            className={cn("rounded-md border px-2.5 py-1.5 text-left text-[11px] transition-colors",
                              answers[i] === j ? "border-[hsl(var(--g-purple-500))] bg-[hsl(270_74%_97%)]" : "border-border hover:bg-slate-50")}>{opt}</button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                {task.status === "IN_PROGRESS" && <Button size="sm" className="mt-3" onClick={submitQuiz} disabled={busy} data-testid="submit-quiz-button">Submit knowledge check</Button>}
                {quizResult && <div className={cn("mt-2 rounded-md p-2 text-[11px]", quizResult.passed ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-800")}>{quizResult.correct}/{quizResult.total} correct. {quizResult.note}</div>}
              </div>

              {task.status === "AWAITING_SUPERVISOR" && (
                <div className="rounded-lg border border-[hsl(var(--g-navy-800))] bg-[hsl(214_45%_97%)] p-3">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-[hsl(var(--g-navy-900))]"><Lock className="h-3.5 w-3.5" /> Supervisor attestation required</div>
                  <p className="mt-1 text-[11px] text-slate-600">Passing the quiz alone does not grant competency. A supervisor must review the work and attest.</p>
                  {isSupervisor
                    ? <Button size="sm" className="mt-2 bg-[hsl(var(--g-navy-950))] hover:bg-[hsl(var(--g-navy-900))]" onClick={attest} disabled={busy} data-testid="attest-button">Attest competency (Proficient, 2.0h)</Button>
                    : <p className="mt-2 text-[11px] font-medium text-amber-700">Switch to <b>Alex Nguyen (Supervisor)</b> in Demo Mode to attest.</p>}
                </div>
              )}

              {task.status === "COMPLETED" && (
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-800"><Award className="h-3.5 w-3.5" /> Competency attested: {task.competency_result}</div>
                  <p className="mt-1 text-[11px] text-emerald-700">{task.hours_logged}h paid · evidence recorded. See your Skills Passport.</p>
                  <div className="mt-2"><EvidenceChip label="Signed evidence event" kind="policy" /></div>
                </div>
              )}
            </div>
          )}
        </Card>

        <Card className="h-fit p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Assignment details</div>
          <dl className="mt-3 space-y-2.5 text-xs">
            <div className="flex items-center gap-2"><DollarSign className="h-3.5 w-3.5 text-slate-400" /><span className="text-muted-foreground">Pay</span><span className="ml-auto font-medium">${task.pay_rate}/hr</span></div>
            <div className="flex items-center gap-2"><Clock className="h-3.5 w-3.5 text-slate-400" /><span className="text-muted-foreground">Hours logged</span><span className="ml-auto font-mono">{task.hours_logged}h</span></div>
            <div className="flex items-center gap-2"><User className="h-3.5 w-3.5 text-slate-400" /><span className="text-muted-foreground">Supervisor</span><span className="ml-auto font-medium">{task.supervisor?.name}</span></div>
            <div className="flex items-center gap-2"><GraduationCap className="h-3.5 w-3.5 text-slate-400" /><span className="text-muted-foreground">Learner</span><span className="ml-auto font-medium">{task.learner?.name}</span></div>
          </dl>
          <Separator className="my-3" />
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Rubric</div>
          <ul className="mt-2 space-y-1.5">{task.rubric.map((r, i) => (
            <li key={i} className="flex items-center justify-between text-[11px]"><span className="text-slate-600">{r.criterion}</span><span className="font-mono text-slate-400">/{r.max}</span></li>))}</ul>
        </Card>
      </div>
    </div>
  );
}
