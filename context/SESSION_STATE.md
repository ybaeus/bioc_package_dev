# Session State - bioc_package_dev

Last updated: 2026-07-23

## Goal
Build reusable Claude tooling for Bioconductor package development in this repo:
a Skill (inline authoring/lifecycle guidance) plus a review Agent (submission-readiness
audit), backed by curated summaries of the official guide "Bioconductor Packages:
Development, Maintenance, and Peer Review" (https://contributions.bioconductor.org,
source repo: Bioconductor/pkgrevdocs).

## Accomplished
- Environment prepped:
  - Installed Node 26.5.0 via Homebrew (/opt/homebrew/bin - NOT on default PATH; prepend it
    when running node/npx).
  - Found and worked around a broken CURL_CA_BUNDLE env var (points to a missing enterprise
    cert, causing curl error 77). Prefix network commands with `env -u CURL_CA_BUNDLE`.
    Saved to memory.
- Installed caveman (JuliusBrussee/caveman) as a Claude Code plugin (user scope). Concise-
  output skill. Activates next session via /caveman or "caveman mode"; stats via /caveman-stats.
- Wrote the build plan and handed it to Ultraplan for remote refinement.
  - Local plan file: /Users/ybae/.claude/plans/i-would-like-to-polymorphic-quasar.md
  - Ultraplan session: https://claude.ai/code/session_01GuiAoNksAgYvqYzd14b42h?from=cli

## In progress
- Ultraplan refinement of the build plan - awaiting the refined plan to teleport back for
  approval and implementation.

## Next steps (once plan approved)
1. Scaffold repo layout:
   - .claude/skills/bioconductor-package-dev/SKILL.md plus resources/ (per-chapter summaries
     with links to live chapters; NOT vendoring pkgrevdocs)
   - .claude/agents/bioc-package-review.md (submission-readiness audit; model: fable)
   - Repo-root README.md so others can install and follow.
2. Generate chapter summaries with fable-model subagents (33 chapters plus appendices A-H;
   full lifecycle: Submissions / Development / Maintenance / Reviewer).
3. Verify: structure and frontmatter parse, chapter URLs resolve, skill trigger smoke test,
   agent smoke test against a dummy package skeleton.

## Future idea (post bioc_package_dev)
- R to Python converter Skill or Agent: convert a Bioconductor (R) package to Python
  (e.g. map Bioc classes like SummarizedExperiment / S4 to Python equivalents such as
  AnnData / BiocPy, translate DESCRIPTION to pyproject, roxygen to docstrings, testthat to
  pytest). Skill vs agent to be decided later; separate follow-on project, not part of the
  current build.

## Key facts / gotchas
- Node at /opt/homebrew/bin (prepend to PATH). Broken CURL_CA_BUNDLE - use
  `env -u CURL_CA_BUNDLE`.
- Repo is otherwise greenfield (only LICENSE, .git, plus this file and memory).
- Decisions locked: both skill and agent; summaries plus links (no pkgrevdocs vendoring);
  full lifecycle; content work done with the fable model.
- Doc convention: no emoji in any docs in this repo.
