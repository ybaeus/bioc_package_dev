# Plan: Bioconductor Package Development — Cross-Tool Skill + Review Agent

## Context

`bioc_package_dev` is a greenfield repo (only `LICENSE`, `.git`, `SESSION_STATE.md`) meant to
hold reusable AI-assistant tooling for developing Bioconductor packages to the project's
official standards. Knowledge source: the official guide *"Bioconductor Packages: Development,
Maintenance, and Peer Review"* (https://contributions.bioconductor.org), source repo
`Bioconductor/pkgrevdocs`.

Full TOC fetched + verified live this session: **33 numbered chapters + appendices A–H** across
four parts — Submissions (ch 1), Development Guidelines (ch 2–23), Maintenance (ch 24–30),
Reviewer Resources (ch 31–33), Appendix A–H. The real submission workflow (Contributions
tracker issue → Single Package Builder webhook → review → BiocCredentials SSH +
git.bioconductor.org dual remotes → release) and the hard numeric gates were verified from
chapters 1, general(3), versionnum(25), and git-version-control(24).

Intended outcome: a shareable git repo whose Bioconductor knowledge is usable across multiple
AI coding assistants (Claude Code, plus Codex / Cursor / Gemini CLI / Copilot via the AGENTS.md
standard), packaged as a Claude Code plugin for one-command install, with a README so other
researchers can adopt it.

**Decisions (confirmed this session):**
- Build **both** a Skill (inline authoring/lifecycle guidance) **and** an Agent (isolated
  submission-readiness audit).
- pkgrevdocs handled via **curated per-chapter summaries + links to live chapters** — NO
  vendoring, no submodule.
- **Cross-tool** is a goal: one portable knowledge base, thin per-tool adapters.
- Distribute as a **Claude Code plugin + marketplace** in this repo; document self-host install
  now, note community-marketplace submission as a later step.
- Include a **lean** set of templates and **one** check script (rationale below).
- Full-lifecycle scope. Content generated with the **fable** model. No emoji in any docs.

## Architecture: one knowledge base, thin adapters

The chapter summaries + workflow runbook are **plain portable markdown** (`knowledge/`) — the
single source of truth, readable by any tool or human. Each assistant gets a thin adapter that
points into `knowledge/`, so there is no content duplication:

- **AGENTS.md** (repo root) — the cross-tool entrypoint. Read natively by Codex, Cursor, Gemini
  CLI, Copilot, Windsurf, and 20+ others. Carries the lifecycle router + pre-submission gate +
  version rules inline (small), and references `knowledge/` for detail.
- **Claude Code plugin** — `skills/bioconductor-package-dev/SKILL.md` + `agents/…`, wrapping the
  same `knowledge/` via `${CLAUDE_PLUGIN_ROOT}/knowledge`. Distributed via `marketplace.json`.
- **GEMINI.md** and **CLAUDE.md** — one-line files that import AGENTS.md, for tools that prefer
  their own filename (both support imports/references).

## Repo layout

```
bioc_package_dev/
├── README.md                         # what it is + per-tool install/usage (NEW)
├── AGENTS.md                         # cross-tool entrypoint (Codex/Cursor/Gemini/Copilot) (NEW)
├── GEMINI.md                         # one-line import of AGENTS.md (NEW)
├── CLAUDE.md                         # one-line import of AGENTS.md (NEW)
├── LICENSE                           # existing
├── context/                          # working docs, not shipped tooling (NEW)
│   ├── SESSION_STATE.md              # moved from repo root
│   ├── plan.md                       # copy of this plan for repo-local reference
│   └── TODO.md                       # running task list
├── knowledge/                        # SINGLE SOURCE OF TRUTH — portable markdown (NEW)
│   ├── index.md                      # router/TOC across all summaries (chapter→file map)
│   ├── workflow.md                   # END-TO-END submission runbook (stitches the process)
│   ├── 01-submissions.md             # ch 1 (+ submission-overview)
│   ├── development/
│   │   ├── package-name.md           # ch 2
│   │   ├── general-dev.md            # ch 3–4
│   │   ├── methods-classes.md        # ch 5
│   │   ├── metadata-files.md         # ch 6–12 (README/DESCRIPTION/NAMESPACE/NEWS/
│   │   │                             #   LICENSE/CITATION/INSTALL)
│   │   ├── documentation.md          # ch 13
│   │   ├── data.md                   # ch 14
│   │   ├── tests.md                  # ch 15
│   │   ├── r-code.md                 # ch 16
│   │   ├── compiled-thirdparty.md    # ch 17
│   │   ├── shiny.md                  # ch 18
│   │   ├── ai-policy.md              # ch 19
│   │   ├── non-software-pkgs.md      # ch 20
│   │   ├── gitignore.md              # ch 21
│   │   └── build-check-bioccheck.md  # ch 22–23
│   ├── maintenance.md                # ch 24–30
│   ├── reviewer.md                   # ch 31–33
│   └── appendices.md                 # A–H
├── templates/                        # lean scaffolding skeletons (NEW, optional)
│   ├── DESCRIPTION
│   ├── NEWS.md
│   ├── .Rbuildignore
│   ├── .gitignore
│   └── inst/CITATION
├── scripts/                          # one check runner (NEW, optional)
│   └── check-submission.R            # R CMD check + BiocCheck, pass/fail vs the gate
├── .claude-plugin/
│   ├── plugin.json                   # plugin manifest (name, version, author)
│   └── marketplace.json              # marketplace listing for /plugin install
├── skills/
│   └── bioconductor-package-dev/
│       └── SKILL.md                  # thin: router + gate; points at ${CLAUDE_PLUGIN_ROOT}/knowledge
└── agents/
    └── bioc-package-review.md        # submission-readiness audit subagent (model: fable)
```

Note: plugin component dirs (`skills/`, `agents/`) live at **repo root**, NOT inside a
`.claude/` dir — the plugin root is this repo, and only `plugin.json` goes inside
`.claude-plugin/`. Grouping thin chapters per file (metadata ch 6–12, maintenance ch 24–30)
keeps `knowledge/` navigable while preserving progressive disclosure.

`workflow.md` is the sequential publish runbook — added because per-chapter summaries are
reference, not process. It stitches the real developer path end to end: pre-submission gate →
host on GitHub default branch → open issue on the Contributions tracker → SPB (Single Package
Builder) webhook build must pass all platforms → reviewer iteration (bump z each commit, 2–6
weeks) → acceptance → register SSH key at BiocCredentials, add `upstream` git.bioconductor.org
remote, dual-remote push → devel vs `RELEASE_x_y` branches (cherry-pick to backport) → ongoing
maintenance. Sources: ch1, ch24, ch25, appendix A.

## Verified chapter → slug map (for summary generation)

Fetch each from `https://contributions.bioconductor.org/<slug>`:

- Submissions: submission-overview, bioconductor-package-submissions (ch1)
- Development: develop-overview, package-name(2), general(3),
  important-bioconductor-package-development-features(4), reusebioc(5), readme(6),
  description(7), namespace(8), news(9), license(10), citation(11), sysdep(12), docs(13),
  data(14), tests(15), r-code(16), other-than-Rcode(17), shiny(18),
  ai-policy-third-party(19), non-software(20), gitignore(21), build-check-bioccheck(22),
  conclusion(23)
- Maintenance: package-maintenance, git-version-control(24), versionnum(25),
  troubleshooting-build-report(26), debugging-cc-code(27), deprecation(28),
  package-end-of-life-policy(29), branch-rename-faqs(30)
- Reviewer: reviewer-resources-overview, review-expectation(31), reviewtools(32),
  review-volunteer-chapter(33)
- Appendix: use-devel(A), advanced-build-options(B), querying-web-resources(C),
  c-fortran(D), cmavericks-best-practices(E), man-links(F), booknews(G), references-1(H)

## Content generation

Fetch + summarize with **fable**-model subagents in parallel, one batch per part. Each summary
is **task-oriented** (actionable rules, required/forbidden patterns, naming/version
conventions), NOT a transcription. Aim ~40–120 lines each. Every summary ends with a link to
its canonical chapter URL **and a "guide version / fetched" stamp** (staleness marker; refresh
bumps plugin `version`). Network note: prefix curl-based fetches with `env -u CURL_CA_BUNDLE`
(broken cert env var); Node at `/opt/homebrew/bin` if needed. Verify the live submission-tracker
repo name at build time — confirm `github.com/Bioconductor/Contributions` before hard-coding it.

## Cross-cutting rules (shared by AGENTS.md and SKILL.md)

Both entrypoints carry these inline (short); detail lives in `knowledge/`:
- **Pre-submission gate** (hard numbers): `R CMD check` clean on R-devel;
  `BiocCheck::BiocCheckGitClone()` + `BiocCheck::BiocCheck('new-package'=TRUE)` clean; source
  build < 10 MB; `R CMD check --no-build-vignettes` < 10 min; individual files <= 5 MB; < 8 GB
  memory; `Version: 0.99.0`; hosted on GitHub default branch; not on CRAN; `biocViews` +
  vignette + man pages present; valid maintainer email.
- **Version rule** (named): start `0.99.0`; `y` odd = devel / even = release (max 99); bump `z`
  every commit; `0.99.z` becomes `1.0.0` at first Bioc release.
- **Bioc code style**: `<-` assignment, 4-space indent, 80-col; contrast with tidyverse.

## SKILL.md design (Claude Code)

- **Frontmatter `description`**: pushy triggering — fire on Bioconductor/Bioc package work,
  `DESCRIPTION`/`NAMESPACE`/`NEWS`/BiocCheck/biocViews, submission prep, S4 /
  `SummarizedExperiment`-style classes, even when "Bioconductor" isn't said explicitly.
- **Body**: short lifecycle router (Authoring → Maintenance → Submission/Review) mapping the
  task to the right `knowledge/` file, plus the cross-cutting rules above. Detail stays in
  `knowledge/`, referenced via `${CLAUDE_PLUGIN_ROOT}/knowledge`.

## Review agent design (`agents/bioc-package-review.md`)

- Frontmatter: `name`, `description` (triggers on "audit/review my package for Bioconductor
  submission"), `model: fable`, read-mostly toolset (Read/Grep/Glob/Bash).
- Behavior: audit against the **explicit pre-submission gate** above, plus the broader checklist
  from `knowledge/reviewer.md` + development chapters. Optionally invoke `scripts/check-submission.R`
  when R is available. Return a structured report (blockers / warnings / suggestions) each mapped
  to a specific guide chapter. Uses `knowledge/` as its base (no duplicated content).

## Templates and scripts (lean, optional)

- `templates/` — small curated skeletons (DESCRIPTION, NEWS.md, .Rbuildignore, .gitignore,
  inst/CITATION). README points to **`biocthis`** for full scaffolding rather than reinventing
  it. Rationale: high scaffolding value, plain files any tool/human copies, low churn.
- `scripts/check-submission.R` — one runner: `R CMD check` + `BiocCheck::BiocCheck()` then
  report pass/fail against the gate. Requires R + BiocCheck installed (documented). Skip a
  version-bump helper (trivial; `usethis`/manual). Rationale: operationalizes the gate we
  emphasize without a maintenance-heavy toolchain.

## Distribution (`.claude-plugin/` + README)

- `plugin.json`: `name` = `bioconductor-package-dev`, `description`, explicit `version` (so
  users only pull updates on a bump), `author`, `repository`, `license`.
- `marketplace.json`: lists this plugin so users run
  `/plugin marketplace add <owner>/bioc_package_dev` then `/plugin install`.
- Self-host now; note `claude plugin validate` + community-marketplace submission as a later
  step. Need the GitHub `<owner>/<repo>` to hard-code the install command (confirm at build).

## README.md

Repo-root README: one-line statement of what this repo is for; the repo layout tree;
prerequisites (R, Bioc-devel, `BiocManager`, `BiocCheck`, optional `biocthis`); **per-tool
install/usage** —
- Claude Code: `/plugin marketplace add <owner>/bioc_package_dev` → `/plugin install`; or clone
  and `--plugin-dir`.
- Codex / Cursor / Gemini CLI / Copilot: clone and rely on `AGENTS.md` (Gemini also `GEMINI.md`).
- Manual fallback: copy `knowledge/` and point any tool at it.
—plus a refresh/versioning note, and attribution + license for pkgrevdocs (verify its license
at build; likely CC-BY). Plain text, no emoji.

## Verification

1. **Structure**: `.claude-plugin/plugin.json`, `skills/bioconductor-package-dev/SKILL.md`,
   `agents/bioc-package-review.md`, `AGENTS.md`, and `knowledge/*` exist and parse (valid YAML
   frontmatter, valid JSON manifests, no broken internal links). Run `claude plugin validate`.
2. **Link check**: every canonical chapter URL in `knowledge/` resolves (HTTP 200).
3. **Claude Code load test**: `claude --plugin-dir .` loads the plugin; skill appears as
   `/bioconductor-package-dev:…` and the agent under Custom Agents.
4. **Skill trigger smoke test**: "help me get my R package ready for Bioconductor submission"
   surfaces the skill; "write my DESCRIPTION for a Bioc package" routes to
   `knowledge/development/metadata-files.md`.
5. **Cross-tool check**: confirm `AGENTS.md` is valid and self-contained enough that a
   non-Claude tool pointed at the repo gets the router + gate + links.
6. **Agent smoke test**: invoke `bioc-package-review` against a minimal dummy package skeleton;
   confirm a structured report referencing guide chapters.
7. Optional later: skill-creator eval loop to tune the SKILL `description` for reliable
   triggering.

## Deferred

- Community-marketplace submission (`claude plugin validate` + review pipeline).
- Skill-creator formal eval + description-optimization loop.
- Future idea (separate project): R→Python Bioconductor package converter.

## References (verified this session)

Bioconductor guide (canonical knowledge source):
- Guide home + TOC: https://contributions.bioconductor.org/index.html
- Submissions ch1: https://contributions.bioconductor.org/bioconductor-package-submissions.html
- General requirements / gate: https://contributions.bioconductor.org/general.html
- Version numbering: https://contributions.bioconductor.org/versionnum.html
- Git workflow (dual remotes, BiocCredentials): https://contributions.bioconductor.org/git-version-control.html
- Source repo: https://github.com/Bioconductor/pkgrevdocs

Cross-tool distribution basis:
- Claude Code plugins: https://code.claude.com/docs/en/plugins
- Claude Code skills: https://code.claude.com/docs/en/skills
- AGENTS.md standard (2026 guide): https://codersera.com/blog/agents-md-complete-guide-2026/
- CLAUDE.md vs AGENTS.md vs GEMINI.md: https://inventivehq.com/blog/claude-md-vs-agents-md-vs-gemini-md
- Gemini CLI GEMINI.md docs: https://geminicli.com/docs/cli/gemini-md/
