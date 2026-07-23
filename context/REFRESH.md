# Refresh runbook

How to keep the `knowledge/` summaries in sync with the upstream Bioconductor guide. Run this
when Bioconductor cuts a release (around April and October) or whenever `pkgrevdocs` has notable
changes. Baseline state lives in `knowledge/SOURCES.md`.

## 1. Detect drift

Check the upstream commit against the pinned one in `knowledge/SOURCES.md`:

- Current commit: `https://api.github.com/repos/Bioconductor/pkgrevdocs/commits/devel` -> field `sha`.
- If it equals the pinned SHA, nothing changed. Stop.
- If it differs, list changed files:
  `https://github.com/Bioconductor/pkgrevdocs/compare/<pinned-sha>...devel`
  (Fetch these with the WebFetch tool; local `curl` has no CA bundle - use `curl -k` only for
  reachability, not for content.)

Also compare the guide TOC (`https://contributions.bioconductor.org/index.html`) against the
slug map in `knowledge/SOURCES.md` to catch added, removed, or renamed chapters. A renamed slug
silently breaks the link in the affected summary.

## 2. Map changes to files

For each changed chapter slug, look up its target file in the `knowledge/SOURCES.md` map. Only
those files need regenerating. A new chapter needs a new file plus a router entry in
`knowledge/index.md` and a map entry in `knowledge/SOURCES.md`. A removed chapter: delete its
section and fix references.

## 3. Regenerate the changed summaries

Re-run the same summary pass used to build these files (prompts and format spec are in
`context/plan.md`, "Content generation"). Use fable-model subagents. Format rules that must hold:
- Plain markdown, no emoji.
- Task-oriented (rules, thresholds, required/forbidden patterns), not a transcription.
- Each file ends with a `Source:` line (canonical chapter URL) and a `Fetched <date>` stamp.

If the pre-submission gate numbers, the version rule, or the submission mechanics changed, also
update the inline copies in `AGENTS.md`, `skills/bioconductor-package-dev/SKILL.md`,
`agents/bioc-package-review.md`, and `knowledge/workflow.md` (these repeat the gate on purpose).

## 4. Update the baseline

In `knowledge/SOURCES.md` set the pinned commit SHA, commit date, and "Summaries fetched" date
to the new values.

## 5. Verify

- `PATH=/opt/homebrew/bin:$PATH claude plugin validate .` (expect: passed).
- Link check: extract `contributions.bioconductor.org/*.html` URLs from `knowledge/` and confirm
  each returns 200 (`env -u CURL_CA_BUNDLE curl -k -sI <url>` locally, or WebFetch).
- Load test: `claude --plugin-dir . -p "..."` and confirm the skill + agent still load and the
  changed content is reflected.

## 6. Release

- Bump `version` in `.claude-plugin/plugin.json` (plugin users only receive updates on a bump).
- Note the change (new NEWS/CHANGELOG line, or the commit message).
- Commit and push to `github.com/ybaeus/bioc_package_dev`. Marketplace users run
  `/plugin marketplace update` then `/plugin update bioconductor-package-dev`.

## Notes
- The canonical chapter link in each summary is always authoritative; a lagging summary still
  points readers to the correct source.
- Environment: R 4.4.0 at /usr/local/bin; `claude` at /opt/homebrew/bin; `gh` is not installed
  (use the GitHub REST API via WebFetch); local curl needs `-k`.
