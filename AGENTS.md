# Bioconductor package development - agent instructions

Cross-tool entrypoint (read natively by Codex, Cursor, Gemini CLI, Copilot, and others). When
the task involves developing, maintaining, submitting, or reviewing a Bioconductor package,
follow the rules here and open the matching file under `knowledge/` for detail. The `knowledge/`
directory is the single source of truth; this file is a short router over it.

## When this applies
Any work on: an R package intended for Bioconductor; `DESCRIPTION` / `NAMESPACE` / `NEWS` /
`biocViews` / `BiocCheck`; S4 or Bioconductor core classes (e.g. SummarizedExperiment);
vignettes and man pages for a Bioc package; submission to the Bioconductor Contributions
tracker; the Bioconductor git server (git.bioconductor.org). It applies even when the user does
not say "Bioconductor" explicitly but the package clearly targets it.

## Router
- Full submission path, start to finish: `knowledge/workflow.md`
- Topic map across all chapters: `knowledge/index.md`
- Submission mechanics + package types: `knowledge/01-submissions.md`
- Authoring topics (naming, metadata, docs, data, tests, R code, compiled code, shiny, etc.):
  `knowledge/development/`
- Maintenance (git server, versioning, build reports, deprecation): `knowledge/maintenance.md`
- What reviewers check: `knowledge/reviewer.md`
- Appendices (devel Bioc, build options, C/Fortran, etc.): `knowledge/appendices.md`

## Pre-submission gate (hard requirements for a new package)
Do not tell a user their package is submission-ready unless all hold:
- `R CMD check` clean on current R-devel (no errors, no warnings).
- `BiocCheck::BiocCheckGitClone()` and `BiocCheck::BiocCheck('new-package'=TRUE)` clean.
- Source build < 10 MB; `R CMD check --no-build-vignettes` < 10 min; individual files <= 5 MB;
  < 8 GB memory for vignettes/examples/tests.
- `Version: 0.99.0`; `biocViews` present; a vignette and man pages present; valid maintainer
  email; not on CRAN; hosted on the GitHub default branch.
Detail: `knowledge/development/build-check-bioccheck.md` and `knowledge/development/general-dev.md`.

## Version rule
Start `0.99.0`. Scheme `x.y.z`: `y` odd in devel, even in release (max 99); bump `z` by 1 on
every commit; `0.99.z` becomes `1.0.0` at the first Bioconductor release; `x` changed only by
the Bioconductor team. Detail: `knowledge/maintenance.md`.

## Bioconductor code style (differs from tidyverse)
Use `<-` for assignment, 4-space indentation, 80-column lines; prefer vectorized code; avoid
`1:n` (use `seq_len`/`seq_along`). Detail: `knowledge/development/r-code.md`.

## Submitting and the git server (short)
Host on the GitHub default branch, then open an issue (title = package name) at
https://github.com/Bioconductor/Contributions/issues/new (Annotation packages: email
packages@bioconductor.org). The Single Package Builder must pass on all platforms. After
acceptance, register an SSH key at BiocCredentials, add `upstream = git.bioconductor.org`, and
push to both remotes; only `devel` and `RELEASE_x_y` branches accept pushes. Full sequence:
`knowledge/workflow.md`.

## Optional helpers
- `scripts/check-submission.R` runs `R CMD check` + `BiocCheck` and reports pass/fail vs the gate
  (needs R + BiocCheck installed).
- `templates/` holds lean skeletons (DESCRIPTION, NEWS.md, .Rbuildignore, .gitignore,
  inst/CITATION). For full scaffolding, prefer the `biocthis` package.

Canonical guide: https://contributions.bioconductor.org (source: github.com/Bioconductor/pkgrevdocs).
