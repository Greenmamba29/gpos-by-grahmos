import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";

const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);

export function AppProvider({ children }) {
  const [me, setMe] = useState(null);
  const [institution, setInstitution] = useState(null);
  const [actors, setActors] = useState([]);
  const [online, setOnline] = useState(true);
  const [agentMode, setAgentMode] = useState("seeded");
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const m = await api.me();
    setMe(m.actor);
    setOnline(m.online);
    setAgentMode(m.agent_mode);
    return m;
  }, []);

  const boot = useCallback(async () => {
    setLoading(true);
    try {
      const [inst, m, acts] = await Promise.all([api.institution(), api.me(), api.actors()]);
      setInstitution(inst);
      setMe(m.actor);
      setOnline(m.online);
      setAgentMode(m.agent_mode);
      setActors(acts);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { boot(); }, [boot]);

  const impersonate = async (actorId) => {
    const r = await api.impersonate(actorId);
    setMe(r.actor);
    return r.actor;
  };
  const toggleAgentMode = async (mode) => {
    await api.setAgentMode(mode);
    setAgentMode(mode);
  };
  const reset = async () => {
    await api.reset();
    await boot();
  };

  return (
    <Ctx.Provider value={{ me, institution, actors, online, setOnline, agentMode,
      toggleAgentMode, loading, refreshMe, impersonate, reset, boot }}>
      {children}
    </Ctx.Provider>
  );
}
