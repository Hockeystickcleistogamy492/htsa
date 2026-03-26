<h1 align="center">Bayesian Reasoning</h1>

> You do not find the truth all at once. You update toward it, one piece of evidence at a time.

---

## What It Is

Bayesian reasoning is a mathematical framework for **updating beliefs in the presence of new evidence**. It is named after Reverend Thomas Bayes, whose theorem describes how to rationally revise a probability estimate when you learn something new.

---

## Bayes' Theorem

```
P(H | E) = P(E | H) × P(H) / P(E)
```

| Symbol | Meaning |
|---|---|
| **P(H)** | Prior — your belief in hypothesis H before seeing evidence |
| **P(E \| H)** | Likelihood — how probable the evidence is if H is true |
| **P(E)** | Marginal — overall probability of seeing this evidence |
| **P(H \| E)** | Posterior — your updated belief after seeing the evidence |

In plain English: **start with a belief, observe evidence, update the belief.**

---

## How This Applies to Investigation

When you have multiple branches in a Why tree, each branch represents a **hypothesis** about the cause. Bayesian reasoning gives you a principled way to assign and update probabilities as evidence comes in.

```
HYPOTHESIS A: "Root cause is a misconfigured timeout"   → P(A) = 0.40
HYPOTHESIS B: "Root cause is a memory leak"             → P(B) = 0.35
HYPOTHESIS C: "Root cause is a bad deploy"              → P(C) = 0.25
```

You gather evidence:

> Evidence: The problem occurs even on builds that predate the last deploy.

This evidence is unlikely if C is true, so P(C) drops. It is consistent with A and B, so they rise:

```
HYPOTHESIS A: P(A) = 0.50  ↑
HYPOTHESIS B: P(B) = 0.44  ↑
HYPOTHESIS C: P(C) = 0.06  ↓ (nearly ruled out)
```

---

## The Prior

The **prior** is your belief before you see evidence. It should be based on:
- Past investigations in this domain
- Base rates (how often does each cause occur in similar situations?)
- Domain expertise

A good investigator does not start with equal priors on all hypotheses. They use knowledge to set informed starting points. Then they update.

---

## The Bayesian Investigation Loop

```
1. Set priors on all hypotheses (branches)
2. Gather evidence at the current Why node
3. Update probabilities using Bayes' theorem
4. Prune low-probability branches (below threshold — a common default is 5%; set this before starting)
5. Follow highest-probability branch
6. Repeat until one hypothesis dominates
```

---

## Avoiding Two Failure Modes

**1. Anchoring (too little updating)**
You set a prior and refuse to move it even when evidence contradicts it. You find the cause you expected, not the real one.

**2. Overreacting to single data points (too much updating)**
One surprising piece of evidence sends you chasing a low-probability hypothesis and abandoning correct ones. Each piece of evidence should move your belief — but proportionally.

Bayes' theorem is the cure for both. It tells you exactly how much to update.

---

## Base Rates Matter

If 80% of similar outages in your system are caused by deploys, your prior for deploy-related root causes should be 0.80, not 0.33. Ignoring base rates is one of the most common investigation errors.

```
Without base rates:  Three equal hypotheses, each at 33%
With base rates:     Deploy at 80%, config at 15%, other at 5%

Same evidence, very different investigation paths.
```

---

## Convergence

As evidence accumulates, posteriors converge — the probabilities bunch up around the true cause, and alternatives drop toward zero. A well-run Bayesian investigation **converges** on the root cause. A poorly run one stays uncertain because evidence is not being gathered or evaluated properly.

---

## Key Terms

| Term | Meaning |
|---|---|
| **Prior** | Belief before seeing evidence |
| **Posterior** | Updated belief after seeing evidence |
| **Likelihood** | How probable the evidence is under a given hypothesis |
| **Hypothesis** | A candidate root cause being evaluated |
| **Base rate** | The background frequency of a cause in similar situations |
| **Convergence** | Posteriors approaching certainty as evidence accumulates |
| **Anchoring** | Failure to update priors in response to evidence |

---

<p align="center"><strong>← Previous</strong> <strong><a href="04_information_theory.md">04 — Information Theory</a></strong> · <strong>Next →</strong> <strong><a href="06_search_algorithms.md">06 — Search Algorithms</a></strong></p>
