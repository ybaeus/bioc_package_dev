# TODO - bioc_package_dev

Running task list. See context/plan.md for the full approved plan.

## Build
- [x] Scaffold repo structure + context/ (knowledge/, skills/, agents/, templates/, scripts/, .claude-plugin/)
- [x] Generate knowledge/ chapter summaries (all four parts + appendices)
  - [x] index.md (router / chapter->file map)
  - [x] workflow.md (end-to-end submission runbook)
  - [x] 01-submissions.md (ch 1)
  - [x] development/ (ch 2-23) - 14 files
  - [x] maintenance.md (ch 24-30)
  - [x] reviewer.md (ch 31-33)
  - [x] appendices.md (A-H)
- [x] Cross-tool adapters: AGENTS.md, GEMINI.md, CLAUDE.md
- [x] Claude Code plugin: .claude-plugin/plugin.json, marketplace.json, skills/.../SKILL.md, agents/bioc-package-review.md
- [x] templates/ (DESCRIPTION, NEWS.md, .Rbuildignore, .gitignore, inst/CITATION)
- [x] scripts/check-submission.R
- [x] README.md

## Verify
- [x] claude plugin validate - passed (after adding marketplace description)
- [x] claude --plugin-dir . load test - skill + agent both discovered
- [x] link check: all 44 knowledge/ chapter URLs resolve 200 (curl needs -k locally; no CA bundle)
- [x] skill trigger smoke test - "get my package ready for Bioconductor" surfaced skill, returned gate + version rule
- [x] script smoke test - check-submission.R ran against a dummy package (R 4.4.0), clean pass report, degrades without BiocCheck
- [ ] agent smoke test against a real package - deferred (needs a real package + BiocCheck)
- [x] cross-tool AGENTS.md self-contained (router + gate + version + links)

## Maintenance
- [x] knowledge/SOURCES.md - slug->file map + pinned pkgrevdocs commit (9b078ea, 2026-07-20)
- [x] context/REFRESH.md - drift-detection + regen runbook
- Refresh trigger: each Bioc release (~April/October) or when pkgrevdocs default branch moves

## Not yet done (optional / future)
- [ ] git add + commit + push to github.com/ybaeus/bioc_package_dev (not committed yet)
- [ ] Install BiocCheck to exercise the full dynamic gate
- [ ] Community-marketplace submission (claude plugin validate + review pipeline)

## Confirmed facts
- GitHub repo: ybaeus/bioc_package_dev (install: /plugin marketplace add ybaeus/bioc_package_dev)
- Submission tracker: github.com/Bioconductor/Contributions (open issue, package name as title)
- This repo LICENSE: Apache-2.0
- pkgrevdocs license: NOASSERTION (no standard license declared) - attribute by link, do not claim a license
- Node at /opt/homebrew/bin; broken CURL_CA_BUNDLE - use env -u CURL_CA_BUNDLE
- claude CLI at /opt/homebrew/bin/claude

## Deferred
- Community-marketplace submission (claude plugin validate + review pipeline)
- skill-creator eval / description tuning
- Future: R->Python Bioconductor package converter
