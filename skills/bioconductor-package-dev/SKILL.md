---
name: bioconductor-package-dev
description: >-
  Use when developing, maintaining, submitting, or reviewing a Bioconductor R package. Fires on
  Bioconductor/Bioc package work, DESCRIPTION/NAMESPACE/NEWS/biocViews/BiocCheck, submission prep,
  the Bioconductor Contributions tracker or git.bioconductor.org, and S4 or Bioconductor core
  classes such as SummarizedExperiment - even when the user does not say "Bioconductor" explicitly
  but the package clearly targets it. Provides the official contribution rules, the pre-submission
  gate, version numbering, and a topic router into curated per-chapter summaries.
---

# Bioconductor package development

Curated from the official guide "Bioconductor Packages: Development, Maintenance, and Peer
Review" (https://contributions.bioconductor.org). The detailed summaries live in
`${CLAUDE_PLUGIN_ROOT}/knowledge/` - open the file for the task instead of loading everything.

## How to use this skill
1. Identify the lifecycle stage: Authoring, Submission, Maintenance, or Review.
2. Open the matching `knowledge/` file (map below) for the rules and exact values.
3. Apply the cross-cutting rules here (gate, version, style) to whatever you write or check.
4. For an end-to-end submission, follow `${CLAUDE_PLUGIN_ROOT}/knowledge/workflow.md`.

## Router (open the file that matches the task)
- Whole submission path, start to finish: `knowledge/workflow.md`
- Full topic map: `knowledge/index.md`
- Submission mechanics + package types: `knowledge/01-submissions.md`
- Naming: `knowledge/development/package-name.md`
- General dev + key features: `knowledge/development/general-dev.md`
- Reusing Bioc classes/methods (S4, SummarizedExperiment): `knowledge/development/methods-classes.md`
- Metadata files (README/DESCRIPTION/NAMESPACE/NEWS/LICENSE/CITATION/INSTALL):
  `knowledge/development/metadata-files.md`
- Documentation (vignettes, man pages): `knowledge/development/documentation.md`
- Package data + large data: `knowledge/development/data.md`
- Unit tests: `knowledge/development/tests.md`
- R code + code style: `knowledge/development/r-code.md`
- Compiled / third-party code: `knowledge/development/compiled-thirdparty.md`
- Shiny: `knowledge/development/shiny.md`
- AI policy + third-party code: `knowledge/development/ai-policy.md`
- Non-software packages: `knowledge/development/non-software-pkgs.md`
- .gitignore: `knowledge/development/gitignore.md`
- Build / Check / BiocCheck (the gate): `knowledge/development/build-check-bioccheck.md`
- Maintenance (git server, versioning, build reports, deprecation): `knowledge/maintenance.md`
- What reviewers check: `knowledge/reviewer.md`
- Appendices (devel Bioc, build options, C/Fortran, etc.): `knowledge/appendices.md`

## Cross-cutting rules (apply always)

Pre-submission gate - a new package is NOT submission-ready unless all hold:
- `R CMD check` clean on current R-devel (no errors, no warnings).
- `BiocCheck::BiocCheckGitClone()` and `BiocCheck::BiocCheck('new-package'=TRUE)` clean.
- Source build < 10 MB; `R CMD check --no-build-vignettes` < 10 min; individual files <= 5 MB;
  < 8 GB memory for vignettes/examples/tests.
- `Version: 0.99.0`; `biocViews` present; a vignette and man pages present; valid maintainer
  email; not on CRAN; hosted on the GitHub default branch.

Version rule: start `0.99.0`; in `x.y.z`, `y` is odd in devel / even in release (max 99); bump
`z` by 1 every commit; `0.99.z` becomes `1.0.0` at the first Bioconductor release; `x` changed
only by the Bioconductor team.

Bioconductor code style (differs from tidyverse): `<-` assignment, 4-space indent, 80-column
lines; prefer vectorized code; avoid `1:n` (use `seq_len`/`seq_along`).

## Submission and git server (short)
Host on the GitHub default branch, then open an issue (title = package name) at
https://github.com/Bioconductor/Contributions/issues/new (Annotation packages: email
packages@bioconductor.org). The Single Package Builder must pass on all platforms. After
acceptance: register an SSH key at BiocCredentials, add `upstream = git.bioconductor.org`, push
to both remotes; only `devel` and `RELEASE_x_y` branches accept pushes. Full sequence:
`knowledge/workflow.md`.

## Optional helpers (in this plugin)
- `${CLAUDE_PLUGIN_ROOT}/scripts/check-submission.R` - runs `R CMD check` + `BiocCheck` and
  reports pass/fail vs the gate (needs R + BiocCheck installed).
- `${CLAUDE_PLUGIN_ROOT}/templates/` - lean skeletons (DESCRIPTION, NEWS.md, .Rbuildignore,
  .gitignore, inst/CITATION). For full scaffolding, prefer the `biocthis` package.

For a full submission-readiness audit, use the `bioc-package-review` agent.
