import React, { useState } from "react";
import { useApp } from "@/context/AppContext";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Users, ShieldAlert, Check } from "lucide-react";
import { toast } from "sonner";

const ROLE_HINT = {
  requester: "Submits requests; cannot approve own spend above threshold.",
  operator: "Runs sourcing & reviews; cannot finalize selection alone.",
  approver: "Approves a specific gate within authority threshold.",
  student: "Completes paid, supervised work; cannot self-attest competence.",
  supervisor: "Attests student competency and paid hours.",
  executive: "Oversight & impact; high authority threshold.",
  supplier: "Limited supplier view of required docs & status.",
};

export function DemoModeSwitcher() {
  const { me, actors, impersonate } = useApp();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(null);
  if (!me) return null;

  const doSwitch = async (a) => {
    setBusy(a.id);
    await impersonate(a.id);
    setBusy(null);
    setOpen(false);
    toast.success(`You are now impersonating ${a.name} · ${a.title}`);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <button data-testid="demo-mode-open-button"
          className="flex items-center gap-2 rounded-lg border border-amber-300 bg-amber-50 px-2.5 py-1.5 text-xs font-medium text-amber-900 hover:bg-amber-100 transition-colors">
          <ShieldAlert className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Demo Mode:</span>
          <span data-testid="demo-mode-current-role" className="font-semibold">{me.name.split(" ")[0]} · {me.title}</span>
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2"><Users className="h-4 w-4 text-[hsl(var(--g-teal-600))]" /> Demo Mode — Impersonate a role</DialogTitle>
          <DialogDescription>
            Switch identities to demonstrate separation-of-duties. Impersonation is a demo-only control; production uses institutional SSO.
          </DialogDescription>
        </DialogHeader>
        <div data-testid="demo-mode-role-select" className="max-h-[52vh] space-y-1.5 overflow-y-auto thin-scroll pr-1">
          {actors.map((a) => (
            <button key={a.id} onClick={() => doSwitch(a)} disabled={busy}
              data-testid={`demo-role-${a.id}`}
              className={cn("flex w-full items-center gap-3 rounded-lg border p-2.5 text-left transition-colors",
                me.id === a.id ? "border-[hsl(var(--g-teal-600))] bg-[hsl(173_84%_97%)]" : "border-border hover:bg-slate-50")}>
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-[hsl(var(--g-navy-950))] text-[11px] font-semibold text-white">{a.avatar}</span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 text-sm font-medium text-slate-900">{a.name}
                  {me.id === a.id && <Check className="h-3.5 w-3.5 text-[hsl(var(--g-teal-600))]" />}</div>
                <div className="text-[11px] text-muted-foreground">{a.title} · {a.department}</div>
                <div className="mt-0.5 text-[11px] text-slate-500">{ROLE_HINT[a.role]}</div>
              </div>
            </button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
