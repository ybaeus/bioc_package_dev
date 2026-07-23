# End-to-end submission runbook

The sequential path from local package to first Bioconductor release. The per-chapter files
under this directory are reference; this file is the process. Follow it top to bottom.

## Phase 0 - Decide it belongs in Bioconductor
- Package addresses high-throughput genomic / biological data analysis.
- Reuses standard Bioconductor data structures (e.g. SummarizedExperiment, S4) where possible.
  See `development/methods-classes.md`.
- Not already on CRAN; CRAN/Bioc-only dependencies.
- Pick a type: Software, Experiment Data, Annotation, or Workflow. See `01-submissions.md`.

## Phase 1 - Build to the gate (before you submit)
Author against the development chapters, then clear every item below. Detail:
`development/build-check-bioccheck.md`, `development/general-dev.md`, `development/metadata-files.md`.

Hard gate (all required):
- `Version: 0.99.0` in DESCRIPTION. See `maintenance.md` (version rule) and metadata-files.
- `biocViews` field present and valid; a vignette; man pages for exported objects.
- Valid maintainer email; maintainer == the person who will submit.
- `R CMD check` clean on current R-devel (no errors, no warnings).
- `BiocCheck::BiocCheckGitClone()` clean.
- `BiocCheck::BiocCheck('new-package'=TRUE)` clean (no errors, no warnings).
- Source build < 10 MB (`R CMD build`); `R CMD check --no-build-vignettes` < 10 min.
- Every individual file <= 5 MB; running vignettes/examples/tests uses < 8 GB memory.
- Bioc code style in R code: `<-`, 4-space indent, 80-col. See `development/r-code.md`.

Use the current devel Bioconductor with the matching R version - see `appendices.md` (Appendix A)
and `development/general-dev.md`. Optional helper: `scripts/check-submission.R` runs the checks.

## Phase 2 - Host on GitHub
- Push the package to the DEFAULT branch of a public GitHub repository (not a subdirectory,
  not a non-default branch).
- Confirm `.gitignore` excludes build artifacts. See `development/gitignore.md`.

## Phase 3 - Submit to the tracker
- Open a new issue at https://github.com/Bioconductor/Contributions/issues/new
- Issue TITLE = the package name. Body = link to your GitHub repo; confirm you have read the
  guidelines and understand the review process.
- Annotation packages are the exception: email packages@bioconductor.org instead.
- Experiment Data that accompanies a software package: add to the same issue; submit the data
  package first if the software depends on it.

## Phase 4 - Single Package Builder (SPB) and review
- A webhook triggers the Single Package Builder; your package must build and check cleanly on
  all platforms. Fix issues, push to GitHub, the build re-runs.
- A reviewer is assigned. Expect 2-6 weeks total. Respond within 2-3 weeks or the issue may be
  closed for inactivity.
- On each change, bump the `z` in the version (0.99.0 -> 0.99.1 -> ...) and push. See
  `maintenance.md` (version rule) and `reviewer.md` for what reviewers check.

## Phase 5 - Acceptance and the Bioconductor git server
Once accepted (detail: `maintenance.md`, ch 24):
- Register your SSH public key at the BiocCredentials app
  (https://git.bioconductor.org/BiocCredentials/). Bioconductor also reads keys from
  https://github.com/<your-id>.keys
- Add the Bioconductor remote and keep GitHub as origin:
  - `git remote add upstream git@git.bioconductor.org:packages/<PKG>.git`
  - `git remote -v` should show origin (GitHub) and upstream (git.bioconductor.org)
- Sync then push to BOTH remotes:
  - `git fetch --all`
  - `git merge upstream/devel` (resolve conflicts if any)
  - `git push upstream devel` (triggers the daily build, ~24h) and `git push origin devel`
- Only `devel` and the current `RELEASE_x_y` branches accept pushes. You cannot create new
  branches on the Bioconductor server. Backport fixes with `git cherry-pick` onto the release
  branch, then push that branch.

## Phase 6 - Release and ongoing maintenance
- Bioconductor releases twice a year (around April and October). At the first release your
  `0.99.z` becomes `1.0.0`. Devel and release version parity: `y` odd in devel, even in release.
- Monitor the daily/weekly build reports and fix breakages promptly. See `maintenance.md`
  (troubleshooting build report, debugging C/C++).
- Subscribe to the bioc-devel mailing list; create a support.bioconductor.org account and watch
  your package tag; keep the maintainer email in DESCRIPTION current.
- Deprecate/retire APIs per the lifecycle rules (`.Deprecated` -> `.Defunct` -> removed). See
  `maintenance.md` (deprecation, end-of-life).

Source: https://contributions.bioconductor.org/bioconductor-package-submissions.html,
https://contributions.bioconductor.org/git-version-control.html,
https://contributions.bioconductor.org/versionnum.html
Fetched 2026-07-23 from contributions.bioconductor.org (Bioconductor devel guide).
