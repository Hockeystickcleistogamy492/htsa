"""
Prompt templates for LLM-driven HTSA investigation.

Each function builds the user message for a specific judgment call.
The SYSTEM_PROMPT provides framework context for all calls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..investigation import Investigation


SYSTEM_PROMPT = """\
You are an investigation advisor using the HTSA (How to Solve Anything) framework.

HTSA investigates problems through 4 layers:
1. Situation Map — establish the 5 Ws (Who, What, When, Where, Why-surface)
2. Causal Chain — recursive Why questions forming a tree of hypotheses
3. Resolution — fix, mitigate, or accept each root cause
4. Verification — confirm fixes work, capture learning

Key rules:
- Evidence tiers: Physical (1, strongest), Observational (2), Inferential (3), Testimonial (4, weakest)
- Evidence direction: SUPPORTS or CONTRADICTS a hypothesis
- Sibling hypothesis probabilities must sum to 1.0
- Root cause requires 4 depth criteria: Actionability, Counterfactual Clarity, System Boundary, Diminishing Returns
- Resolution types: fix (eliminate cause), mitigate (reduce impact), accept (acknowledge and monitor)
- Counterfactual test: "If this fix had existed before the problem, would the problem still have happened?"

Always respond with valid JSON matching the requested schema. No markdown fences."""


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def build_context(inv: Investigation, focus_node_id: str | None = None) -> str:
    """Build a compact text summary of the current investigation state."""
    lines: list[str] = []

    # Situation
    sit = inv.situation
    if sit.what:
        lines.append("SITUATION:")
        for field, label in [
            ("who_affected", "Who affected"),
            ("who_detector", "Who detected"),
            ("what", "What"),
            ("when_before", "Before"),
            ("when_during", "During"),
            ("when_after", "After"),
            ("where", "Where"),
            ("why_surface", "Surface Why"),
        ]:
            val = getattr(sit, field, "")
            if val:
                lines.append(f"  {label}: {val}")
        lines.append("")

    # Tree
    if inv.graph.origin_id:
        lines.append("INVESTIGATION TREE:")
        _render_tree(inv, inv.graph.origin_id, lines, focus_node_id)
        lines.append("")

    # Pruned
    pruned = inv.pruned_branches
    if pruned:
        lines.append("PRUNED:")
        for n in pruned:
            p = f"{n.pruned_probability:.0%}" if n.pruned_probability else "?"
            lines.append(f"  - {n.statement} (was {p})")
        lines.append("")

    lines.append(f"Entropy: {inv.entropy:.3f}")
    return "\n".join(lines)


def _render_tree(
    inv: Investigation,
    node_id: str,
    lines: list[str],
    focus_id: str | None,
) -> None:
    node = inv.graph.get_node(node_id)
    indent = "  " * (node.depth + 1)
    marker = " << FOCUS" if focus_id and node.id == focus_id else ""
    prob = f"{node.probability:.0%}" if node.probability > 0 else "?"
    lines.append(f"{indent}[{prob}] {node.statement} ({node.status.value}){marker}")
    for e in node.evidence:
        lines.append(
            f"{indent}  | {e.direction.value}: {e.description} (Tier {e.tier.value})"
        )
    for child_id in inv.graph.children_ids(node_id):
        _render_tree(inv, child_id, lines, focus_id)


# ---------------------------------------------------------------------------
# Layer 1 — Situation Map
# ---------------------------------------------------------------------------

def situation_prompt(problem: str, context: str = "") -> str:
    extra = f"\n\nAdditional context:\n{context}" if context else ""
    return f"""\
Analyze this problem and extract the 5 Ws for a situation map.

Problem: {problem}{extra}

Respond with JSON:
{{
  "who_affected": "who is affected by this problem",
  "who_detector": "who or what detected the problem",
  "what": "what happened — the core event or symptom",
  "when_before": "what was the normal state before",
  "when_during": "when the problem occurred or was noticed",
  "where": "where it happened — system, location, environment",
  "why_surface": "the immediate, surface-level apparent reason"
}}

Fill every field you can infer. Use empty string "" for fields you cannot determine."""


# ---------------------------------------------------------------------------
# Layer 2 — Causal Chain
# ---------------------------------------------------------------------------

def hypotheses_prompt(inv: Investigation, parent_id: str, count: int = 3) -> str:
    ctx = build_context(inv, focus_node_id=parent_id)
    parent = inv.graph.get_node(parent_id)
    existing = inv.graph.children_ids(parent_id)
    existing_text = ""
    if existing:
        names = [inv.graph.get_node(cid).statement for cid in existing]
        existing_text = f"\n\nExisting hypotheses (do not duplicate): {', '.join(names)}"

    return f"""\
{ctx}

Generate {count} hypotheses for WHY: "{parent.statement}"
{existing_text}
Each hypothesis should be a specific, testable causal claim.
Probabilities must sum to 1.0 across all {count} hypotheses.

Respond with JSON:
{{
  "hypotheses": [
    {{"statement": "specific causal claim", "probability": 0.4, "reasoning": "why likely"}}
  ]
}}"""


def evidence_prompt(node_statement: str, description: str, source: str) -> str:
    return f"""\
Classify this evidence for the hypothesis: "{node_statement}"

Evidence source: {source}
Evidence description: {description}

Respond with JSON:
{{
  "tier": 1,
  "direction": "supports",
  "reasoning": "why this tier and direction"
}}

Tier guide:
1 = Physical/instrumental (logs, sensors, measurements, controlled experiments)
2 = Observational (direct witness observation at the time)
3 = Inferential (reasoned conclusion from Tier 1/2 evidence)
4 = Testimonial (recalled after the fact, hearsay)

Direction: "supports" or "contradicts"."""


def likelihoods_prompt(node_statement: str, evidence_desc: str, direction: str) -> str:
    return f"""\
Estimate Bayesian likelihood ratios for this evidence.

Hypothesis: "{node_statement}"
Evidence: {evidence_desc}
Direction: {direction}

P(evidence | hypothesis true) = likelihood
P(evidence | hypothesis false) = likelihood_complement

Respond with JSON:
{{
  "likelihood": 0.9,
  "likelihood_complement": 0.2,
  "reasoning": "explanation"
}}

Values must be between 0.01 and 0.99."""


def node_evaluation_prompt(inv: Investigation, node_id: str) -> str:
    ctx = build_context(inv, focus_node_id=node_id)
    node = inv.graph.get_node(node_id)

    return f"""\
{ctx}

Evaluate the focused node: "{node.statement}"

Should this node be:
- "branch" — dig deeper, generate sub-hypotheses (there are deeper causes)
- "root_cause" — this is specific and actionable enough to be a root cause
- "needs_evidence" — gather evidence before deciding

Consider:
- Is this specific enough to act on directly? (root_cause)
- Could there be deeper underlying causes? (branch)
- Do we need evidence to evaluate this? (needs_evidence)

Respond with JSON:
{{
  "decision": "branch",
  "reasoning": "why this decision"
}}"""


def depth_criteria_prompt(inv: Investigation, node_id: str) -> str:
    ctx = build_context(inv, focus_node_id=node_id)
    node = inv.graph.get_node(node_id)
    evidence_text = "\n".join(
        f"  - [{e.tier.name}] {e.direction.value}: {e.description}"
        for e in node.evidence
    ) if node.evidence else "  (none)"

    return f"""\
{ctx}

Evaluate the 4 depth criteria for: "{node.statement}"

Evidence:
{evidence_text}

1. Actionability — Can someone take a concrete action to address this cause?
2. Counterfactual Clarity — If we fix this, would the original problem not have occurred?
3. System Boundary — Have we reached the edge of what we can control or change?
4. Diminishing Returns — Would going deeper yield meaningfully different actions?

Respond with JSON:
{{
  "actionability": true,
  "counterfactual_clarity": true,
  "system_boundary": true,
  "diminishing_returns": true,
  "reasoning": "explanation for each criterion"
}}"""


def generate_evidence_prompt(inv: Investigation, node_id: str) -> str:
    ctx = build_context(inv, focus_node_id=node_id)
    node = inv.graph.get_node(node_id)

    return f"""\
{ctx}

For the hypothesis: "{node.statement}"

Based on your knowledge, what evidence would exist in a real investigation?
Generate 1-3 pieces of evidence, classifying each by tier and direction.

Respond with JSON:
{{
  "evidence": [
    {{
      "source": "where this evidence comes from",
      "description": "what the evidence shows",
      "tier": 1,
      "direction": "supports"
    }}
  ]
}}"""


def suggest_evidence_prompt(inv: Investigation, node_id: str) -> str:
    ctx = build_context(inv, focus_node_id=node_id)
    node = inv.graph.get_node(node_id)

    return f"""\
{ctx}

For the hypothesis: "{node.statement}"

What evidence should we look for to test this hypothesis?
Suggest 2-4 specific things to check.

Respond with JSON:
{{
  "suggestions": [
    {{
      "what_to_check": "specific thing to look for",
      "source": "where to find it",
      "expected_tier": 1,
      "if_found": "what finding it would mean",
      "if_not_found": "what not finding it would mean"
    }}
  ]
}}"""


# ---------------------------------------------------------------------------
# Layer 3 — Resolution
# ---------------------------------------------------------------------------

def resolution_prompt(inv: Investigation, node_id: str) -> str:
    ctx = build_context(inv, focus_node_id=node_id)
    node = inv.graph.get_node(node_id)
    evidence_text = "\n".join(
        f"  - {e.description}" for e in node.evidence
    ) if node.evidence else "  (none)"

    return f"""\
{ctx}

Propose a resolution for root cause: "{node.statement}"

Evidence:
{evidence_text}

Resolution types:
- "fix" — eliminate the cause entirely
- "mitigate" — reduce impact or likelihood
- "accept" — acknowledge and monitor (when fixing isn't feasible)

Rate impact, recurrence risk, and actionability on 1-5 scale.

Respond with JSON:
{{
  "type": "fix",
  "change": "specific change to implement",
  "owner": "who should implement this",
  "impact": 5,
  "recurrence": 4,
  "actionability": 5,
  "reasoning": "why this resolution"
}}"""


def counterfactual_prompt(inv: Investigation, node_id: str) -> str:
    node = inv.graph.get_node(node_id)
    change = node.resolution.change if node.resolution else "(no resolution set)"

    return f"""\
Counterfactual test for root cause: "{node.statement}"

Proposed fix: {change}

If this fix had existed BEFORE the problem occurred, would the problem still have happened?

Respond with JSON:
{{
  "passes": true,
  "reasoning": "why the fix would or would not have prevented the problem"
}}

passes=true means the fix WOULD have prevented the problem."""


# ---------------------------------------------------------------------------
# Layer 4 — Verification
# ---------------------------------------------------------------------------

def verification_prompt(inv: Investigation, node_id: str) -> str:
    node = inv.graph.get_node(node_id)
    change = node.resolution.change if node.resolution else "(no resolution)"

    return f"""\
Define a verification window for: "{node.statement}"

Resolution: {change}

Window types:
- "event_driven" — wait for the next trigger event
- "time_driven" — wait one full cycle
- "continuous" — measure over a defined interval

Respond with JSON:
{{
  "window_type": "event_driven",
  "description": "what we are waiting for or measuring",
  "metric": "how we will know the fix worked"
}}"""
