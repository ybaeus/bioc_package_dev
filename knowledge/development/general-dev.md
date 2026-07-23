# General Development Requirements

Covers: Chapter 3 - General guidelines, and Chapter 4 - Important Bioconductor
package development features.

## Development environment
- Develop against the devel version of Bioconductor and use devel Bioconductor
  packages.
- Use a recent R-devel matching the current Bioconductor devel branch.

## Pre-submission gate (build and check)
- Must pass `R CMD build` and `R CMD check` with NO errors and NO warnings on
  recent R-devel.
- Must pass `BiocCheck::BiocCheckGitClone()` with no errors/warnings.
- Must pass `BiocCheck::BiocCheck('new-package' = TRUE)` with no errors/warnings.
- All ERRORs, WARNINGs, and NOTEs must be addressed or explicitly justified.

## Hard numeric thresholds
- Source package produced by `R CMD build`: **< 10 MB**.
- Individual files (software packages): **<= 5 MB** each.
- `R CMD check --no-build-vignettes` runtime: **< 10 minutes**.
- Memory usage across vignettes, examples, and tests: **< 8 GB**.
- Use lossy compression (e.g., pngquant) to shrink large images/screenshots.

## File hygiene
- Do not include filenames that differ only in case (cross-platform safety).
- Exclude unnecessary files: `.DS_Store`, `.project`, `.git`, cache files, logs,
  `*.Rproj`, `*.so`.
- Use `.gitignore` to keep undesirable files out of the repository.
- Keep application-specific tooling (GitHub Actions, devtools config) on separate
  branches, not in the submitted package.
- R CMD check options are customized by Bioconductor via flags configurable
  through the `R_CHECK_ENVIRON` environment variable.

## biocViews (required feature)
- The DESCRIPTION file MUST contain a `biocViews:` field (case-sensitive,
  lowercase 'b').
- Choose terms from only ONE category: Software, Annotation Data, Experiment Data,
  or Workflow.
- Use leaf-level terms rather than broad parent categories.
- Terms must match the official hierarchy exactly (spelling and capitalization);
  consult the devel branch biocViews list.
- Submission validation checks that biocViews are present, valid, and from a
  single category.

## Vignettes (required feature)
- Every submitted package must have at least one Rmd (preferred) or Rnw vignette.
- Render with `BiocStyle::html_document`.
- Vignettes must contain evaluated (non-trivial, runnable) R code.
- Include a detailed introduction motivating inclusion in Bioconductor and, where
  relevant, compare against existing similar packages.

## Reuse existing infrastructure
- Reuse established Bioconductor classes and methods where appropriate (see the
  Common Bioconductor Methods and Classes guidance / methods-classes.md).

Source: https://contributions.bioconductor.org/general.html and
https://contributions.bioconductor.org/important-bioconductor-package-development-features.html
Fetched 2026-07-23 from contributions.bioconductor.org (Bioconductor devel guide).
