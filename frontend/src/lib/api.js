import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const client = axios.create({ baseURL: API });

const get = async (url, params) => (await client.get(url, { params })).data;
const post = async (url, body) => (await client.post(url, body)).data;

export const api = {
  institution: () => get("/institution"),
  me: () => get("/me"),
  actors: () => get("/demo/actors"),
  impersonate: (actor_id) => post("/demo/impersonate", { actor_id }),
  setAgentMode: (mode) => post("/demo/agent-mode", { mode }),
  reset: () => post("/demo/reset", {}),
  jump: (case_id, state) => post("/demo/jump", { case_id, state }),
  audit: (case_id) => get("/demo/audit", case_id ? { case_id } : {}),
  triggerException: (key, case_id) => post("/demo/exception", { key, case_id }),
  exceptions: (case_id) => get("/exceptions", case_id ? { case_id } : {}),

  today: () => get("/today"),
  cases: (lane) => get("/cases", lane ? { lane } : {}),
  case: (id) => get(`/cases/${id}`),
  timeline: (id) => get(`/cases/${id}/timeline`),
  transition: (id, target, evidence_refs) =>
    post(`/cases/${id}/transition`, { target, evidence_refs }),
  caseSuppliers: (id) => get(`/cases/${id}/suppliers`),
  decision: (id) => get(`/cases/${id}/decision`),
  suppliers: () => get("/suppliers"),

  approvals: (params) => get("/approvals", params || {}),
  decideApproval: (id, decision, rationale) =>
    post(`/approvals/${id}/decide`, { decision, rationale }),

  campusMemory: (q, collection) => get("/campus-memory", { q, collection }),
  impact: () => get("/impact"),
  flows: () => get("/flows"),
  notifications: () => get("/notifications"),

  studentTasks: () => get("/student/tasks"),
  studentTask: (id) => get(`/student/tasks/${id}`),
  acceptTask: (task_id) => post("/student/tasks/accept", { task_id }),
  submitQuiz: (task_id, answers) => post("/student/tasks/quiz", { task_id, answers }),
  attestTask: (task_id, level, hours) =>
    post("/student/tasks/attest", { task_id, level, hours }),
  passport: (learner_id) => get("/student/passport", learner_id ? { learner_id } : {}),

  offlineQueue: () => get("/offline/queue"),
  offlineSync: () => post("/offline/sync", {}),

  operatorViews: () => get("/operator/views"),
  operatorView: (key) => get(`/operator/view/${key}`),

  runAgent: (agent, case_id) => post("/agents/run", { agent, case_id }),
};
