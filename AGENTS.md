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

## Pre-submission gate
Two tiers, because upstream states them at two different strengths. Do not report a tier-2 item
as a blocker; report it as something a reviewer will very likely ask about.

Tier 1 - stated as requirements:
- `R CMD check` and `BiocCheck` pass with no ERROR and no WARNING on current R-devel. This is the
  tracker's own wording: "a minimum requirement for package acceptance". It also says "Passing
  these checks does not result in automatic acceptance" - a human review follows.
- Run both entry points: `BiocCheck::BiocCheckGitClone()` and
  `BiocCheck::BiocCheck('new-package' = TRUE)`.
- Individual files must be <= 5 MB. Upstream states this one as "must".
- `biocViews` present; a vignette and man pages present; maintainer email valid and belonging to
  the person submitting; not on CRAN ("a package can only be submitted to one or the other");
  hosted on the GitHub default branch. BiocCheck catches most of these.

Tier 2 - stated as should or recommended:
- `Version: 0.99.0` for a new package (upstream: "should set"). Expected in practice; set it.
- Source build under 10 MB (upstream: "should occupy less than").
- `R CMD check --no-build-vignettes` under 10 min (upstream: "should require less than").
- Vignettes, examples and tests under 8 GB memory (upstream: "it is recommended that").

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

## Tooling (use these, do not reimplement them)
This repo ships no validator and no templates on purpose - Bioconductor already maintains both,
and reusing existing infrastructure is itself a review criterion (ch 5).

```r
# Validation - BiocCheck is authoritative
BiocCheck::BiocCheckGitClone()
BiocCheck::BiocCheck('new-package' = TRUE)

# Scaffolding - biocthis writes Bioconductor-shaped files
biocthis::use_bioc_description(biocViews = "Software")
biocthis::use_bioc_news_md()
biocthis::use_bioc_vignette(name = "<pkg>", title = "Introduction to <pkg>")
biocthis::use_bioc_citation()
biocthis::use_bioc_github_action()
```

Install with:

```r
BiocManager::install(c(
    "BiocCheck", "biocthis",
    # use_bioc_vignette() adds these to Suggests and refuses to run unless they are installed
    "BiocStyle", "knitr", "RefManageR", "sessioninfo", "testthat"
))
```

BiocCheck cannot measure the two
timing gate items (`R CMD check --no-build-vignettes` under 10 min, under 8 GB memory) - those
need a real build.

Current cycle: Bioconductor release 3.23, devel 3.24, both on R 4.6.0. Build against devel for a
new submission. Never guess this pair - it changes twice a year, `knowledge/SOURCES.md` records
what was verified and when, and https://bioconductor.org/config.yaml is authoritative.

Canonical guide: https://contributions.bioconductor.org (source: github.com/Bioconductor/pkgrevdocs).
