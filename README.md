# bioc_package_dev

Reusable AI-assistant tooling for developing, maintaining, submitting, and reviewing
Bioconductor R packages to the project's official standards. The knowledge is distilled from the official guide "Bioconductor Packages: Development, Maintenance, and Peer Review" (https://contributions.bioconductor.org) into portable, task-oriented summaries that any AI
coding assistant - or a human - can follow.

It ships in two forms from one source of truth:
- A Claude Code plugin: a skill (`bioc-pkg-dev`) plus a review agent
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
│   ├── workflow.md           # end-to-end runbook, incl. converting an existing package
│   ├── SOURCES.md            # .Rmd -> slug -> file map + pins for all tracked upstreams
│   ├── 01-submissions.md     # ch 1
│   ├── development/          # ch 2-23 (naming, metadata, docs, data, tests, code, ...)
│   ├── maintenance.md        # ch 24-30
│   ├── reviewer.md           # ch 31-33
│   └── appendices.md         # A-H
├── docs/REFRESH.md           # how to re-sync with upstream when it moves
├── scripts/                  # verification, not package tooling (see "How this is verified")
├── evals/                    # behavioral test cases for the skill and agent
├── .github/workflows/        # CI running the verification layers
├── .claude-plugin/           # Claude Code plugin + marketplace manifests
├── skills/bioc-pkg-dev/SKILL.md
└── agents/bioc-package-review.md
```

There is deliberately no templates directory and no check script. Bioconductor already
maintains both - `biocthis` for scaffolding, `BiocCheck` for validation - and reusing existing
infrastructure instead of reinventing it is one of the things reviewers look for (ch 5). Shipping
a competing copy would have made this repo violate the guidance it teaches.

## Prerequisites

For the guidance itself, none - it is markdown. To actually build and check a package you need:
- R (current release, plus R-devel for the final submission check).
- `BiocManager::install(c("BiocCheck", "biocthis", "BiocStyle", "knitr", "RefManageR",
  "sessioninfo", "testthat", "roxygen2"))` - BiocCheck validates and biocthis scaffolds; the rest
  are what `biocthis::use_bioc_vignette()` refuses to run without. The exact list, and the traps
  in the scaffolding chain, are in the tooling block in `AGENTS.md`.
- Pandoc, if you want to build an R Markdown vignette locally.
- Optional: `usethis`, `devtools`.

To run this repo's own verification you need Python 3 (stdlib only) for `scripts/verify.py`; the
network layer additionally needs outbound HTTPS. No R is required for the static layer.

## Install and use

### Claude Code (plugin)

One-command install from this repo's marketplace:

```
/plugin marketplace add ybaeus/bioc_package_dev
/plugin install bioc-pkg-dev
```

Then, in a package project, the skill triggers automatically on Bioconductor work, or invoke it
with `/bioc-pkg-dev`. For a submission-readiness audit, ask Claude to "review my
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

## Example prompts

Written for the main case: you already have R work on GitHub - a package, or just analysis code -
and want to contribute it to Bioconductor. Ask in your own words - these are shapes, not
incantations.

Getting oriented:

- "I have an R package on GitHub, what do I need to do to submit it to Bioconductor?"
- "I have this crufty analysis code, review it and make it into a Bioconductor-submittable package"
- "My package is on CRAN, can I move it to Bioconductor?"
- "What version number do I use for a new submission?"

Working through specifics:

- "I have 300 MB of reference data, where does it go?" (answer: not in the package)
- "Write me a function that iterates over samples" (applies Bioconductor style, not tidyverse)
- "My DESCRIPTION has no biocViews - what do I put there?"
- "Walk me through what happens after I open the Contributions issue."

Checking readiness - these route to the `bioc-package-review` agent, which audits and reports
blockers rather than advising as you work:

- "Audit my package for Bioconductor submission readiness."
- "Would this package pass review? Tell me what a reviewer would flag."

The split in one line each: the skill guides you while you work; the agent renders a verdict on
demand.

## Keeping it current

The summaries are stamped with the date they were generated from the live guide, and
`knowledge/SOURCES.md` pins the exact upstream `pkgrevdocs` commit they came from. Bioconductor
updates the guide roughly twice a year with each release. Follow `docs/REFRESH.md`: diff the
current upstream commit against the pinned one, regenerate only the changed chapters, bump
`version` in `.claude-plugin/plugin.json`, and push. Marketplace users then run
`/plugin marketplace update` and `/plugin update bioc-pkg-dev`. The summaries always
link back to the canonical chapter, which is the authority if anything drifts.

Five upstreams are tracked, not just the guide: `pkgrevdocs`, the Contributions issue template,
BiocCheck, biocthis, and bioc-actions. All five pins live in `knowledge/SOURCES.md`, and the
weekly `fidelity` CI job opens an issue when any of them moves.

## How this is verified

Prose summarizing a live document rots quietly: a URL dies, upstream rewords a rule, a threshold
drifts between the files that restate it, or a reworded skill `description` stops the skill from
firing while every file still looks fine. Four layers catch different failures.

| Layer | Command | Catches |
|---|---|---|
| Static | `python3 scripts/verify.py` | broken internal paths, gitignored references, manifest and frontmatter errors, missing `Source:`/`Fetched` stamps, rule text that has drifted between the files that duplicate it, emoji, a stale README tree |
| Fidelity | `python3 scripts/verify.py --network` | upstream commit drift mapped to the affected summaries, dead chapter URLs, thresholds that no longer match upstream, summaries that harden an upstream "should" into a "must", gate wording that no longer matches the submission tracker, new upstream chapters nobody summarized |
| Golden path | `Rscript scripts/golden-path.R` + `R CMD build` + `BiocCheck` in CI | the scaffolding commands this repo tells you to run, by running them and checking the result with real Bioconductor tooling |
| Behavior | `claude plugin eval . --scaffold` | the skill firing when it should, staying quiet when it should not, and returning the right values - including every prompt in "Example prompts" above |

The fidelity job is a weekly cron rather than a PR gate: upstream changing is a reason to open an
issue, not to block someone's pull request.

The golden path earns its keep. On its first real run it found five ways the documented
instructions failed: `use_bioc_vignette()` needs BiocStyle and friends actually installed, not
just declared; `use_bioc_description()` silently declines to touch an existing DESCRIPTION;
`use_bioc_citation()` writes an `inst/CITATION` with an empty title and author that makes
`R CMD build` fail; and `biocViews = "Software"` on its own is a BiocCheck error. Every one of
those would have been hit by a user following this repo's advice, and none of them is visible by
reading the files. It now passes end to end against Bioconductor devel.

## Built on

This repo is a thin layer over other people's work. It contributes routing, summarization, and
verification; everything substantive below belongs to the projects listed here, and the design
rule throughout has been to point at existing Bioconductor infrastructure rather than ship a
competing copy of it.

- **Bioconductor Packages: Development, Maintenance, and Peer Review** - Kevin Rue-Albrecht,
  Daniela Cassol, Johannes Rainer, Lori Shepherd, Marcel Ramos Pérez, Martin Morgan.
  https://contributions.bioconductor.org, source
  [Bioconductor/pkgrevdocs](https://github.com/Bioconductor/pkgrevdocs). Every file under
  `knowledge/` is derived from it, cites the chapter it came from, and defers to it on any
  disagreement.
- **[BiocCheck](https://github.com/Bioconductor/BiocCheck)** - Lori Shepherd, Marcel Ramos, and
  the Bioconductor core team. The authoritative validator. This repo runs it and reads its output
  instead of reimplementing its checks.
- **[biocthis](https://github.com/lcolladotor/biocthis)** - Leonardo Collado-Torres. Scaffolding
  that writes Bioconductor-shaped package files. This repo recommends it rather than shipping
  templates, and CI runs the exact command sequence it recommends.
- **[bioc-actions](https://github.com/grimbough/bioc-actions)** - Mike Smith. Composite GitHub
  Actions for setting up Bioconductor, building, checking, and running BiocCheck. They power the
  golden-path job, which is what lets this repo claim its instructions actually work.
- **[Bioconductor/Contributions](https://github.com/Bioconductor/Contributions)** - the submission
  tracker, and the source of the authoritative pre-submission checklist that the gate here is
  checked against.

Thanks to all of them. Errors in the summaries are this repo's, not theirs - report them here, and
consult the linked chapter as the authority.

## Attribution and license

The summaries are derived from the Bioconductor contribution guide, source repository
[Bioconductor/pkgrevdocs](https://github.com/Bioconductor/pkgrevdocs) and the rendered guide at
https://contributions.bioconductor.org. That upstream material belongs to the Bioconductor
project; each summary links to its canonical chapter. This repository's own tooling is released
under Apache-2.0 (see `LICENSE`). "Bioconductor" is a trademark of the Bioconductor project;
this project is not affiliated with or endorsed by Bioconductor.
