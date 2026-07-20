"""
AgentProvider — model-neutral LLM interface for GPOS agents.

Claude Sonnet 4.5 primary, GPT-5 fallback (via EMERGENT_LLM_KEY).
Model *proposes* schema-validated JSON; the kernel authorizes/executes.

Two modes:
  - "seeded": deterministic fixtures (default; used for the Golden Demo, zero LLM spend)
  - "live":   real Claude reasoning (toggle in UI; requires key balance)

Every proposal is schema-validated; if the live model fails validation OR the key has
no balance, we gracefully fall back to the seeded proposal so the demo never breaks.
"""
import os
import json
import uuid

from jsonschema import validate as js_validate, ValidationError

PRIMARY = ("anthropic", "claude-sonnet-4-5-20250929")
FALLBACK = ("openai", "gpt-5")

SHARED_SYS = (
    "You are a GPOS procurement agent operating for Howard University. "
    "Separate verified facts, user statements, and inferences. Never fabricate suppliers, "
    "quotes, certifications, laws, approvals, shipment events, or learning evidence. "
    "Preserve source references and timestamps for every material claim. Recommendations "
    "do NOT authorize spend. Return ONLY a single valid JSON object, no prose, no fences."
)


def _extract_json(text: str):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        raise ValueError("no json object")
    return json.loads(text[s:e + 1])


async def run_live(system_message: str, user_text: str, schema: dict):
    """Attempt real LLM (Claude primary, GPT-5 fallback). Returns (data, model) or raises."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    key = os.environ.get("EMERGENT_LLM_KEY")
    last = None
    for prov, mod in (PRIMARY, FALLBACK):
        for _ in range(2):
            try:
                chat = LlmChat(api_key=key, session_id=f"gpos-{uuid.uuid4()}",
                               system_message=system_message).with_model(prov, mod)
                raw = await chat.send_message(UserMessage(text=user_text))
                data = _extract_json(raw if isinstance(raw, str) else str(raw))
                js_validate(instance=data, schema=schema)
                return data, f"{prov}:{mod}"
            except (ValueError, ValidationError, json.JSONDecodeError) as ex:
                last = ex
                continue
            except Exception as ex:  # budget / network / provider errors
                last = ex
                break
    raise RuntimeError(str(last))


# ---- Schemas (used for both live validation and to document proposal shape) ----
REQUEST_SCHEMA = {
    "type": "object",
    "required": ["category", "risk", "normalized", "missing_fields"],
    "properties": {
        "category": {"type": "string"},
        "risk": {"type": "string"},
        "normalized": {"type": "object"},
        "missing_fields": {"type": "array"},
    },
}


async def agent_propose(mode, agent_key, context, schema, seeded_builder):
    """Return (proposal, provenance). seeded_builder() -> dict is the deterministic fixture."""
    seeded = seeded_builder(context)
    if mode == "live":
        try:
            user = f"CONTEXT:\n{json.dumps(context, default=str)[:4000]}\n\nProduce the proposal."
            data, model = await run_live(SHARED_SYS + "\n" + context.get("instruction", ""),
                                         user, schema)
            return data, {"mode": "live", "model": model}
        except Exception as ex:
            return seeded, {"mode": "seeded_fallback", "error": str(ex)[:160]}
    return seeded, {"mode": "seeded"}
