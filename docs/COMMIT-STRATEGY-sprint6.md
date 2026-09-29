# Commit & PR strategy — Sprint 6 memory close-out

> **Date:** 2026-09-30. **Status:** commits `e211bec`…`d77dc88` **executed
> locally**; **nothing pushed**. Branch is ahead of its remote by 9. Review,
> then push.
> Read with [`HANDOVER-2026-09-30.md`](HANDOVER-2026-09-30.md).

---

## 1. The situation

- `TA-agents`, branch `feat/memory-episodes`, HEAD `53be6f0`.
- **59 working-tree entries** — 33 modified, 26 untracked (23 of the untracked
  are this sprint's work; 3 are the docs written today).
- The branch was already pushed up to `53be6f0`; the 9 commits below are
  **local only**.
- Remote is a **fork** (`AmanSarraf/TA-agents`), not upstream.

**Why this is urgent, stated plainly:** 26 untracked files have no history. A
`git clean -fd`, a stray `git checkout .`, or a mis-typed branch command
destroys them irrecoverably. The rest of this document is a nice-to-have; the
first commit is a fire drill.

---

## 2. Rules this has to obey

From `TA-agents/AGENTS.md`, the workspace `AGENTS.md`, and `skills/ta-ship`:

| Rule | Consequence here |
| --- | --- |
| Every commit DCO-signed | `git commit -s` on all 9 |
| Never push to `main`; PR against `dev` | 4 PRs, all targeting `dev` |
| "Keep the PR to one logical change" | 9 commits grouped into 4 PRs, not 9 PRs |
| Never commit `.env` or secrets | `.env` is gitignored; the working key stays local |
| `tests/evals/`, `contracts/`, `ARCHITECTURE.md`, `CLAUDE.md`, `AGENTS.md`, `.github/` are CODEOWNERS-gated | PR 1 and PR 4 need `@nosoypoot` |

---

## 3. The shape: 9 commits → 4 stacked PRs

```
PR 1  feat(eval)     rerank golden set                     1 commit   ~900 lines
PR 2  feat(memory)   persistence, cache, forgetting        3 commits  ~2,900
PR 3  feat(recall)   episode recall, end to end            4 commits  ~5,800
PR 4  docs           ADR amendment, handover, Sprint 7     1 commit   ~2,400
```

Stacked in that order, each based on the previous. The headline feature —
recall, including the default reversal — is isolated in **PR 3**, which is
where a mentor's attention is worth most.

### PR 1 — `feat(eval)`: the rerank golden set

Small and independent. Establishes the precedent for judging tie-breaks.

| Commit | Files |
| --- | --- |
| `C1 feat(eval): add golden rerank/auto-select eval and relation-tag follow-ups` | `src/talent_angels/evals/rerank.py` *(new)*, `src/talent_angels/evals/__init__.py`, `src/talent_angels/session/followup.py`, `tests/conftest.py` *(new — every later test file needs it)*, `tests/evals/golden_rerank.json` *(new ⚠ CODEOWNERS)*, `tests/test_golden_rerank.py` *(new)*, `tests/test_followup.py` *(new)* |

### PR 2 — `feat(memory)`: persistence, cache, forgetting

The substrate. No recall yet — just the store and the ability to make it forget.

| Commit | Files |
| --- | --- |
| `C2 feat(memory/cache): wire the SQLite neighbour cache into the suite registry` | `src/talent_angels/memory/cache.py`, `src/talent_angels/suites/registry.py`, `tests/test_neighbor_cache_wiring.py` *(new)* |
| `C3 feat(memory): persist LangGraph checkpoints across process restarts` | `src/talent_angels/assistant/graph.py`, `src/talent_angels/memory/paths.py`, `tests/test_checkpoint_persistence.py` *(new)* |
| `C4 feat(memory/erase): make forgetting actually forget across all three stores` | `src/talent_angels/memory/erase.py` *(new)*, `src/talent_angels/session/kernel.py`, `src/talent_angels/session/commands.py`, `src/talent_angels/session/copy.py`, `src/talent_angels/tui/app.py`, `tests/test_erase_scopes.py` *(new)*, `tests/test_memory_erase.py` *(new)* |

### PR 3 — `feat(recall)`: episode recall, end to end

The headline. Carries the default reversal and the vector floor.

| Commit | Files |
| --- | --- |
| `C5 feat(recall): add the retriever seam and wire recall into the answer path` | `src/talent_angels/memory/retrieval.py` *(new)*, `src/talent_angels/session/phrase.py`, `src/talent_angels/assistant/answer.py`, `src/talent_angels/assistant/synthesize.py`, `src/talent_angels/memory/profile.py`, `tests/test_recall.py` *(new)*, `tests/test_answer.py`, `tests/test_phrase.py`, `tests/test_synthesize.py` |
| `C6 feat(recall): add FTS5 lexical episode recall behind TA_RECALL` | `src/talent_angels/memory/episodes.py`, `src/talent_angels/memory/fts_retriever.py` *(new)*, `src/talent_angels/env.py`, `src/talent_angels/cli.py`, `tests/test_fts_retriever.py` *(new)* |
| `C7 feat(recall): add sqlite-vec semantic recall with a relevance floor` | `src/talent_angels/memory/embeddings.py` *(new)*, `src/talent_angels/memory/vector_index.py` *(new)*, `src/talent_angels/memory/vector_retriever.py` *(new)*, `src/talent_angels/memory/fallback_retriever.py` *(new)*, `src/talent_angels/evals/recall.py` *(new)*, `pyproject.toml`, `tests/test_vector_recall.py` *(new)*, `tests/test_fallback_recall.py` *(new)*, `tests/test_recall_harness.py` *(new)* |
| `C8 fix(assistant/session): guard pathfind intent and stop profile text surviving reset` | `src/talent_angels/assistant/agent_loop.py`, `src/talent_angels/assistant/turn.py`, `src/talent_angels/tui/render.py`, `tests/test_agent_loop.py`, `tests/test_session.py`, `tests/test_session_turns.py`, `tests/test_tui_entry.py`, `tests/test_tui_render.py` |

### PR 4 — `docs`: the record

| Commit | Files |
| --- | --- |
| `C9 docs: amend ADR-0007, hand over Sprint 6, and plan the Sprint 7 B2B pilot` | `.env.example`, `README.md`, `ARCHITECTURE.md` *(⚠ CODEOWNERS)*, `docs/decisions/0007-memory-architecture.md`, `docs/gate2-conocer-b2b-pilot.md` *(new)*, `docs/HANDOVER-2026-09-30.md` *(new)*, `docs/SPRINT7-B2B-PLAN.md` *(new)*, `docs/COMMIT-STRATEGY-sprint6.md` *(new)* |

---

## 4. Two commits carry the reasoning, not just the diff

**C7** and **C9** are where a reviewer must actually read. Their messages should
not be one-liners. Draft bodies:

**C7** — why a floor exists, with the number:

> Vector search without a relevance floor answers *every* irrelevant question
> with its nearest neighbour. Measured on a 30-turn corpus, 43 queries: the
> unfloored vector retriever returned 210 irrelevant hits against 0 for lexical
> and 0 for floored vector. `MIN_RELEVANCE_SCORE = -1.10` sits in the measured
> gap — irrelevant top-1 scores span `-1.303`…`-1.197`, answerable top-1
> `-1.018`…`-0.234`.
>
> The floor is calibrated from **seven** irrelevant queries and the corpora are
> English-only. Recalibrate before trusting it on other languages or corpora.

**C9** — why the default changed:

> Recall defaulted to `off` on the sound reasoning that a feature which changes
> what the app says back to you should not surprise anyone who did not ask for
> it. It now defaults to `hybrid`, because the measurement ended the question
> the decision was waiting on: 0/36 unanswered at p@1 0.917 with 0 irrelevant
> hits, and the common path costs nothing — no network, no embedding, no index.
> An install without credentials or without a built index degrades to lexical
> and warns once. The invariant that protects a user who never wanted recall is
> unchanged and now tested: **a question with nothing to recall leaves the
> system prompt byte-identical.**

---

## 5. Honest caveats

1. **Per-commit green is not guaranteed, and I have not verified it.** `env.py`
   and `episodes.py` accumulate changes from both C6 and C7; splitting them
   cleanly means either two partial commits or one combined one. The current
   gate result (653 passed) is for the **whole tree**, not for each commit. If
   bisectability matters to you, say so and I will verify it in a scratch
   worktree before touching this branch. If not, PR-level review is the unit
   that matters and the 4-PR split already delivers that.

2. **Two docs in PR 4 have broken links, and I recommend fixing them before
   pushing** rather than after review:
   - `docs/gate2-conocer-b2b-pilot.md` links to `../data/SPRINT7_PILOTS_PROPOSAL.md`,
     which is inside the gitignored `/data/` and therefore not in the repo.
   - The same doc links to `../../docs/decisions/0006-taxonomy-data-sources.md`,
     which resolves inside `TA-agents` — but ADR-0006 actually lives in
     `TA-memory/decisions/`.

3. **The planning docs are invisible to the team.** `/data/` is gitignored, so
   `SPRINT6_PILOTS_PROPOSAL`, `SPRINT7_PILOTS_PROPOSAL`, `TA_SPRINT6_HANDOFF`
   and `SPRINT6_MEETING_NOTES` are all local-only. Options: move prose to
   `docs/`, or add a `!data/*.md` negation to `.gitignore`. I lean toward the
   negation — least churn, and the data dumps stay ignored. **Your call.**

4. **`TA-taxonomies` needs its own push, separately.** Branch
   `feat/hybrid-search`, tree **clean**, 5 commits including the Tier 5 hybrid
   search (`365b806`) and the suite implementation guide. It is a different
   repo with its own review surface, and it is where the Sprint 7 Gate 0 work
   happens. Do not bundle it with the `TA-agents` PRs.

5. **Do not squash.** The 9 commits are the unit of review. Squash only if a
   mentor asks, and then only PR 4 — never PR 3.

---

## 6. Commands (do not run without approval)

```bash
cd TA-agents

# 0. Fire drill first: get the untracked files into history, cheaply.
#    This one commit is the insurance policy. Everything else can be redone;
#    an untracked file cannot.
git add tests/conftest.py tests/test_fts_retriever.py src/talent_angels/memory/fts_retriever.py
git commit -s -m "chore: checkpoint the untracked recall files into history"

# 1. Verify the gates are green before making anything reviewable
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q --ignore=tests/integration      # expect 653 passed

# 2..9 then commit C1..C9 in the order above, each with `git add <files>` and
#     `git commit -s`. Never `git add -A` — it will sweep in the stale plan
#     docs and anything else lying around.

# 10. Push and open the PRs, stacked against dev
git push -u fork feat/memory-episodes
gh pr create --base dev --head feat/memory-episodes
```

For stacked PRs, the workspace already uses `gh stack`; the base is `dev`.

---

## 7. If you would rather not do nine commits

Reasonable alternative, and much less work: **two PRs.**

- PR A — everything except the docs (all 8 code commits as one).
- PR B — the docs.

Honest cost: PR A becomes ~9,000 lines, and a mentor has to review the memory
substrate, the recall seam, the vector index and the default reversal in one
pass. That is a worse review, and the review is the point of the exercise.

My recommendation is still the 4-PR split. But the 2-PR version is a legitimate
choice if the priority is getting the work off this laptop today — which, given
that 26 files are currently unbacked, is a real consideration.
