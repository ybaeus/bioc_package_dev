# Refresh runbook

How to keep this repo in sync with the upstream projects it depends on. Run it when Bioconductor
cuts a release (around April and October), when the weekly `fidelity` CI job opens a drift issue,
or before any plugin version bump.

Pinned baseline state lives in `knowledge/SOURCES.md`. This file is the procedure; that file is the
data. Both ship with the plugin.

## Tracked upstreams

Five, not one. A change to any of them can silently invalidate the guidance.

| Upstream | How to detect a change | What it invalidates |
|---|---|---|
| `Bioconductor/pkgrevdocs` | commits API `sha` vs the pin; guide TOC vs the slug map | all of `knowledge/` |
| `Bioconductor/Contributions` `issue_template.md` | commits API for that path vs the pin | the pre-submission gate in `AGENTS.md`, `SKILL.md`, `agents/bioc-package-review.md` |
| `Bioconductor/BiocCheck` | release version + NEWS | what "BiocCheck clean" means; what the review agent should pre-empt |
| `lcolladotor/biocthis` | release version; the `use_bioc_*()` function list | the scaffolding commands the agent recommends, and `scripts/golden-path.R` |
| `grimbough/bioc-actions` | latest tag; each action's `action.yml` inputs | `.github/workflows/verify.yml` |

Most of this is automated. `python3 scripts/verify.py --network` performs every detection step
below and, in CI, opens or updates a single tracking issue. Run it first; this runbook is what you
do with the result.

## Priority order

When more than one signal fires, work top-down. The ordering is by blast radius, not by effort.

1. **Numeric or modal audit failure** - a specific claim in `knowledge/` is now factually wrong and
   is being served to users. Fix immediately and restamp the file.
2. **A chapter URL 404s or redirects** - a chapter was renamed or removed, so the slug map is wrong.
   Fix `knowledge/SOURCES.md` before touching content; every later step depends on the map.
3. **A mapped `.Rmd` changed** - those specific summaries are stale. Scoped refresh only.
4. **Pin moved but no mapped chapter changed** - cosmetic upstream change. Bump the pin, no content
   work.

## 1. pkgrevdocs (the guide)

### Detect

- Current commit: `https://api.github.com/repos/Bioconductor/pkgrevdocs/commits/devel`, field `sha`.
  Compare against the pinned SHA in `knowledge/SOURCES.md`. Equal means stop.
- Changed files: `https://github.com/Bioconductor/pkgrevdocs/compare/<pinned-sha>...devel`
- Chapter set: compare the guide TOC (`https://contributions.bioconductor.org/index.html`) against
  the slug map in `knowledge/SOURCES.md`. This is the only way to notice an **added** chapter -
  every existing file still checks out, so no per-file check will see it.

### Map changes to files

For each changed chapter slug, look up its target in the `knowledge/SOURCES.md` map. Only those
files need regenerating.

- New chapter: new summary file, plus a router entry in `AGENTS.md`, plus a map entry in
  `knowledge/SOURCES.md`.
- Removed chapter: delete its section and fix inbound references.
- Renamed chapter: update the slug map and the `Source:` footer of the affected file.

### Regenerate

Re-run the summary pass for the affected files only. Format rules that must hold, since
`scripts/verify.py` enforces them:

- Plain markdown. No emoji anywhere.
- Task-oriented - actionable rules, thresholds, required and forbidden patterns. Not a
  transcription of the chapter.
- Roughly 40-120 lines per file.
- Ends with a `Source:` line carrying the canonical chapter URL, and a `Fetched <ISO date>` stamp.
- **Preserve upstream modality.** If the guide says "should" or "ideally", the summary says
  "should" or "ideally". Hardening a recommendation into a requirement is a defect, and the
  modal-verb audit in `verify.py --network` will fail on it.
- Restamp `Fetched` on every file you touch. `verify.py` fails when a file's last git commit is
  newer than its stamp, so an edited-but-unstamped file is caught.

If the gate numbers, the version rule, or the submission mechanics changed, also update the inline
copies in `AGENTS.md`, `skills/bioconductor-package-dev/SKILL.md` and
`agents/bioc-package-review.md`. These repeat the gate deliberately, and `verify.py` requires the
copies to stay identical.

## 2. Contributions issue_template.md (the authoritative gate)

The tracker's issue template is the checklist a submitter actually ticks. It, not our prose, is the
authority on what submission requires.

- Detect: `https://api.github.com/repos/Bioconductor/Contributions/commits?path=issue_template.md&per_page=1`
- Content: `https://raw.githubusercontent.com/Bioconductor/Contributions/devel/issue_template.md`

If a checkbox is added, removed, or reworded, update the gate in all three router files and in
`knowledge/01-submissions.md`. This template changes rarely - the pinned commit dates to 2021 - so
any movement is worth reading in full rather than skimming a diff.

## 3. BiocCheck (the validator)

This repo delegates all validation to BiocCheck rather than reimplementing it, so BiocCheck's
behavior is part of our contract with users.

- Detect: release version at `https://bioconductor.org/packages/release/bioc/html/BiocCheck.html`;
  changes at `https://raw.githubusercontent.com/Bioconductor/BiocCheck/devel/NEWS`.

New or removed checks change what "BiocCheck clean" means. If a check is added that maps to advice
we give, `agents/bioc-package-review.md` should pre-empt it so users hear it from the agent before
they hear it from the tool. If a check is removed, drop any advice that existed only to satisfy it.

The two gate items BiocCheck cannot measure are the timing ones - `R CMD check --no-build-vignettes`
under 10 minutes, and under 8 GB memory. Those need a real build; CI measures them.

## 4. biocthis (the scaffolder)

This repo recommends biocthis for scaffolding rather than shipping competing templates. The
commands we tell users to run must exist and must still produce an acceptable package.

- Detect: release version at `https://bioconductor.org/packages/release/bioc/html/biocthis.html`;
  function list at `https://api.github.com/repos/lcolladotor/biocthis/contents/R`.

If a `use_bioc_*()` function is renamed or removed, the command block in `AGENTS.md`, `SKILL.md`
and `agents/bioc-package-review.md` is wrong, and `scripts/golden-path.R` will fail in CI. Those
four places carry the same block and `verify.py` requires them identical, so fix all four together.

Note `biocthis_example_pkg()` is not a Bioconductor-ready generator - it wraps
`usethis::create_package()` in `tempdir()` and produces a bare skeleton. The Bioc-ready path is the
`use_bioc_*()` chain, which is what `golden-path.R` runs.

## 5. bioc-actions (the CI harness)

- Detect: `https://api.github.com/repos/grimbough/bioc-actions/tags`; input schemas at
  `https://raw.githubusercontent.com/grimbough/bioc-actions/<tag>/<action>/action.yml` for
  `setup-bioc`, `build-install-check`, `run-BiocCheck`, `use-bioc-caches`.

Pin a tag in `.github/workflows/verify.yml`, never a branch. A changed input name is a red build
with a confusing message; reading the `action.yml` diff first saves the debugging.
`scripts/verify.py` fails if the tag in the workflow and the tag in `knowledge/SOURCES.md` differ.

Only three of the four actions are used: `setup-bioc`, `build-install-check`, `run-BiocCheck`.
`use-bioc-caches` is deliberately excluded because it pins `actions/cache@v2`, which GitHub
auto-fails - the job dies in "Set up job" with no step ever running, and the error names the
deprecated cache rather than the action that pulled it in. Broken at `v1.0.16` and on `main` as
of 2026-08-14. When bumping the pin, check whether that has been fixed; if it has, the workflow
can drop its hand-rolled `actions/cache@v4` step.

## 6. Update the baseline

In `knowledge/SOURCES.md`, set every pin you verified: the pkgrevdocs SHA and commit date, the
Contributions issue_template SHA, the BiocCheck and biocthis versions, the bioc-actions tag, and
the "Summaries fetched" date.

## 7. Verify

Run in this order; each is cheaper than the next and catches different failures.

1. `python3 scripts/verify.py` - static checks. Must be clean.
2. `python3 scripts/verify.py --network` - drift, URL liveness, numeric and modal audits, gate vs
   tracker, chapter coverage. Must be clean.
3. `PATH=/opt/homebrew/bin:$PATH claude plugin validate .` - manifests. Expect "passed".
4. `Rscript scripts/golden-path.R` then `R CMD build` and `BiocCheck` on the result - confirms the
   scaffolding commands we recommend still produce an acceptable package. CI does this too, but
   running it locally first means the first CI run is not the first execution.
5. `claude --plugin-dir . -p "..."` - load test; confirm skill and agent load and the changed
   content is reflected.
6. `claude plugin eval . --ablation with-without` - behavioral cases. Costs tokens; run when the
   `description` fields or the routing changed, not on every refresh.

## 8. Release

- Bump `version` in `.claude-plugin/plugin.json`. Plugin users only receive updates on a bump.
- Note the change in the commit message.
- Commit and push to `github.com/ybaeus/bioc_package_dev`. Marketplace users then run
  `/plugin marketplace update` followed by `/plugin update bioconductor-package-dev`.

## Notes

- The canonical chapter link in each summary is always authoritative. A lagging summary still points
  readers at the correct source, which is why the `Source:` footer is mandatory.
- Never edit a `knowledge/` file without updating its `Fetched` stamp in the same commit.
- Environment: `env -u CURL_CA_BUNDLE curl -sS <https url>` fetches content fine; the
  `CURL_CA_BUNDLE` variable is set to a stale path and unsetting it is sufficient. `-k` is not
  needed and should not be used. R 4.4.0 at `/usr/local/bin`; `claude` at `/opt/homebrew/bin`;
  `gh` is not installed locally, so use the GitHub REST API via curl.
