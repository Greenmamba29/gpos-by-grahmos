import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { PageHeader, Loading } from "@/components/shared";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import {
  Building2, UserRound, ClipboardCheck, GraduationCap, ArrowRight, ArrowLeft,
  Check, Sparkles, ShieldCheck, Clock, Rocket,
} from "lucide-react";

const LANES = ["Event Procurement", "IT & SaaS", "Facilities + Microfactory", "Classroom + Lab"];

const TRACKS = {
  admin: {
    label: "Institution Admin Setup", icon: Building2, target: "\u226412 min", accent: "navy",
    intro: "Make campus requests governable without slowing people down.",
    steps: [
      { t: "Welcome", d: "Set up Grahmos for your institution. You'll see value before any identity-heavy setup.", cta: "Start setup" },
      { t: "Outcome selection", d: "Choose your launch goals.", field: "outcomes",
        options: ["Savings", "Speed", "Student work", "Compliance", "Supplier diversity"] },
      { t: "Institution profile", d: "Campus, timezone, fiscal year, data residency.", input: ["campuses", "fiscal_year"] },
      { t: "Identity", d: "SSO if available; otherwise a demo identity directory. Note: enterprise SSO is deferred for the demo.", note: "Purpose: resolve who can request, approve, and supervise." },
      { t: "Departments + roles", d: "Import or map requesters, operators, approvers, supervisors.", note: "9 demo actors are pre-seeded for you." },
      { t: "Authority + SoD", d: "Thresholds, dual control, delegations, prohibited combinations.", note: "Facilities \u2264 $30k \u00b7 Finance \u2264 $50k \u00b7 Procurement \u2264 $40k. Requester cannot self-approve above $5k." },
      { t: "Connections", d: "Grahmos Assist, workflows, Slack/Telegram, email/calendar, LMS, ERP (sandbox).", note: "All external systems run in sandbox for the demo." },
      { t: "Agent Team", d: "Preview roles, skills, tools, and channel capabilities; run a test request.", note: "Grahmos Assist proposes; humans authorize." },
      { t: "Launch checklist", d: "Pick your launch lanes, owners, and sample data.", field: "lanes", options: LANES, cta: "Launch workspace" },
    ],
  },
  requester: {
    label: "Requester Onboarding", icon: UserRound, target: "\u22643 min", accent: "teal",
    intro: "Describe what you need; Grahmos finds the right path.",
    steps: [
      { t: "Value first", d: "Describe a need in plain language \u2014 Grahmos turns it into a governed, evidence-backed case." },
      { t: "Your role", d: "Confirm your department and preferred channel & language.", input: ["department"] },
      { t: "Request type", d: "Choose from the four launch lanes, or 'Not sure'.", field: "lane", options: LANES.concat(["Not sure"]) },
      { t: "First practice request", d: "Create a first low-risk request with inline guidance.", cta: "Try Request Hub", link: "/request" },
      { t: "Track & respond", d: "Preview status tracking and how to respond when Grahmos asks a question.", cta: "Finish" },
    ],
  },
  operator: {
    label: "Procurement Operator Onboarding", icon: ClipboardCheck, target: "guided", accent: "teal",
    intro: "Own the queue, review agent work, keep governance tight.",
    steps: [
      { t: "Outcome dashboard", d: "Learn your queue vocabulary and outcome tiles.", link: "/", cta: "Peek at Today" },
      { t: "Decision packet anatomy", d: "Facts vs inferences, evidence, risk, and recommendation \u2014 kept separate from authorization." },
      { t: "Reviewing agent work", d: "How to review Grahmos Assist findings and request reruns." },
      { t: "Approvals & SoD", d: "How approval/SoD gates work and what an override records (reason + policy + expiry)." },
      { t: "Failure & offline", d: "Walkthrough of the exception queue and offline-conflict resolution." },
      { t: "Supervised case sim", d: "Complete one supervised case simulation before production access.", cta: "Finish" },
    ],
  },
  student: {
    label: "Student Fellow Onboarding", icon: GraduationCap, target: "\u22648 min", accent: "purple",
    intro: "Turn paid, supervised work into verified skills and job pathways.",
    steps: [
      { t: "Choose a goal", d: "Supplier research, quote analysis, logistics, facilities, or contract ops.", field: "goal",
        options: ["Supplier research", "Quote analysis", "Logistics", "Facilities/Microfactory", "Contract ops"] },
      { t: "How this works", d: "Paid work, a supervisor relationship, data rules, and what agents may assist with." },
      { t: "Baseline check", d: "One quick scenario question \u2014 no long placement test." },
      { t: "Micro-lesson", d: "A lesson tied to a real task (demo: quote validation).", link: "/students", cta: "Open Work Board" },
      { t: "First guided action", d: "A worked example with AI coach hints." },
      { t: "Submit evidence", d: "Submit your work and receive supervisor feedback." },
      { t: "Earn & launch", d: "See competencies earned, hours/pay, next task, and the employment pathway.", link: "/passport", cta: "Finish" },
    ],
  },
};

const TRACK_ICON_ACCENT = {
  navy: "bg-slate-100 text-[hsl(var(--g-navy-900))]",
  teal: "bg-[hsl(173_84%_95%)] text-[hsl(var(--g-teal-700))]",
  purple: "bg-[hsl(270_74%_96%)] text-[hsl(var(--g-purple-700))]",
};

export default function Onboarding() {
  const [statuses, setStatuses] = useState(null);
  const [track, setTrack] = useState(null);
  const [step, setStep] = useState(0);
  const [data, setData] = useState({});
  const nav = useNavigate();

  useEffect(() => { api.onboardingStatus().then((r) => setStatuses(r.tracks)); }, []);

  const openTrack = async (key) => {
    const saved = await api.getOnboarding(key);
    setTrack(key); setStep(saved.completed ? 0 : saved.current_step || 0); setData(saved.data || {});
  };

  const persist = async (nextStep, completed = false) => {
    await api.saveOnboarding({ track, current_step: nextStep, data, completed });
  };

  const cfg = track ? TRACKS[track] : null;
  const s = cfg?.steps[step];

  const next = async () => {
    if (track === "admin" && s.t === "Institution profile") {
      await api.updateInstitution({ campuses: data.campuses, fiscal_year: data.fiscal_year });
    }
    if (track === "admin" && s.t === "Launch checklist") {
      await api.updateInstitution({ launch_lanes: data.lanes || [] });
    }
    if (step + 1 >= cfg.steps.length) {
      await persist(cfg.steps.length, true);
      toast.success(`${cfg.label} complete!`);
      const status = await api.onboardingStatus(); setStatuses(status.tracks);
      if (s.link) nav(s.link); else setTrack(null);
      return;
    }
    await persist(step + 1);
    setStep(step + 1);
  };

  if (!statuses) return <Loading />;

  if (!track) {
    return (
      <div className="mx-auto max-w-[1080px]">
        <PageHeader title="Get Started" subtitle="Role-based onboarding — value first, progress saved, resume anytime." />
        <div className="grid gap-3 sm:grid-cols-2">
          {Object.entries(TRACKS).map(([key, t]) => {
            const st = statuses.find((x) => x.track === key) || {};
            const Icon = t.icon;
            const pct = Math.round(((st.current_step || 0) / t.steps.length) * 100);
            return (
              <Card key={key} onClick={() => openTrack(key)} data-testid={`track-${key}`}
                className="cursor-pointer p-5 transition-transform hover:-translate-y-0.5">
                <div className="flex items-start gap-3">
                  <span className={cn("grid h-11 w-11 place-items-center rounded-xl", TRACK_ICON_ACCENT[t.accent])}><Icon className="h-5 w-5" /></span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">{t.label}
                      {st.completed && <Check className="h-4 w-4 text-emerald-600" />}</div>
                    <p className="mt-0.5 text-xs text-muted-foreground">{t.intro}</p>
                    <div className="mt-2 flex items-center gap-2 text-[11px] text-slate-500">
                      <Clock className="h-3 w-3" />{t.target} · {t.steps.length} steps</div>
                    <Progress value={st.completed ? 100 : pct} className="mt-2 h-1.5" />
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    );
  }

  const Icon = cfg.icon;
  const pct = Math.round(((step + 1) / cfg.steps.length) * 100);
  return (
    <div className="mx-auto max-w-[760px]">
      <button onClick={() => setTrack(null)} className="mb-3 text-[11px] text-[hsl(var(--g-teal-700))] hover:underline">← All tracks</button>
      <div className="mb-4 flex items-center gap-3">
        <span className={cn("grid h-10 w-10 place-items-center rounded-xl", TRACK_ICON_ACCENT[cfg.accent])}><Icon className="h-5 w-5" /></span>
        <div className="flex-1"><div className="text-sm font-semibold text-slate-900">{cfg.label}</div>
          <Progress value={pct} className="mt-1.5 h-1.5" /></div>
        <span className="font-mono text-xs text-slate-500">Step {step + 1}/{cfg.steps.length}</span>
      </div>

      <Card className="p-6" data-testid="onboarding-step">
        <div className="text-lg font-semibold tracking-[-0.01em] text-slate-900">{s.t}</div>
        <p className="mt-2 text-sm leading-6 text-slate-600">{s.d}</p>
        {s.note && <div className="mt-3 rounded-lg bg-slate-50 p-3 text-xs text-slate-600"><Sparkles className="mr-1 inline h-3.5 w-3.5 text-[hsl(var(--g-teal-600))]" />{s.note}</div>}

        {s.field && (
          <div className="mt-4 flex flex-wrap gap-2">
            {s.options.map((o) => {
              const arr = data[s.field] || (s.field === "outcomes" || s.field === "lanes" ? [] : "");
              const active = Array.isArray(arr) ? arr.includes(o) : arr === o;
              const toggle = () => {
                if (Array.isArray(arr)) {
                  const nv = active ? arr.filter((x) => x !== o) : [...arr, o];
                  setData({ ...data, [s.field]: nv });
                } else setData({ ...data, [s.field]: o });
              };
              return (
                <button key={o} onClick={toggle} data-testid={`opt-${o.replace(/[^a-zA-Z]+/g, "-")}`}
                  className={cn("rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
                    active ? "border-[hsl(var(--g-teal-600))] bg-[hsl(173_84%_95%)] text-[hsl(var(--g-teal-700))]" : "border-border text-slate-600 hover:bg-slate-50")}>
                  {active && <Check className="mr-1 inline h-3 w-3" />}{o}
                </button>
              );
            })}
          </div>
        )}

        {s.input && (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {s.input.map((f) => (
              <div key={f}><label className="text-[11px] font-medium capitalize text-slate-600">{f.replace(/_/g, " ")}</label>
                <Input value={data[f] || ""} onChange={(e) => setData({ ...data, [f]: e.target.value })} className="mt-1 text-sm" data-testid={`input-${f}`} /></div>
            ))}
          </div>
        )}

        <div className="mt-6 flex items-center justify-between">
          <Button variant="ghost" size="sm" disabled={step === 0} onClick={() => setStep(step - 1)} data-testid="onboarding-back"><ArrowLeft className="mr-1 h-3.5 w-3.5" />Back</Button>
          <Button onClick={next} data-testid="onboarding-next" className="bg-[hsl(var(--g-navy-950))] hover:bg-[hsl(var(--g-navy-900))]">
            {s.cta || "Continue"} <ArrowRight className="ml-1 h-3.5 w-3.5" />
          </Button>
        </div>
      </Card>

      <div className="mt-3 flex items-center gap-2 text-[11px] text-muted-foreground">
        <ShieldCheck className="h-3.5 w-3.5" /> Progress is saved and resumable — you won't lose entered data.
      </div>
    </div>
  );
}
