# 2026-04-28 — Phase 8.1: post-release doc fixes

*Endorsement Marker: Local stewardship — U. Warring, AG Schätz, Physikalisches
Institut Freiburg.*

## Context

Two small doc-text inconsistencies in the artefacts shipped at the
`pilot-v0.1` tag (commit `9a0fc76`). Caught in a post-release pass.
Both are zero-bytes-of-code fixes; the tag stays at `9a0fc76`
because re-tagging would be destructive and the fixes are downstream
polish, not corrections to the release content itself.

## What was done

### Fix 1 — README layout block

The `Layout` ASCII tree had `notebooks/` annotated as "deliverables
2–4: validation, scans, regime map". After Phase 7 shipped notebook
04 (deliverable 5 — design table), this is one off and out of order.

Updated to "deliverables 2–5: validation, regime map, scans, design
table". The new order matches the actual notebook numbering
(`01_baseline_validation`, `02_regime_map`, `03_parameter_scans`,
`04_design_table`).

### Fix 2 — `docs/deliverable-index.md` §4.4 lead-in

The "Validation surfaces" section opened with "The five §4.4
cross-method consistency checks all pass" — but the table below
lists more than five rows because Phase 4.1 added the resolved-mesh
A↔C equilibrium check and the raw-operator mass-conservation check,
and the original five span both `test_equilibrium.py` and
`test_method_consistency.py`.

Updated lead-in: "The §4.4 cross-method consistency surface — the
five core checks listed in the spec plus the additional Method-C
and Phase-4.1 surfaces added during implementation — is pinned
end-to-end by the test suite". The table content is unchanged.

### Conversational miscount (not an artefact change)

Reviewer also noted that my Phase-8 release summary said "9 commits
on main" — actual `git rev-list --count --first-parent main` is 15.
That number was wrong in conversation only; no committed artefact
contained it. The right framing — used in the deliverable index and
lab notes — is "9 numbered phases plus review-fix `.1` commits". No
fix needed in the repository.

## Decisions

| Decision | Rationale |
|---|---|
| Fix on `main` post-tag rather than re-tagging | Re-tagging is destructive (force-update changes a published reference). The release tag captures a known state at `9a0fc76`; doc nits accumulate as `.1` commits and the next release tag (if any) picks them up. |
| No new release tag | Two two-line prose fixes don't justify a `pilot-v0.1.1`. If subsequent post-release polish accumulates enough to warrant it, a patch tag can be cut then. |
| Lab note despite tiny fix size | Consistency with the established `.1` pattern. The audit trail is more valuable than the marginal cost of the note. |

## Verification

```
HEAD before this pass:  9a0fc769887872164738c1e0ee383f7536c67b72
Python 3.13.7
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9

$ PYTHONPATH=src pytest -q
92 passed in 3.47s
$ ruff check src/ tests/ notebooks/
All checks passed!
$ git rev-list --count --first-parent main
15  (= 9 phases + 6 review-fix commits)
```

The 92-test count is unchanged from `pilot-v0.1` — these are
documentation-only fixes.

## Cross-references

- `pilot-v0.1` tag at `9a0fc76` — the release reference; intentionally
  unchanged.
- Phase 8 lab note — what shipped at the release.
- Phase 5.1 / 4.1 / 3.x lab notes — the established review-driven-fix
  pattern this note continues.
