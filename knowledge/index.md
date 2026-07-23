# Bioconductor knowledge base - router

Task-oriented summaries of the official guide "Bioconductor Packages: Development,
Maintenance, and Peer Review" (https://contributions.bioconductor.org). Open the file that
matches the task. Each summary links back to its canonical chapter for the full text.

## Start here
- New to submission, or want the whole path end to end: read `workflow.md` (the runbook).
- Just need one topic: use the map below.

## Lifecycle router

Authoring a package:
- Naming: `development/package-name.md` (ch 2)
- General setup + key features: `development/general-dev.md` (ch 3-4)
- Reusing Bioc classes/methods (SummarizedExperiment, S4, etc.): `development/methods-classes.md` (ch 5)
- Metadata files (README, DESCRIPTION, NAMESPACE, NEWS, LICENSE, CITATION, INSTALL):
  `development/metadata-files.md` (ch 6-12)
- Documentation (vignettes, man pages, roxygen): `development/documentation.md` (ch 13)
- Package data + large data (ExperimentHub/AnnotationHub): `development/data.md` (ch 14)
- Unit tests: `development/tests.md` (ch 15)
- R code + Bioc code style: `development/r-code.md` (ch 16)
- Compiled / third-party code (C/C++/Fortran/Python): `development/compiled-thirdparty.md` (ch 17)
- Shiny apps: `development/shiny.md` (ch 18)
- AI policy + third-party code: `development/ai-policy.md` (ch 19)
- Non-software packages (ExperimentData/Annotation/Workflow): `development/non-software-pkgs.md` (ch 20)
- .gitignore: `development/gitignore.md` (ch 21)
- Build / Check / BiocCheck (the gate): `development/build-check-bioccheck.md` (ch 22-23)

Submitting:
- Eligibility, package types, tracker issue, Single Package Builder: `01-submissions.md` (ch 1)
- The full sequence from local build to first release: `workflow.md`

Maintaining (after acceptance):
- Git workflow (BiocCredentials, git.bioconductor.org dual remotes), version numbering,
  build-report troubleshooting, deprecation, end of life, branch rename: `maintenance.md` (ch 24-30)

Reviewing (and what reviewers check):
- Review expectations, reviewer tools, volunteering: `reviewer.md` (ch 31-33)

Appendices:
- Using devel Bioconductor, advanced build options, querying web resources, C/Fortran, Mavericks,
  Rd links, NEWS, references: `appendices.md` (A-H)

## The gate (memorize)
See `workflow.md` and `development/build-check-bioccheck.md` for detail. A new package must:
- Pass `R CMD check` clean on current R-devel (no errors, no warnings).
- Pass `BiocCheck::BiocCheckGitClone()` and `BiocCheck::BiocCheck('new-package'=TRUE)` clean.
- Source build < 10 MB; `R CMD check --no-build-vignettes` < 10 min; individual files <= 5 MB;
  < 8 GB memory to run vignettes/examples/tests.
- Set `Version: 0.99.0`; include `biocViews`, a vignette, and man pages; valid maintainer email;
  not already on CRAN; hosted on the GitHub default branch.

Source: https://contributions.bioconductor.org/index.html
Fetched 2026-07-23 from contributions.bioconductor.org (Bioconductor devel guide).
