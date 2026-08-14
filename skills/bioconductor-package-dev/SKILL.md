---
name: bioconductor-package-dev
description: >-
  Guides you through turning an existing R package into a Bioconductor submission - what the
  requirements are, what the pre-submission gate demands, and how peer review works. Use when a
  package on GitHub is being prepared for Bioconductor, when moving a package from CRAN to
  Bioconductor, when asked whether a package is submission-ready, and for any Bioconductor
  development, maintenance, or review work: DESCRIPTION/NAMESPACE/NEWS/biocViews/BiocCheck,
  version numbering, vignettes and man pages, large data placement, the Contributions tracker,
  git.bioconductor.org, and S4 or Bioconductor core classes such as SummarizedExperiment - even
  when the user does not say "Bioconductor" explicitly but the package clearly targets it.
---

# Bioconductor package development

Curated from the official guide "Bioconductor Packages: Development, Maintenance, and Peer
Review" (https://contributions.bioconductor.org). The detailed summaries live in
`${CLAUDE_PLUGIN_ROOT}/knowledge/` - open the file for the task instead of loading everything.

The common case is conversion: the user already has a working package or tool on GitHub and wants
it in Bioconductor. Start from what exists and find the gaps against the gate; do not scaffold
from scratch unless there is no package yet.

## How to use this skill
1. Identify the lifecycle stage: Authoring, Conversion/Submission, Maintenance, or Review.
2. Open the matching `knowledge/` file for the rules and exact values. The topic router lives in
   `${CLAUDE_PLUGIN_ROOT}/AGENTS.md` under "Router", and the full map in `knowledge/index.md`.
3. Apply the cross-cutting rules below (gate, version, style) to whatever you write or check.
4. For an end-to-end submission, follow `${CLAUDE_PLUGIN_ROOT}/knowledge/workflow.md`. For an
   existing package, start at its "Converting an existing package" section.

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

## Submission and git server (short)
Host on the GitHub default branch, then open an issue (title = package name) at
https://github.com/Bioconductor/Contributions/issues/new (Annotation packages: email
packages@bioconductor.org). The Single Package Builder must pass on all platforms. After
acceptance: register an SSH key at BiocCredentials, add `upstream = git.bioconductor.org`, push
to both remotes; only `devel` and `RELEASE_x_y` branches accept pushes. Full sequence:
`knowledge/workflow.md`.

For a full submission-readiness audit, use the `bioc-package-review` agent.
