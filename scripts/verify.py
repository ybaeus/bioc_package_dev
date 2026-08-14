#!/usr/bin/env python3
"""Verify the internal consistency of this repository.

Layer 1 (default) is static: no network, no R, no LLM, Python 3 stdlib only. It checks the
things that rot silently in a repo made of prose - dead paths, stamps, duplicated rule text
that has drifted between the files that restate it.

Layer 2 (--network) checks this repo against its upstreams. See check_network().

    python3 scripts/verify.py
    python3 scripts/verify.py --network
    python3 scripts/verify.py --list

Exit status is 1 if any check fails. Warnings never fail the run.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The skill bundle mirrored byte for byte from bioconductor/ai-agent-skills. knowledge/ lives
# inside it, not at the repository root, because that is where upstream keeps it - prose inside
# the bundle writes `knowledge/...` and means this. Nothing in here may be edited to satisfy a
# local check: the check gets taught the layout, or the change goes upstream and comes back.
MIRRORED_SKILL = "skills/bioc-pkg-dev"
KNOWLEDGE = MIRRORED_SKILL + "/knowledge"

# Where this repository records the CI action versions it pins. Repo-native on purpose: the
# bundle mirrors upstream, which has no stake in our workflow.
CI_PINS = "docs/REFRESH.md"

# Files that restate the pre-submission gate. Kept in sync deliberately (an agent needs the gate
# in context nearly every turn, so it is duplicated rather than referenced), which is exactly why
# it has to be checked.
GATE_FILES = [
    "AGENTS.md",
    "skills/bioc-pkg-dev/SKILL.md",
    "agents/bioc-package-review.md",
    KNOWLEDGE + "/workflow.md",
]

# Files carrying the identical BiocCheck/biocthis tooling block. SKILL.md is deliberately not
# one of them any more: it mirrors upstream, whose layout has no "## Tooling" section, so
# requiring one here would force the two copies apart again. AGENTS.md and the review agent are
# repo-native and still have to agree.
ROUTER_FILES = [
    "AGENTS.md",
    "agents/bioc-package-review.md",
]

# Sections AGENTS.md must keep. It is the cross-tool router and now the only file that routes.
#
# The byte-identical AGENTS.md/SKILL.md comparison that used to live here is gone. SKILL.md is a
# verbatim mirror of upstream, which states the same rules in its own words and links into
# knowledge/ relative to the skill directory rather than the repository root - byte-equality is
# unachievable by construction, not merely unmet, so a check demanding it would only ever be
# noise. The substantive half moved to GATE_VALUES, which every gate-restating file satisfies.
ROUTER_SECTIONS = [
    "## Pre-submission gate",
    "## Version rule",
    "## Bioconductor code style (differs from tidyverse)",
]

# The hard numbers of the gate. Every file restating the gate must carry all of them. "80%" is
# here because it is the gate item a package fails while looking fine: BiocCheck errors below
# 80% runnable examples, so a file restating the gate without it calls a package submittable
# when BiocCheck will not.
GATE_VALUES = ["0.99.0", "10 MB", "10 min", "5 MB", "8 GB", "80%"]

# Tools this repo used to reimplement and must never reference again.
DEAD_REFERENCES = ["check-submission.R", "context/REFRESH.md"]

# Top-level names that mean "a path inside this repository". Deleted and not-yet-created
# directories are listed on purpose: a reference to one must fail, not be silently skipped.
REPO_PREFIXES = {
    ".claude-plugin", ".github", "agents", "context", "docs", "evals",
    "knowledge", "scripts", "skills", "templates",
}

# Basenames that name a file in the *user's* package, not in this repo.
FOREIGN_BASENAMES = {"NEWS.md", "README.md", "CITATION.md", "INSTALL.md"}

# Spelled with escapes, not literals: a checker that trips its own check is not a good look, and
# box-drawing characters (U+2500-257F, used by the README tree) must stay outside these ranges.
EMOJI = re.compile(
    "["
    "\U0001f000-\U0001faff"  # pictographs, emoticons, transport, symbols
    "\u2600-\u27bf"          # miscellaneous symbols and dingbats
    "\u2b00-\u2bff"          # arrows and geometric shapes
    "\ufe0f"                 # variation selector 16
    "]"
)

SLUG_URL = re.compile(r"https://contributions\.bioconductor\.org/([A-Za-z0-9._-]+)\.html")


@dataclass
class Result:
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout


def tracked_files() -> list[str]:
    return [p for p in git("ls-files").splitlines() if p]


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


def shipped_markdown() -> list[str]:
    """Every tracked markdown file. context/ is gitignored, so it is absent by construction."""
    return [p for p in tracked_files() if p.endswith(".md")]


def knowledge_files() -> list[str]:
    return [
        p for p in tracked_files()
        if p.startswith(KNOWLEDGE + "/") and p.endswith(".md")
        and p != KNOWLEDGE + "/SOURCES.md"
    ]


def section(text: str, heading: str) -> str | None:
    """Return a section body, up to the next heading of the same level or higher.

    Handles `##` and `###`: a `### 3. ...` step must end at `### 4. ...`, not run on to the
    next `##`, or every comparison against it silently includes the steps that follow.
    """
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return None
    depth = len(heading) - len(heading.lstrip("#"))
    body = []
    for line in lines[start + 1:]:
        stripped = len(line) - len(line.lstrip("#"))
        if 0 < stripped <= depth and line[stripped:stripped + 1] == " ":
            break
        body.append(line)
    return "\n".join(body).strip("\n")


# --------------------------------------------------------------------------------------------
# Check 1 - plugin manifests
# --------------------------------------------------------------------------------------------

def check_manifests(res: Result) -> None:
    try:
        plugin = json.loads(read(".claude-plugin/plugin.json"))
        market = json.loads(read(".claude-plugin/marketplace.json"))
    except (OSError, json.JSONDecodeError) as exc:
        res.fail(f"manifests: cannot parse - {exc}")
        return

    for key in ("name", "description", "version"):
        if not plugin.get(key):
            res.fail(f".claude-plugin/plugin.json: missing required key {key!r}")
    for key in ("name", "description", "owner", "plugins"):
        if not market.get(key):
            res.fail(f".claude-plugin/marketplace.json: missing required key {key!r}")

    name = plugin.get("name")
    if name and not os.path.isdir(os.path.join(ROOT, "skills", name)):
        res.fail(f"plugin.json name {name!r} has no matching skills/{name}/ directory")

    listed = [p.get("name") for p in market.get("plugins", [])]
    if name and name not in listed:
        res.fail(f"plugin.json name {name!r} is not listed in marketplace.json plugins {listed}")

    version = plugin.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        res.fail(f"plugin.json version {version!r} is not x.y.z - users only update on a bump")


# --------------------------------------------------------------------------------------------
# Check 2 - skill and agent frontmatter
# --------------------------------------------------------------------------------------------

def frontmatter(path: str) -> dict[str, str]:
    text = read(path)
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    block = text[4:end]
    out: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            out[key] = m.group(2).strip()
        elif key and line.strip():
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def check_frontmatter(res: Result) -> None:
    skill = "skills/bioc-pkg-dev/SKILL.md"
    meta = frontmatter(skill)
    if not meta:
        res.fail(f"{skill}: no YAML frontmatter")
    else:
        if meta.get("name") != "bioc-pkg-dev":
            res.fail(f"{skill}: frontmatter name {meta.get('name')!r} != directory name")
        desc = meta.get("description", "")
        if len(desc) < 80:
            res.fail(f"{skill}: description is {len(desc)} chars - too thin to route on")
        # The target user converts an existing package, and this description is the only thing
        # routing to the skill here - the plugin has no SKILLS.md index the way upstream does.
        # Demoted from failure to warning when SKILL.md became a verbatim mirror: upstream owns
        # the wording, and it can afford a terser description because its SKILLS.md entry carries
        # the "when to use" bullets. The risk is real rather than theoretical, so it still gets
        # said out loud, and evals/trigger-cran-move is what actually measures it.
        missing = [t for t in ("existing", "CRAN", "submission") if t.lower() not in desc.lower()]
        if missing:
            res.warn(
                f"{skill}: description never mentions {missing} - this is the conversion "
                "audience's vocabulary and the description is the only router here. "
                "Run evals/trigger-cran-move before trusting the skill still fires."
            )

    agent = "agents/bioc-package-review.md"
    meta = frontmatter(agent)
    if not meta:
        res.fail(f"{agent}: no YAML frontmatter")
        return
    for key in ("name", "description", "model", "tools"):
        if not meta.get(key):
            res.fail(f"{agent}: frontmatter missing {key!r}")
    expected = os.path.basename(agent)[:-3]
    if meta.get("name") != expected:
        res.fail(f"{agent}: frontmatter name {meta.get('name')!r} != filename {expected!r}")
    if "Write" in meta.get("tools", "") or "Edit" in meta.get("tools", ""):
        res.fail(f"{agent}: grants write tools, but the agent is specified as read-only")


# --------------------------------------------------------------------------------------------
# Check 3 - path references resolve and are not gitignored
# --------------------------------------------------------------------------------------------

BACKTICKED = re.compile(r"`([^`\n]+)`")


def path_candidates(path: str, line: str) -> list[str]:
    """Backticked tokens on one line that are meant to name a file in *this* repository.

    Most backticked paths in these documents belong to the user's package (`tests/`, `man/`,
    `inst/CITATION`) or to an upstream project, so the filter has to be narrow: a token counts
    only if it is rooted at one of this repo's top-level directories, or if it is a relative
    markdown reference inside knowledge/. Lines carrying a URL are skipped entirely - they are
    naming somebody else's file.
    """
    if "http" in line:
        return []
    out = []
    for token in BACKTICKED.findall(line):
        token = token.strip().replace("${CLAUDE_PLUGIN_ROOT}/", "").rstrip(".,;:")
        if not token or " " in token or "(" in token or token.startswith(("<", "-")):
            continue
        if os.path.basename(token) in FOREIGN_BASENAMES:
            continue
        rooted = token.split("/", 1)[0] in REPO_PREFIXES
        knowledge_ref = path.startswith(KNOWLEDGE + "/") and token.endswith(".md")
        if rooted or knowledge_ref:
            out.append(token)
    return out


def resolve(path: str, token: str, by_basename: dict[str, list[str]]) -> str | None:
    # MIRRORED_SKILL is a base because prose inside the bundle says `knowledge/...` and means the
    # bundle's own directory, not the repository root - upstream keeps knowledge/ beside SKILL.md.
    bases = (
        ROOT,
        os.path.join(ROOT, os.path.dirname(path)),
        os.path.join(ROOT, MIRRORED_SKILL),
        os.path.join(ROOT, KNOWLEDGE),
    )
    for base in bases:
        if os.path.exists(os.path.join(base, token)):
            return os.path.relpath(os.path.join(base, token), ROOT)
    if "/" not in token:
        hits = by_basename.get(token, [])
        if len(hits) == 1:
            return hits[0]
    return None


def check_paths(res: Result) -> None:
    by_basename: dict[str, list[str]] = {}
    for tracked in tracked_files():
        by_basename.setdefault(os.path.basename(tracked), []).append(tracked)

    ignored: dict[str, bool] = {}
    for path in shipped_markdown():
        for lineno, line in enumerate(read(path).splitlines(), 1):
            for token in path_candidates(path, line):
                resolved = resolve(path, token, by_basename)
                if resolved is None:
                    res.fail(f"{path}:{lineno}: references `{token}`, which does not exist")
                    continue
                if resolved not in ignored:
                    code = subprocess.run(
                        ["git", "check-ignore", "-q", resolved],
                        cwd=ROOT, capture_output=True, check=False,
                    ).returncode
                    ignored[resolved] = code == 0
                if ignored[resolved]:
                    res.fail(
                        f"{path}:{lineno}: references `{token}`, which is gitignored - "
                        "dead path in every clone and in the installed plugin"
                    )


# --------------------------------------------------------------------------------------------
# Check 4 - README layout tree matches the repository
# --------------------------------------------------------------------------------------------

def check_readme_tree(res: Result) -> None:
    text = read("README.md")
    body = section(text, "## Repository layout")
    if body is None:
        res.fail("README.md: no '## Repository layout' section")
        return
    block = re.search(r"```\n(.*?)```", body, re.S)
    if not block:
        res.fail("README.md: layout section has no fenced tree")
        return

    # Only depth-0 entries are compared: a top-level directory disappearing is the failure that
    # matters, and mirroring every leaf would make the tree a second source of truth.
    listed = set()
    for line in block.group(1).splitlines():
        m = re.match(r"^(?:├── |└── )(\S+)", line)
        if not m:
            continue
        listed.add(m.group(1).rstrip("/").split("/")[0])

    actual = {p.split("/")[0] for p in tracked_files()}
    actual.discard(".gitignore")
    missing = sorted(actual - listed)
    if missing:
        res.fail(f"README.md layout tree omits tracked top-level entries: {missing}")

    for entry in sorted(listed - actual):
        if entry.startswith("."):
            continue
        res.warn(f"README.md layout tree lists {entry!r}, which is not tracked yet")


# --------------------------------------------------------------------------------------------
# Check 5 - Source and Fetched stamps
# --------------------------------------------------------------------------------------------

STAMP = re.compile(r"^Fetched (\d{4}-\d{2}-\d{2})", re.M)


def check_stamps(res: Result) -> None:
    today = dt.date.today()
    for path in knowledge_files():
        text = read(path)
        if not SLUG_URL.search(text):
            res.fail(f"{path}: no canonical contributions.bioconductor.org Source: URL")
        m = STAMP.search(text)
        if not m:
            res.fail(f"{path}: no 'Fetched YYYY-MM-DD' stamp")
            continue
        age = (today - dt.date.fromisoformat(m.group(1))).days
        if age > 90:
            res.warn(f"{path}: Fetched stamp is {age} days old")


# --------------------------------------------------------------------------------------------
# Check 6 - SOURCES.md map and the per-file Source: footers agree
# --------------------------------------------------------------------------------------------

def sources_rows() -> list[tuple[str, str, str]]:
    """(rmd, slug, target) rows of the chapter map in knowledge/SOURCES.md."""
    rows = []
    for line in read(KNOWLEDGE + "/SOURCES.md").splitlines():
        if not line.startswith("| `") or line.startswith("| ---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        rmd, slug, _chapter, target = cells
        rows.append((rmd.strip("`"), slug.strip("`"), target))
    return rows


def check_sources_map(res: Result) -> None:
    rows = sources_rows()
    if not rows:
        res.fail(KNOWLEDGE + "/SOURCES.md: chapter map has no parseable rows")
        return

    mapped_slugs = {slug for _rmd, slug, _t in rows if slug != "-"}

    # Forward: every mapped slug whose target is a real file must be cited by that file.
    for _rmd, slug, target in rows:
        if slug == "-" or not target.startswith("`"):
            continue
        target_path = os.path.join(KNOWLEDGE, target.strip("`"))
        if not os.path.exists(os.path.join(ROOT, target_path)):
            res.fail(f"{KNOWLEDGE}/SOURCES.md: maps {slug} to {target_path}, does not exist")
            continue
        if slug not in SLUG_URL.findall(read(target_path)):
            res.fail(
                f"{KNOWLEDGE}/SOURCES.md: maps slug {slug!r} to {target_path}, "
                f"but that file never cites {slug}.html in its Source: footer"
            )

    # Reverse: every slug cited anywhere must be in the map.
    for path in knowledge_files():
        for slug in set(SLUG_URL.findall(read(path))):
            if slug not in mapped_slugs:
                res.fail(f"{path}: cites slug {slug!r}, which is absent from the SOURCES.md map")


# --------------------------------------------------------------------------------------------
# Check 7 - references to tooling this repo deliberately removed
# --------------------------------------------------------------------------------------------

def check_dead_references(res: Result) -> None:
    for path in shipped_markdown():
        text = read(path)
        for needle in DEAD_REFERENCES:
            if needle in text:
                res.fail(f"{path}: references {needle!r}, which was removed from this repo")
        if re.search(r"`templates/", text):
            res.fail(
                f"{path}: references `templates/`, which was removed - "
                "point at biocthis instead"
            )


# --------------------------------------------------------------------------------------------
# Check 8 - the BiocCheck/biocthis block is identical everywhere it appears
# --------------------------------------------------------------------------------------------

TOOLING_HEADING = "## Tooling (use these, do not reimplement them)"


def tooling_block(text: str) -> str | None:
    for m in re.finditer(r"```r\n(.*?)```", text, re.S):
        if "BiocCheckGitClone" in m.group(1):
            return m.group(1)
    return None


def check_tooling_block(res: Result) -> None:
    blocks = {}
    for path in ROUTER_FILES:
        text = read(path)
        if TOOLING_HEADING not in text:
            res.fail(f"{path}: missing the {TOOLING_HEADING!r} section")
        block = tooling_block(text)
        if block is None:
            res.fail(f"{path}: has no BiocCheck/biocthis command block")
            continue
        blocks[path] = block

    if len(set(blocks.values())) > 1:
        res.fail(
            "the BiocCheck/biocthis command block differs between "
            + ", ".join(sorted(blocks))
            + " - all three must be identical, and golden-path.R runs it"
        )

    for path, block in blocks.items():
        if "BiocCheckGitClone()" not in block or "'new-package' = TRUE" not in block:
            res.fail(f"{path}: tooling block does not call both BiocCheck entry points")
        if "use_bioc_description" not in block:
            res.fail(f"{path}: tooling block does not scaffold with biocthis")

    golden = os.path.join(ROOT, "scripts", "golden-path.R")
    if blocks and os.path.exists(golden):
        with open(golden, encoding="utf-8") as handle:
            script = handle.read()
        for call in sorted(set(re.findall(r"use_bioc_\w+", next(iter(blocks.values()))))):
            if call not in script:
                res.fail(
                    f"scripts/golden-path.R never calls {call}(), "
                    "so the documented scaffolding chain is not the tested one"
                )


# --------------------------------------------------------------------------------------------
# Check 9 - the gate numbers appear everywhere the gate is restated
# --------------------------------------------------------------------------------------------

def check_gate_values(res: Result) -> None:
    for path in GATE_FILES:
        text = read(path)
        for value in GATE_VALUES:
            if value not in text:
                res.fail(f"{path}: restates the gate but never mentions {value!r}")


# --------------------------------------------------------------------------------------------
# Check 10 - no emoji
# --------------------------------------------------------------------------------------------

def check_no_emoji(res: Result) -> None:
    for path in tracked_files():
        if not path.endswith((".md", ".py", ".R", ".json", ".yml", ".yaml")):
            continue
        for lineno, line in enumerate(read(path).splitlines(), 1):
            m = EMOJI.search(line)
            if m:
                res.fail(f"{path}:{lineno}: emoji {m.group(0)!r} - repo docs are plain text")


# --------------------------------------------------------------------------------------------
# Check 11 - duplicated rule text has not drifted, and the router lives in one place
# --------------------------------------------------------------------------------------------

def check_single_source(res: Result) -> None:
    agents = read("AGENTS.md")

    for heading in ROUTER_SECTIONS:
        if section(agents, heading) is None:
            res.fail(f"AGENTS.md: missing router section {heading!r}")

    # SKILL.md mirrors skills/bioc-pkg-dev in bioconductor/ai-agent-skills, so it has to keep the
    # frontmatter that repository's CI requires. Losing a field here surfaces as a failed sync
    # upstream rather than as a failure at home, which is the wrong place to find out.
    meta = frontmatter(f"{MIRRORED_SKILL}/SKILL.md") or {}
    for key in ("name", "description", "version", "category", "author"):
        if not meta.get(key):
            res.fail(
                f"{MIRRORED_SKILL}/SKILL.md: frontmatter missing {key!r} - "
                "bioconductor/ai-agent-skills rejects the skill without it"
            )
    for banned in ("platforms", "triggers"):
        if banned in meta:
            res.fail(
                f"{MIRRORED_SKILL}/SKILL.md: prohibited frontmatter field {banned!r} - "
                "skills upstream are agent-agnostic"
            )
    if meta.get("name") != os.path.basename(MIRRORED_SKILL):
        res.fail(
            f"{MIRRORED_SKILL}/SKILL.md: frontmatter name {meta.get('name')!r} does not match "
            "its directory - upstream requires the two to be identical"
        )


# --------------------------------------------------------------------------------------------
# Check 12 - the Fetched stamp is a contract, not a decoration
# --------------------------------------------------------------------------------------------

def check_stamp_contract(res: Result) -> None:
    for path in knowledge_files():
        m = STAMP.search(read(path))
        if not m:
            continue  # already reported by check 5
        committed = git("log", "-1", "--format=%cs", "--", path).strip()
        if not committed:
            continue  # never committed; nothing to compare against
        if dt.date.fromisoformat(committed) > dt.date.fromisoformat(m.group(1)):
            res.fail(
                f"{path}: last commit {committed} is newer than its Fetched stamp {m.group(1)} - "
                "content was edited without restamping, so the provenance is a claim it cannot back"
            )


# --------------------------------------------------------------------------------------------
# Check 13 - the CI workflow pins the action version recorded in SOURCES.md
# --------------------------------------------------------------------------------------------

WORKFLOW = ".github/workflows/verify.yml"


def check_workflow_pins(res: Result) -> None:
    if not os.path.exists(os.path.join(ROOT, WORKFLOW)):
        res.fail(f"{WORKFLOW} does not exist - the verification layers are not wired to CI")
        return
    text = read(WORKFLOW)

    for m in re.finditer(r"uses:\s*(\S+)@(\S+)", text):
        action, ref = m.groups()
        if ref in ("main", "master", "devel", "HEAD"):
            res.fail(f"{WORKFLOW}: {action} is pinned to a branch ({ref}), not a tag")

    # The pin lives in docs/REFRESH.md, not in the bundle's SOURCES.md: it is this repository's
    # CI dependency, and the bundle mirrors upstream, which has no CI of ours to pin.
    pinned = re.search(r"bioc-actions.*?\|\s*`(v[\d.]+)`", read(CI_PINS))
    if not pinned:
        res.fail(f"{CI_PINS}: no bioc-actions tag pin found")
        return
    used = set(re.findall(r"grimbough/bioc-actions/\S+@(\S+)", text))
    wrong = sorted(used - {pinned.group(1)})
    if wrong:
        res.fail(
            f"{WORKFLOW} uses bioc-actions {wrong}, but {CI_PINS} pins "
            f"{pinned.group(1)} - bump both together or neither"
        )


# --------------------------------------------------------------------------------------------
# Check 14 - documented example prompts are the prompts CI actually exercises
# --------------------------------------------------------------------------------------------

def eval_cases() -> list[str]:
    return [p for p in tracked_files() if p.startswith("evals/") and p.endswith("case.yaml")]


def check_evals(res: Result) -> None:
    cases = eval_cases()
    if not cases:
        res.fail("evals/ has no case.yaml files - Layer 4 is not wired up")
        return

    for path in cases:
        text = read(path)
        name = os.path.basename(os.path.dirname(path))
        if "schema_version:" not in text:
            res.fail(f"{path}: no schema_version - the eval runner rejects the case")
        m = re.search(r"^name:\s*(\S+)", text, re.M)
        if not m:
            res.fail(f"{path}: no name field")
        elif m.group(1) != name:
            res.fail(f"{path}: name {m.group(1)!r} does not match its directory {name!r}")
        if "graders:" not in text:
            res.fail(f"{path}: no graders - a case with no grader scores nothing")

    # Every prompt the README advertises has to be one the suite actually runs, or the docs
    # drift away from what is tested and the examples become folklore.
    body = section(read("README.md"), "## Example prompts") or ""
    documented = re.findall(r'^- "([^"]+)"', body, re.M)
    if not documented:
        res.fail("README.md: no quoted prompts found under '## Example prompts'")
        return

    haystack = " ".join(re.sub(r"\s+", " ", read(p)) for p in cases)
    for prompt in documented:
        if re.sub(r"\s+", " ", prompt) not in haystack:
            res.fail(
                f"README.md documents the prompt {prompt!r}, which no eval case runs - "
                "add a case for it or drop it from the README"
            )


STATIC_CHECKS = [
    ("manifests", check_manifests),
    ("frontmatter", check_frontmatter),
    ("paths", check_paths),
    ("readme-tree", check_readme_tree),
    ("stamps", check_stamps),
    ("sources-map", check_sources_map),
    ("dead-references", check_dead_references),
    ("tooling-block", check_tooling_block),
    ("gate-values", check_gate_values),
    ("no-emoji", check_no_emoji),
    ("single-source", check_single_source),
    ("stamp-contract", check_stamp_contract),
    ("workflow-pins", check_workflow_pins),
    ("evals", check_evals),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--network", action="store_true", help="also run upstream fidelity checks")
    parser.add_argument("--list", action="store_true", help="list checks and exit")
    parser.add_argument("--json", action="store_true", help="emit machine-readable results")
    args = parser.parse_args(argv)

    checks = list(STATIC_CHECKS)
    if args.network:
        from verify_network import NETWORK_CHECKS  # noqa: PLC0415  (optional, needs network)
        checks += NETWORK_CHECKS

    if args.list:
        for name, fn in checks:
            print(f"{name:18s} {(fn.__doc__ or '').strip().splitlines()[0] if fn.__doc__ else ''}")
        return 0

    res = Result()
    for name, fn in checks:
        before = len(res.failures)
        try:
            fn(res)
        except Exception as exc:  # a checker crash is a failure, not a pass
            res.fail(f"{name}: checker raised {type(exc).__name__}: {exc}")
        status = "FAIL" if len(res.failures) > before else "ok"
        if not args.json:
            print(f"[{status:4s}] {name}")

    if args.json:
        print(json.dumps({"failures": res.failures, "warnings": res.warnings}, indent=2))
    else:
        for msg in res.warnings:
            print(f"  warn: {msg}")
        for msg in res.failures:
            print(f"  FAIL: {msg}")
        print(f"\n{len(res.failures)} failure(s), {len(res.warnings)} warning(s)")

    return 1 if res.failures else 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
