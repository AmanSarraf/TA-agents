# Sprint 7 — B2B adaptation of the Talent Angels pilot

> **Status:** plan, open for discussion. Not an ADR; the decisions that bind go
> through ADR-0008.
> **Date:** 2026-09-30. **Supersedes nothing:** the design research is in
> [`gate2-conocer-b2b-pilot.md`](gate2-conocer-b2b-pilot.md) (702 lines, and
> good — read it before planning). This document is the *sequenced, re-verified*
> version. **Where the two disagree, this one wins**, because the research was
> written before the graph state was checked. See
> [`HANDOVER-2026-09-30.md`](HANDOVER-2026-09-30.md).

---

## 1. What "B2B adaptation" actually means

Talent Angels so far is a **one-person** product: one user asks about their
own career, and the assistant answers from the graph plus that user's memory.
Sprint 7 pilots are the **one-business** mode: *a whole organisation brings its
own data*, and gets back a business deliverable that is not an answer to a
question.

That shift changes three things, and only these three:

| | One person (shipped) | One business (Sprint 7) |
| --- | --- | --- |
| Who owns the goal | the user, in conversation | the business, in a batch |
| What comes in | a question | *their* graph, in *their* shape |
| What comes out | an answer | an enriched copy of their own data |
| Who reads it | the asker | a colleague who never asked |
| Cost of a mistake | mildly confusing | a wrong claim in someone's business process |

Everything else — the suite contract, `locate()`, `AgentResult`, the run log,
`LLM_PROVIDER=none`, the MCP edge — is reusable as-is. **Gate 2 needs no new
agent, no new graph access, and no new search.** That is the single most
reassuring fact in this plan, and it is why Gate 2 is achievable by one person.

The whole risk is on the other side of the table: for the first time we touch
somebody else's data and hand back a business deliverable.

---

## 2. The critical path changed. Read this first.

The research doc lists P0 as "chase the branch and the export — not a code
task". That is still true, and there is a **second, larger** P0 that the
research predates:

> **The graph does not currently contain full ESCO.** Verified live on
> 2026-09-30: the `EscoOccupation`/`EscoSkill` labels do not exist; only the
> 51-node ICT *fixture* is present. O\*NET **is** loaded (31,942 nodes).

The pilot's entire deliverable is "CONOCER's own graph, carrying real ESCO/O\*NET
skill tags". Right now one of those two taxonomies is a six-occupation sample.
The pilot cannot produce a credible deliverable on a fixture.

**The good news: this is not a research problem.** `docs/esco-full-load.md`
documents a complete, previously measured procedure — 22 s ingest, 45 MB on
disk, `search_nodes` median 11 ms — and the 52 MB of source data is already on
disk. It just needs re-running; the dedicated `ta-neo4j-full` container it
targets no longer exists on this machine.

So P0 has two halves, and they are very different in effort:

| P0 item | Effort | Risk |
| --- | --- | --- |
| Re-create `ta-neo4j-full`, load full ESCO, run both embed batches | ~1 hour, fully scripted and previously measured | Low — the procedure is written down and has run before |
| Chase CONOCER's branch + export | Unknown, external, **not a code task** | High — blocks everything downstream |

**Recommendation: do the ESCO half immediately, in parallel with waiting on
CONOCER.** It is unblocked, cheap, and it de-risks Gate 2's quality ceiling. It
also independently unlocks Tier 5 semantic search (§5), which is a user-visible
improvement to the one-person product and needs no pilot at all.

---

## 3. Gate 0 — unblock the graph (do this first, ~1 hour)

Do not start the pilot design work on a fixture.

- [ ] Re-create `ta-neo4j-full` per `docs/esco-full-load.md` §1 (Bolt 7690, so
      the day-to-day database on 7687 is never touched).
- [ ] Load full ESCO with an **explicit** `--mode` and `NEO4J_URI`. The default
      is `--mode fixture`, which **wipes the ESCO labels first** — this is the
      easiest way to destroy a day of work.
- [ ] Validate: expect ~1,400 occupations and ~3,000+ skills, not 6 and 51.
- [ ] Run the embed batch for **both** suites: `esco/embed.py` and
      `onet/embed.py`. Confirm a `VECTOR` index appears in `SHOW INDEXES` and
      that nodes carry `label_embedding`. **This has never been run.**
- [ ] Declare `ta-taxonomies` in `pyproject.toml` (still commented out pending
      ADR-0004) so a clean clone can run the pilot. Gate 2's quality ceiling
      depends on being reproducible for the rest of the team, not just on one
      laptop.
- [ ] Re-run the recall harness and the locate evals against the *full* graph.
      Every quality number we have was measured on a 6-occupation fixture for
      ESCO, so **all ESCO-side numbers are provisional and must be re-measured.**

**Exit criteria:** full ESCO present; one vector index per suite; a clean
checkout on a second machine reproduces the graph; locate/recall evals
re-measured and recorded.

---

## 4. Gate 1 — the tracer bullet (one sitting, no LLM)

The research doc is emphatic and correct here: build P1 as a single tracer
bullet. **One standard, one suite, five criteria, no LLM, no review.** If the
seam is not obvious in one sitting, the design is wrong — and that is cheap to
find out, which is the entire point of doing it this way.

**The shape of the tracer bullet**

```
CONOCER Element  (their graph, their labels)
      │
      ▼
  locate()          ← pure, LLM-free, single call, already exists
      │
      ▼
  ESCO/O*NET Skill + confidence + evidence pointer
      │
      ▼
  write back into THEIR graph, same shape they sent
```

Four things this deliberately does **not** do: no LLM, no batch beyond five
criteria, no new capability, no review workflow, no UI. Every one of those is a
thing you can add after you know the seam is real.

**The one genuinely new piece** is the *bidirectional* edge — a business's node
gains a pointer to a Talent Angels taxonomy node. That is the first time
cross-graph referencing happens, and it is where the licensing and
evidence-as-pointer rules get their first real test.

### 4.1 The `method` question — decide this early

**Landmine.** `locate()` drops each candidate's `method` label
(`skills/locate/resolve.py:45-49, 96`). So when we write "this CONOCER element
maps to ESCO skill X", we cannot currently say *how* we know — only that
auto-select rated it 0.95. For an internal tool that is fine. For a business
deliverable that a third party will act on, "how did you decide this?" is the
first question asked, and we would have no answer.

Three options, in order of my preference:

| Option | What it costs | Review needed |
| --- | --- | --- |
| **A. Adapter reads `ToolResult.candidates` directly**, in a new `enrichment/` module, and owns both the verdict and the ledger | No contract change. Duplicates a little logic that `locate()` already did | None |
| B. One additive optional field on `AgentResult` | Cleanest long-term; makes provenance first-class everywhere | **Yes** — `contracts/` is CODEOWNERS-protected |
| C. Ignore it for the pilot | Zero effort | Ships a deliverable we can't defend |

**I would take A now and B later, and I would not block the tracer bullet on
this.** The research doc reaches the same conclusion. Option A is a genuine
throwaway: if it turns out the whole product wants provenance, promote it to B
later — the adapter is already the only caller.

**Explicitly record the quality target before looking at results.**
Extract-then-map reaches ~83% end-to-end precision (ESCoE Skills Extractor);
LLM-extract + vector-match ≈80% (SkiLLMo, ACM SAC 2025). Quote a number in
advance — ~80%, with the known failure modes (metaphor, multi-skill) named —
so "we got 61%" is read as a finding rather than a disappointment.

---

## 5. Gate 2 — run the pilot, then make it reproducible

Once the tracer bullet is real:

- [ ] Run Locate node-by-node over the 3 standards received (EC1705, EC1691,
      EC-PROMPT) — each Element's performance/product/knowledge/attitude text
      submitted individually, real skill tags returned.
- [ ] Produce the enriched result: **CONOCER's own graph, same shape it came
      in**, now carrying skill tags. That round-trip is the proof of concept.
- [ ] Measure and report: precision per standard, failure taxonomy, and
      time-per-element. Include the misses — the failure modes are the
      reusable knowledge.
- [ ] Share the GitHub branch so the rest of the team can run the pilot, not
      just read about it. **This is still outstanding from the last sync and it
      is the difference between a pilot and a demo.**
- [ ] Keep the whole deterministic half runnable under `LLM_PROVIDER=none`.
      The MCP edge is the precedent: it is already a non-chat programmatic
      consumer of the suite contract, with a clean error-is-a-return discipline.

**Independent of the pilot, and worth doing in parallel:** Tier 5 semantic
search is implemented, committed, and **completely dormant** (no vector index
has ever been built). Turning it on is one command from Gate 0, and it improves
the one-person product that the rest of the team actually uses today.

---

## 6. Parallel track — Pathfinder and the taxonomies

These are Gate 1 in the existing proposal and are **not** blocked by the pilot.
They do not need CONOCER, and they do not need ESCO's data to be correct code.

**Pathfinder** — `skills/pathfind/` is an empty directory. The honest
"not implemented" response works and the fall-through bug is already fixed, so
this is a clean build with no firefighting:

- [ ] Decide the route-finding contract before writing the tool: what is a
      path, what is a step, what does it cite, and what is a *disqualifier*
      (a gap too wide to bridge is a finding, not a failure).
- [ ] One tool, deterministic, in code — not a model call. Depth caps and
      top-K cuts belong in the tool per `ARCHITECTURE.md`.
- [ ] Real tests replacing the placeholder assertion, including the
      "no route exists" case. **That negative case is the product.** "You cannot
      get from nurse to software developer in one hop" is a useful, honest,
      expensive-to-fake answer; inventing a plausible path is the failure mode
      to design against.

**Taxonomies** — 2 of 5 sources present. Ordered by value to the crosswalk:

- [ ] **BLS/SOC** first, despite being "structure only". SOC is the spine that
      ties O\*NET, BLS and ESCO's ISCO mapping together. A crosswalk with no
      spine is four disconnected graphs.
- [ ] **SFIA** second — codes, names, levels, structure only. **Never** its
      descriptive text (licensing). Levels are first-class nodes: level 4 of a
      skill is not level 7 of the same skill.
- [ ] **Sweden JobTech** last — CC0, ~6.9M postings, additive signal rather
      than crosswalk backbone.
- [ ] Resolve ADR-0006's open question before building JobTech: does its
      taxonomy actually carry ESCO concept mappings? Unverified since the ADR
      was written.

---

## 7. What is decided vs. what is not

**Already decided — do not re-litigate:**
- Sprint 7's pilot work is business-focused; keep designing for one-person too.
- CONOCER first, because its data is in hand and already graph-shaped.
- Gate 2 needs no new agent, no new graph access, no new search.
- SFIA is structure-only; levels are first-class nodes.
- The deterministic half must stay runnable with `LLM_PROVIDER=none`.

**Not decided — needs a decision, with a recommendation:**

| Question | Recommendation |
| --- | --- |
| Where does cross-graph provenance live? | Adapter first (`enrichment/`), contract change later if it generalises |
| Is "one element at a time" a new capability? | Decide **from the experiment**. Most likely it is Locate in a loop, owned by the business side — and saying so early stops it becoming a premature skill |
| Does the business-facing deliverable get its own interface? | MCP edge first. It already exists, it is already a non-chat consumer, and it avoids inventing a UI before the shape is known |
| Does the full ESCO graph replace the fixture, or sit beside it? | Sit beside it, in its own container on 7690. The fixture stays as the fast offline test fixture — that is what makes the test suite quick |

---

## 8. Risks, and the ones I would bet on

Ranked by my actual confidence, not by how bad they sound.

1. **CONOCER's data does not arrive** (external, uncontrolled). Everything in
   Gate 2 is blocked on it. *Mitigation:* do the ESCO work now so that when it
   arrives the pilot can start the same day. Also: Pilot B (the university) is
   a real fallback and needs no external data at all.
2. **Precision lands near 60–70%, not 80%.** Plausible — the literature number
   is best-case and our corpus is different. *This is a finding, not a
   failure*, provided the number was agreed in advance and the misses are
   characterised. The failure mode to avoid is discovering the expectation
   afterwards.
3. **Per-node quality hides a bad standard.** One standard may score well
   because it is easy. *Mitigation:* report per-standard, never aggregate only.
4. **Licensing slips.** CONOCER's text is theirs; ESCO's structure is
   redistributable but its descriptive text is not. Evidence-as-pointer exists
   precisely for this. *Mitigation:* keep the boundary mechanical from commit
   one — pointers, never copied payloads.
5. **The tracer bullet takes three days instead of one sitting.** Means the
   seam is in the wrong place. *Mitigation:* it is explicitly scoped so this is
   discoverable cheaply — that is the entire reason for scoping it this tightly.
6. **Pathfinder and the taxonomies get starved by pilot work.** Real. *Either*
   sequence them explicitly as parallel tracks with their own owner, *or*
   accept they slip. What does not work is leaving them on a checklist next to
   the pilot items and hoping.
