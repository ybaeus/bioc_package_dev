# Sources and refresh baseline

This file records where each summary came from and the exact upstream state it was generated
against. Use it to detect drift and to refresh only what changed. See `context/REFRESH.md` for
the procedure.

## Upstream baseline (update on every refresh)

- Source repository: https://github.com/Bioconductor/pkgrevdocs
- Default branch: `devel`
- Pinned commit (last summarized from): `9b078ea2a0ec05274be83cb12ea75473c6d0c808`
- Commit date: 2026-07-20
- Summaries fetched: 2026-07-23
- Rendered guide: https://contributions.bioconductor.org

To find the current upstream commit:
`https://api.github.com/repos/Bioconductor/pkgrevdocs/commits/devel` (field `sha`). Compare the
`sha` to the pinned commit above. If they differ, list changed chapter files with the GitHub
compare API: `https://github.com/Bioconductor/pkgrevdocs/compare/<pinned>...devel`

## Chapter slug -> knowledge file map

Every page is `https://contributions.bioconductor.org/<slug>.html`.

Submissions:
- submission-overview, bioconductor-package-submissions (ch1) -> `01-submissions.md`

Development (ch 2-23) -> `development/`:
- package-name (ch2) -> `development/package-name.md`
- general (ch3), important-bioconductor-package-development-features (ch4) -> `development/general-dev.md`
- reusebioc (ch5) -> `development/methods-classes.md`
- readme (ch6), description (ch7), namespace (ch8), news (ch9), license (ch10), citation (ch11),
  sysdep (ch12) -> `development/metadata-files.md`
- docs (ch13) -> `development/documentation.md`
- data (ch14) -> `development/data.md`
- tests (ch15) -> `development/tests.md`
- r-code (ch16) -> `development/r-code.md`
- other-than-Rcode (ch17) -> `development/compiled-thirdparty.md`
- shiny (ch18) -> `development/shiny.md`
- ai-policy-third-party (ch19) -> `development/ai-policy.md`
- non-software (ch20) -> `development/non-software-pkgs.md`
- gitignore (ch21) -> `development/gitignore.md`
- build-check-bioccheck (ch22), conclusion (ch23) -> `development/build-check-bioccheck.md`

Maintenance (ch 24-30) -> `maintenance.md`:
- package-maintenance, git-version-control (ch24), versionnum (ch25),
  troubleshooting-build-report (ch26), debugging-cc-code (ch27), deprecation (ch28),
  package-end-of-life-policy (ch29), branch-rename-faqs (ch30)

Reviewer (ch 31-33) -> `reviewer.md`:
- reviewer-resources-overview, review-expectation (ch31), reviewtools (ch32),
  review-volunteer-chapter (ch33)

Appendices (A-H) -> `appendices.md`:
- use-devel (A), advanced-build-options (B), querying-web-resources (C), c-fortran (D),
  cmavericks-best-practices (E), man-links (F), booknews (G), references-1 (H)

Not chapter-derived (maintain by hand):
- `index.md` (router), `workflow.md` (runbook), this file.
