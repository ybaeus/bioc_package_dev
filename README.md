# bioc_package_dev

Reusable AI-assistant tooling for developing, maintaining, submitting, and reviewing
Bioconductor R packages to the project's official standards. The knowledge is distilled from the
official guide "Bioconductor Packages: Development, Maintenance, and Peer Review"
(https://contributions.bioconductor.org) into portable, task-oriented summaries that any AI
coding assistant - or a human - can follow.

It ships in two forms from one source of truth:
- A Claude Code plugin: a skill (`bioconductor-package-dev`) plus a review agent
  (`bioc-package-review`).
- A cross-tool `AGENTS.md` that Codex, Cursor, Gemini CLI, GitHub Copilot, and other assistants
  read natively.

## Repository layout

```
bioc_package_dev/
├── README.md                 # this file
├── AGENTS.md                 # cross-tool entrypoint (Codex/Cursor/Gemini/Copilot)
├── GEMINI.md                 # imports AGENTS.md (for Gemini CLI)
├── CLAUDE.md                 # imports AGENTS.md (for Claude Code)
├── LICENSE                   # Apache-2.0
├── knowledge/                # single source of truth - portable markdown summaries
│   ├── index.md              # topic router across all summaries
│   ├── workflow.md           # end-to-end submission runbook
│   ├── 01-submissions.md     # ch 1
│   ├── development/          # ch 2-23 (naming, metadata, docs, data, tests, code, ...)
│   ├── maintenance.md        # ch 24-30
│   ├── reviewer.md           # ch 31-33
│   └── appendices.md         # A-H
├── templates/                # lean package skeletons
├── scripts/
│   └── check-submission.R    # runs the pre-submission gate checks
├── .claude-plugin/           # Claude Code plugin + marketplace manifests
├── skills/bioconductor-package-dev/SKILL.md
├── agents/bioc-package-review.md
└── context/                  # working docs (session state, plan, TODO)
```

## Prerequisites

For the guidance itself, none - it is markdown. To actually build and check a package you need:
- R (current release, plus R-devel for the final submission check).
- `BiocManager`, and `BiocManager::install("BiocCheck")`.
- Optional: `biocthis` for full package scaffolding; `usethis`, `devtools`, `roxygen2`.

## Install and use

### Claude Code (plugin)

One-command install from this repo's marketplace:

```
/plugin marketplace add ybaeus/bioc_package_dev
/plugin install bioconductor-package-dev
```

Then, in a package project, the skill triggers automatically on Bioconductor work, or invoke it
with `/bioconductor-package-dev`. For a submission-readiness audit, ask Claude to "review my
package for Bioconductor submission" (runs the `bioc-package-review` agent).

To try it before installing, clone this repo and run:

```
claude --plugin-dir /path/to/bioc_package_dev
```

### Codex / Cursor / Gemini CLI / GitHub Copilot (AGENTS.md)

These tools read `AGENTS.md` natively. Either work inside a clone of this repo, or copy
`AGENTS.md` and the `knowledge/` directory into your package project. Gemini CLI also reads
`GEMINI.md` (which imports `AGENTS.md`).

### Any tool, or a human (manual)

Read `knowledge/index.md` to find the topic, or `knowledge/workflow.md` for the full submission
path. Point any assistant at the `knowledge/` directory.

## Keeping it current

The summaries are stamped with the date they were generated from the live guide, and
`knowledge/SOURCES.md` pins the exact upstream `pkgrevdocs` commit they came from. Bioconductor
updates the guide roughly twice a year with each release. Follow `context/REFRESH.md`: diff the
current upstream commit against the pinned one, regenerate only the changed chapters, bump
`version` in `.claude-plugin/plugin.json`, and push. Marketplace users then run
`/plugin marketplace update` and `/plugin update bioconductor-package-dev`. The summaries always
link back to the canonical chapter, which is the authority if anything drifts.

## Attribution and license

The summaries are derived from the Bioconductor contribution guide, source repository
[Bioconductor/pkgrevdocs](https://github.com/Bioconductor/pkgrevdocs) and the rendered guide at
https://contributions.bioconductor.org. That upstream material belongs to the Bioconductor
project; each summary links to its canonical chapter. This repository's own tooling is released
under Apache-2.0 (see `LICENSE`). "Bioconductor" is a trademark of the Bioconductor project;
this project is not affiliated with or endorsed by Bioconductor.
