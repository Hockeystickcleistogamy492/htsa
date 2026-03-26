<h1 align="center">Causal Inference</h1>

> Correlation tells you what moves together. Causation tells you what actually caused what. These are not the same thing.

---

## What It Is

Causal inference is the mathematical discipline of determining **cause and effect** from data and evidence. It was formalized by statistician and computer scientist **Judea Pearl**, whose work established that causation cannot be derived from correlation alone — it requires a model.

Pearl's central tool: the **DAG** (Directed Acyclic Graph) — the exact same structure as the 5 Whys tree.

---

## The Problem With "Why"

When you ask why something happened, you are making a causal claim. But two things can be correlated — moving together — without either causing the other.

**Classic example:**
- Ice cream sales and drowning rates are correlated.
- Ice cream does not cause drowning.
- A third variable — **hot weather** — causes both.

This third variable is called a **confounder**. Causal inference is largely about identifying and controlling for confounders.

---

## Pearl's Ladder of Causation

Pearl describes three levels of causal reasoning:

| Level | Question | Example |
|---|---|---|
| **1. Association** | What is? | "The system crashed when the deploy ran." |
| **2. Intervention** | What if I do X? | "If I roll back the deploy, will the system recover?" |
| **3. Counterfactual** | What if X had not happened? | "Would the crash have happened without the deploy?" |

The 5 Whys operates primarily at **Level 2 and 3**. Each Why answer is an intervention claim — "this caused that." Strong investigations test counterfactuals at every node.

---

## The Do-Calculus

Pearl formalized causation with **do-notation**:

```
P(Y | X)       = probability of Y given that we observe X
P(Y | do(X))   = probability of Y given that we intervene and SET X
```

These are different. Observing that it's raining does not cause wet ground. Intervening (making it rain) does. The 5 Whys is always asking the **do(X)** question — not just "did these things co-occur?" but "did this actively produce that?"

---

## How This Applies to the Framework

At every Why node, you are making a causal claim. That claim must meet a minimum standard:

**The Counterfactual Test:**
> "If this Why answer had NOT been true, would the problem still have occurred?"

- If **yes** → this is not the cause. Continue looking.
- If **no** → this is a genuine causal factor. Record it and continue down.

```
Why 3: "The alert threshold was set too high"
  Counterfactual test: If the threshold had been correct, would the outage still have happened?
  Answer: No → genuine cause → continue to Why 4
```

---

## Confounders in Investigations

A **confounder** is a hidden variable that causes two things to appear related when they are not.

```
[Deploy ran] ──────────────► [System crashed]
      ▲                              ▲
      └──── [Traffic spike] ─────────┘
```

Both the deploy and the crash correlate. But the real cause is the traffic spike. The deploy just happened to coincide with it. Without causal inference discipline, you blame the deploy and fix the wrong thing.

---

## Key Principles

1. **Correlation is not causation.** Always test the counterfactual.
2. **Confounders exist.** Look for hidden variables that explain the correlation.
3. **Causation requires a mechanism.** How did X produce Y? If you cannot state the mechanism, you have not established cause.
4. **The DAG is the model.** Drawing your Why tree IS doing causal inference. The structure of the graph encodes your causal assumptions.

---

## Key Terms

| Term | Meaning |
|---|---|
| **Causal inference** | The math of determining what caused what |
| **Confounder** | A hidden variable that creates false correlations |
| **Counterfactual** | "What would have happened if X had not occurred?" |
| **Do-calculus** | Pearl's formal notation for intervention vs. observation |
| **DAG** | Directed Acyclic Graph — the mathematical model of causation |
| **Mechanism** | The process by which a cause produces an effect |

---

<p align="center"><strong>← Previous</strong> <strong><a href="02_exponential_problem_space.md">02 — Exponential Problem Space</a></strong> · <strong>Next →</strong> <strong><a href="04_information_theory.md">04 — Information Theory</a></strong></p>
