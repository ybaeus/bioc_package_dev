# Improvement backlog

Gaps found by using the skill on real work, not by reading it. Sorted by how the fix ships, because
that is what decides sequencing: half of this repository is a mirror and cannot be edited here.

## The two tracks

**Track A ships from this repository.** `AGENTS.md`, `agents/bioc-package-review.md`, `README.md`,
`scripts/`, `evals/`, `docs/`. Commit and push; users get it on the next plugin bump.

**Track B needs an upstream pull request first.** Anything under `skills/bioc-pkg-dev/` -
`SKILL.md` and all of `knowledge/`. Fix it in a branch of
[bioconductor/ai-agent-skills](https://github.com/Bioconductor/ai-agent-skills), restamping
`Fetched` in the same commit, open the PR there, then `rsync -a --delete` back and run
`scripts/verify.py`. Editing the copy here is how the two silently diverge; see "The mirror rule"
in `REFRESH.md`.

One trap when sorting work into these tracks. `verify.py` keeps two different lists:

- `ROUTER_FILES` and `ROUTER_SECTIONS` are repo-native only. `SKILL.md` was deliberately removed
  from `ROUTER_FILES`, because upstream's layout has no `## Tooling` section and demanding one
  would force the copies apart. So the tooling block and the `AGENTS.md` sections are Track A.
- `GATE_FILES` still includes `skills/bioc-pkg-dev/SKILL.md` and `knowledge/workflow.md`. Every
  file in it must carry every string in `GATE_VALUES`. **Adding a gate number is therefore Track
  B even if you only intended to touch `AGENTS.md`** - the check will fail on two mirrored files
  you cannot edit.

## Track A - ships now

### A1. Teach the review agent the rename surface

Highest value per unit of work in this list, and it needs no upstream PR.

The C registration entry point `R_init_<pkg>` must match the `Package:` field or every `.Call`
breaks at load. Invisible to static review, loud at runtime. Add to
`agents/bioc-package-review.md` as a concrete check: compare `R_init_*` in `src/` and `useDynLib`
in `NAMESPACE` against `Package:` in `DESCRIPTION`, and report a mismatch as a blocker.

Same check should cover the rest of the surface a rename touches, which in the apeBioc run was 19
sites: man page `\alias{}` and `\name{}`, vignette filenames and `%\VignetteIndexEntry{}`,
`inst/CITATION`, test fixtures, `::`-qualified self-references.

### A2. Say that a BiocCheck finding can be wrong

`checkSingleColon` fired on correct code. Resolving it meant reading BiocCheck's source. The
guidance treats BiocCheck as authoritative, which is right, but should add that the function
implementing each check is readable and is the tiebreaker - the same technique already used to
establish the 80% example rule.

Goes in the tooling block, which lives in `AGENTS.md` and `agents/bioc-package-review.md`.
`verify.py` requires those two identical, so change both in one commit. Track A because
`ROUTER_FILES` excludes the mirror.

### A3. Name the fork case in "When this applies"

`AGENTS.md` currently describes work on a package you are building. One line naming the adopted or
forked package brings the router in line with Track B below, and does not depend on it landing.

Do not add a gate number here without reading the `GATE_FILES` trap above.

### A4. Evals for A1-A3

Each of the above is a behavioral claim, so it needs a case in `evals/`. A1 in particular is worth
a fixture: a package whose `R_init_` prefix does not match `DESCRIPTION`.

## Track B - needs an upstream PR

### B1. A fork chapter (items formerly 1, 2, 3, 6)

These share one root cause and should be one PR, not four. The skill assumes a package being
**created**; the harder real case is a package being **adopted** - live, already shipping, with
users and dependents.

- **Adoption path.** `knowledge/workflow.md` has "Converting existing work", but it assumes your
  own code. Nothing covers taking over a package that already exists elsewhere: who the maintainer
  becomes, what happens to the original's users, whether to fork at all.
- **Rename surface.** `knowledge/development/package-name.md` never mentions the C symbol prefix.
  Needs the A1 checklist in prose form. Also worth stating: use anchored or guarded replacement,
  not a global `sed`. In this run a blanket substitution rewrote substrings inside unrelated
  identifiers and URLs.
- **Ecosystem interop.** Downstream packages import the original name, and the fork's S3 methods
  collide with the original's when both are loaded (hit with `phangorn`). The skill flags "reuse
  existing infrastructure" as a review criterion but says nothing about the case where your package
  *is* what others already depend on. Unresolved, and the hardest item here.
- **Behavioral equivalence.** What made this fork defensible rather than merely compliant was
  proving it computes what upstream computes: test parity against the original, output diffing, a
  frozen reference. Came entirely from a hand-written plan.
  `knowledge/development/tests.md` covers writing tests for new code, not proving a port faithful.

### B2. Authorship you do not own

33 upstream authors, none of them the submitter. `Authors@R` roles (`aut` / `cre` / `ctb`), what
the maintainer-email requirement means when you are not the author, how the AI-disclosure policy
interacts with derived work, whether upstream consent is expected before submitting a fork.

`knowledge/development/metadata-files.md` covers `Authors@R` mechanically only. Small and
self-contained - separate PR from B1, lands faster.

### B3. BiocCheck fallibility, in the knowledge file

The prose half of A2, in `knowledge/development/build-check-bioccheck.md`. Independent of B1 and
B2; smallest upstream PR of the three.

## Out of scope - decided, not deferred

Cluster and HPC specifics (module systems, containers, partitions, quota) were most of the
session's real difficulty and belong nowhere near this skill. Bioconductor guidance is
environment-neutral and should stay that way. Recorded so it is not rediscovered as a gap.

## Do not regress these

Verified useful in the same run, all things that would otherwise have been guessed wrong:

- `biocViews` absent is an ERROR, and a top-level term alone is also an ERROR.
- Package name must equal the repository name, case-sensitive, no underscores. Caught before
  submission rather than after.
- Reset to `0.99.0` regardless of the upstream version, counterintuitive at 5.8-3.
- Both BiocCheck entry points, not just `BiocCheck()`.
- The biocthis traps: `use_bioc_description()` silently declining on an existing DESCRIPTION, and
  `use_bioc_citation()` writing an `inst/CITATION` that fails `R CMD build`. Negative knowledge -
  it prevented harm rather than suggesting an action.
- The AI-disclosure policy.

## Standing warning

`verify.py` reports one warning: the mirrored `SKILL.md` description drops "existing" and "CRAN",
which is the conversion audience's vocabulary, and the description is the only router in the plugin
build. Measure with `evals/trigger-cran-move` before trusting the skill to fire on "move my CRAN
package". Fixing it is Track B.

## Source

The apeBioc run (2026-08): forking a live CRAN package (`ape` 5.8-3, 33 authors, C code, downstream
dependents) into a Bioconductor submission. The skill's checklist is why the error count reached
zero rather than "probably fine". Everything above is what it did not cover.
