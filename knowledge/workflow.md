# End-to-end submission runbook

The sequential path from local package to first Bioconductor release. The per-chapter files
under this directory are reference; this file is the process. Follow it top to bottom.

## Converting an existing package (start here if code already exists)

Most submitters are not starting from an empty directory - they have a working package or tool on
GitHub. Do not scaffold from scratch. Work the list below in order; it is ordered by how expensive
the problem is to discover late, not by how hard it is to fix.

1. **Eligibility and type** - Phase 0 below. Cheapest to answer and the only one that can end the
   effort entirely.
2. **CRAN status** - "Not exist on CRAN. A package can only be submitted to one or the other."
   Moving from CRAN means leaving CRAN, not dual-listing. Note also that the naming policy says a
   name should not conflict with "any current or past CRAN package"; a maintainer migrating their
   own package should raise that in the submission issue rather than assume it is fine.
3. **Name** - see `development/package-name.md`. Renaming after review has started is painful, and
   the check is a search, not a build.
4. **Version** - reset to `0.99.0` no matter what the package is at today. A package at `2.4.1` on
   GitHub still submits as `0.99.0`. See `maintenance.md`.
5. **Metadata gaps** - `biocViews` (usually missing entirely on a non-Bioc package), `Authors@R`
   with a valid `cre` email, `NEWS.md`, `inst/CITATION`. The `biocthis::use_bioc_*()` chain
   writes these; see the tooling block in `AGENTS.md`. One trap for a conversion:
   `use_bioc_description()` replaces DESCRIPTION rather than merging into it, and declines
   silently when it cannot ask - so on an existing package add `biocViews` by hand.
6. **Reuse audit** - does the package define its own container where `SummarizedExperiment`,
   `GRanges`, or another core class would do? This is the single most common substantive review
   request and the most expensive to retrofit. See `development/methods-classes.md` (ch 5).
7. **Data placement** - anything large moves out of the package to ExperimentHub/AnnotationHub
   before you measure sizes. See `development/data.md`.
8. **Documentation** - a real evaluated vignette, not a stub; man pages with runnable examples.
   Existing packages usually have a README doing the vignette's job. See
   `development/documentation.md`.
9. **Code style** - `<-`, 4-space indent, 80 columns, no `1:n`. Mechanical, so do it last; doing it
   first only creates conflicts with the changes above.
10. **Run the gate** - Phase 1 below, then Phase 2 onward unchanged.

Steps 1-5 are usually a day. Step 6 is where a conversion either goes smoothly or becomes a
rewrite, so check it early even though it is fixed late.

## Phase 0 - Decide it belongs in Bioconductor
- Package addresses high-throughput genomic / biological data analysis.
- Reuses standard Bioconductor data structures (e.g. SummarizedExperiment, S4) where possible.
  See `development/methods-classes.md`.
- Not already on CRAN; CRAN/Bioc-only dependencies.
- Pick a type: Software, Experiment Data, Annotation, or Workflow. See `01-submissions.md`.

## Phase 1 - Build to the gate (before you submit)
Author against the development chapters, then clear every item below. Detail:
`development/build-check-bioccheck.md`, `development/general-dev.md`, `development/metadata-files.md`.

Tier 1 - stated as requirements:
- `R CMD check` clean on current R-devel (no errors, no warnings).
- `BiocCheck::BiocCheckGitClone()` clean.
- `BiocCheck::BiocCheck('new-package' = TRUE)` clean (no errors, no warnings). The tracker calls
  passing check and BiocCheck "a minimum requirement for package acceptance", and notes that
  passing "does not result in automatic acceptance" - review still follows.
- Every individual file <= 5 MB (upstream: "must be").
- `biocViews` field present and valid; a vignette; man pages for exported objects.
- Valid maintainer email; maintainer == the person who will submit.

Tier 2 - stated as should or recommended. Expected in practice and a reviewer will ask, but a
miss here is not a blocker:
- `Version: 0.99.0` in DESCRIPTION. See `maintenance.md` (version rule) and metadata-files.
- Source build under 10 MB (`R CMD build`); `R CMD check --no-build-vignettes` under 10 min.
- Running vignettes/examples/tests uses under 8 GB memory.
- Bioc code style in R code: `<-`, 4-space indent, 80-col. See `development/r-code.md`.

Use the current devel Bioconductor with the matching R version - see `appendices.md` (Appendix A)
and `development/general-dev.md`. BiocCheck is the authoritative validator for everything above
except the two timing items, which need a real build; see the tooling block in `AGENTS.md`.

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
Fetched 2026-08-14 from contributions.bioconductor.org (Bioconductor devel guide).
