# DecisionFlow AI — Concept & Theoretical Working

This document explains *what the platform is and why it works the way it does*:
the ideas behind Agentic Decision Intelligence, the Next Best Action paradigm,
and the theory of multi-agent reasoning, retrieval, explainability, human
oversight, and memory. For the concrete build, see `ARCHITECTURE.md`.

---

## 1. The Core Idea: Decision Intelligence, Not Conversation

Most "AI assistants" are conversational: a human asks, the model answers, and
nothing is remembered or acted upon. DecisionFlow AI is built on a different
premise. It is a **decision-support system** whose job is to look at everything
known about a customer and answer a single operational question:

> *"What should the Customer Success Manager do next, and why?"*

The output is not a chat reply but a ranked set of **Next Best Actions (NBAs)**,
each justified with evidence and subject to human approval. The platform is a
*reusable reasoning pipeline*, not a chatbot — the conversation is replaced by a
structured analyse → reason → recommend → review → remember loop.

---

## 2. The Next Best Action Paradigm

"Next Best Action" comes from decision science and CRM strategy. Instead of
asking a human to manually synthesise scattered signals, the system:

1. **Aggregates context** from every available source (meetings, CRM, email,
   tickets, notes).
2. **Scores the situation** for risk and opportunity.
3. **Ranks candidate actions** by priority, confidence, and business impact.
4. **Recommends the few that matter most** rather than a long undifferentiated list.

The theoretical value is *consistency and coverage*: the model never forgets to
check the renewal date, never overlooks a competitor mention, and applies the
same playbook every time — while the human retains judgment and authority.

---

## 3. Why Multiple Agents? (Separation of Concerns)

A single large prompt that tries to "read everything and decide" is brittle: it
mixes unrelated reasoning, is hard to debug, and produces shallow output. The
agentic approach instead decomposes the problem into **specialists**, each with
one narrow responsibility and its own prompt:

| Agent | Cognitive role |
|-------|----------------|
| Planner | Orchestrator — decides *which* specialists are needed |
| Conversation | Comprehension — turns unstructured dialogue into structure |
| CRM | Grounding — anchors reasoning in hard account facts |
| Knowledge | Retrieval — brings in institutional expertise |
| Risk | Critical analysis — what could go wrong |
| Opportunity | Generative analysis — what could go right |
| Recommendation | Synthesis — converts analysis into action |
| Explanation | Justification — makes reasoning transparent |
| Memory | Continuity — connects this decision to history |

This mirrors how a real account team works: different people read the meeting,
check the CRM, consult the playbook, weigh risk, and then a lead synthesises a
plan. **Separation of concerns** makes each step independently testable,
swappable, and explainable, and lets new specialists be added without disturbing
the others.

### The Planner and the orchestration principle

A key theoretical choice is that the **Planner performs no business reasoning**.
Its only job is orchestration — deciding which agents to run based on which
inputs exist. Keeping planning and reasoning separate prevents the orchestration
logic from becoming entangled with domain logic, which is what makes the
platform reusable across domains.

---

## 4. Reasoning Over Enterprise Context (RAG Theory)

A model's pretrained knowledge does not contain *your company's* pricing rules,
implementation steps, or playbooks. **Retrieval-Augmented Generation (RAG)**
closes this gap: enterprise documents are embedded into a vector space, and at
reasoning time the most semantically relevant passages are retrieved and fed to
the agents as grounding.

Theoretically this does two things. First, it *grounds* recommendations in
authoritative, current company knowledge rather than the model's priors. Second,
it provides **citable evidence** — the same retrieved passages that informed a
recommendation are shown to the human as the documents behind it. Retrieval is
therefore both a reasoning aid and an explainability mechanism.

---

## 5. Explainability as a First-Class Concept

A recommendation a human cannot scrutinise is a recommendation a human cannot
trust. DecisionFlow AI treats explanation as a dedicated stage, not an
afterthought. Every NBA is decomposed into:

- **Evidence** — the specific transcript insight, CRM fact, and knowledge
  documents that support it.
- **Reasoning** — the causal link from evidence to action.
- **Confidence** — a calibrated signal of how strongly the system believes it.
- **Business impact & expected outcome** — what is at stake and what success
  looks like.

This reflects the principle of **traceable AI**: every conclusion can be walked
back to its inputs. It converts the system from an opaque oracle into an
auditable colleague.

---

## 6. Human-in-the-Loop: Augmentation, Not Automation

The platform deliberately stops short of acting. It recommends; the human
**Approves, Rejects, or Modifies**. This embodies a specific philosophy:

- The AI handles *synthesis at scale* — reading everything, applying the playbook
  consistently, surfacing options.
- The human handles *judgment and accountability* — context the system can't see,
  relationships, and the final call.

Theoretically this is an **augmentation** model rather than full automation. It
keeps a human accountable for every customer-facing decision, and — crucially —
each human decision becomes a training signal stored in memory.

---

## 7. Memory and Continual Improvement

Without memory, every analysis starts from zero and the system can never learn
what this particular account's team actually does. The Memory concept gives the
platform **continuity over time**:

- It **recalls** prior interactions before reasoning, so recommendations are
  informed by what was tried before and how it turned out.
- It **records** every analysis and every human decision (approved / rejected /
  modified) with a timestamp and result.

Over many cycles this creates a feedback loop: approvals reinforce useful
patterns, rejections discourage poor ones, and the customer's history becomes an
asset the system reasons over. Conceptually, memory is what turns a stateless
analyser into an **organisational learning system**.

---

## 8. The Theoretical Working, Step by Step

Putting the concepts together, a single decision cycle works like this:

```
        Human uploads what they know about the account
                          │
        Memory recalls the customer's prior history
                          │
        Planner decides which specialists are required
                          │
   Comprehension  →  Grounding  →  Retrieval        (build understanding)
   (Conversation)     (CRM)        (Knowledge)
                          │
        Risk analysis  ↔  Opportunity analysis       (weigh the situation)
                          │
        Recommendation synthesises the Top-5 actions  (decide)
                          │
        Explanation attaches evidence to each one     (justify)
                          │
        Human reviews and Approves / Rejects / Modifies (govern)
                          │
        Memory stores the decision and its outcome    (learn)
                          │
        ── feeds the next cycle for this customer ──►
```

Each stage consumes the accumulated context and adds its own contribution, so
reasoning compounds: retrieval is informed by comprehension, risk is informed by
grounding and history, recommendations are informed by all of it, and every
output is explainable back to its sources.

---

## 9. Why This Generalises (Reusability Theory)

Although the reference domain is **Customer Success for SaaS** (deciding the next
action before a renewal), nothing in the architecture is specific to it. The
*structure* — plan, comprehend, ground, retrieve, weigh risk and opportunity,
recommend, explain, govern, remember — is a general template for **operational
decision-making under uncertainty**.

To re-target the platform to, say, lending, healthcare triage, or IT incident
management, one changes the **prompts** (what each specialist looks for), the
**knowledge corpus** (the institutional documents), and the **inputs** — not the
reasoning machinery. This separation of *generic reasoning structure* from
*domain-specific content* is what makes DecisionFlow AI a reusable platform
rather than a single-purpose app.

---

## 10. Summary of Guiding Principles

- Decisions, not conversations.
- Specialised agents over one monolithic prompt.
- Orchestration kept separate from reasoning.
- Grounded in enterprise knowledge via retrieval.
- Every recommendation explainable and evidence-backed.
- Humans augmented and accountable, never bypassed.
- Memory turns repeated use into organisational learning.
- Generic reasoning structure + swappable domain content = reusability.
