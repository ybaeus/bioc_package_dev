#!/usr/bin/env python3
"""Layer 2: check this repository against the upstreams it summarizes.

Imported by verify.py when run with --network; not meant to be run on its own. Every check here
needs outbound HTTPS and nothing else - no R, no LLM, no API token. In CI these run on a weekly
cron rather than as a pull-request gate, because upstream changing is a reason to open an issue,
not a reason to block somebody's pull request.

The fidelity checks work by quotation. Where a knowledge file states a load-bearing rule, it
quotes upstream's own words for that rule, and the check asserts the quote is still present in
both places. That catches the two failures a link checker cannot see: upstream changing a rule,
and a summary restating a recommendation as a requirement.
"""

from __future__ import annotations

import html
import json
import os
import re
import ssl
import subprocess
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = "https://contributions.bioconductor.org"
USER_AGENT = "bioc_package_dev-verify/1.0 (+https://github.com/ybaeus/bioc_package_dev)"

# A machine sitting behind a TLS-intercepting proxy has a trust store that urllib rejects and
# curl accepts, which would otherwise make every check here fail for a reason that has nothing
# to do with this repository. So: urllib first, curl second, and never -k in either.
_CURL_ENV = {k: v for k, v in os.environ.items() if k not in ("CURL_CA_BUNDLE", "SSL_CERT_FILE")}

_cache: dict[str, str] = {}


def _curl(url: str, timeout: int, head: bool = False) -> tuple[int, str]:
    args = ["curl", "-sS", "--max-time", str(timeout), "-A", USER_AGENT]
    args += ["-o", os.devnull, "-w", "%{http_code}", "-I"] if head else ["-w", "\n%{http_code}"]
    proc = subprocess.run(
        [*args, url], capture_output=True, text=True, env=_CURL_ENV, check=False
    )
    if proc.returncode != 0:
        return 0, ""
    if head:
        return int(proc.stdout.strip() or 0), ""
    body, _, code = proc.stdout.rpartition("\n")
    return int(code.strip() or 0), body


def fetch(url: str, timeout: int = 30) -> str:
    if url in _cache:
        return _cache[url]
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - https only
            body = resp.read().decode("utf-8", errors="replace")
    except (ssl.SSLError, urllib.error.URLError) as exc:
        code, body = _curl(url, timeout)
        if code != 200:
            raise OSError(f"{url}: urllib said {exc}; curl said HTTP {code}") from exc
    _cache[url] = body
    return body


def fetch_json(url: str) -> object:
    return json.loads(fetch(url))


def status(url: str, timeout: int = 30) -> int:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except OSError:
        return _curl(url, timeout, head=True)[0]


def strip_html(page: str) -> str:
    page = re.sub(r"(?s)<(script|style).*?</\1>", " ", page)
    page = re.sub(r"(?s)<[^>]+>", " ", page)
    return html.unescape(page)


def normalize(text: str) -> str:
    """Fold the differences that are not meaning: markup, quote glyphs, wrapping, case."""
    text = text.replace("**", "").replace("`", "").replace("_", "")
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


def chapter_text(slug: str) -> str:
    return normalize(strip_html(fetch(f"{GUIDE}/{slug}.html")))


# --------------------------------------------------------------------------------------------
# The quotation table - the heart of the fidelity layer
# --------------------------------------------------------------------------------------------
# Each row: the upstream chapter, the exact upstream wording, and the file in this repo that is
# required to carry that wording verbatim. Hand-maintained on purpose. Automatic sentence
# alignment between a chapter and its summary is unreliable, and a check nobody trusts is a check
# nobody triages - so this covers only the rules that carry weight.

CLAIMS: list[dict[str, str]] = [
    {
        "slug": "general",
        "quote": "individual files must be <= 5MB",
        "file": "knowledge/development/general-dev.md",
        "note": "the only size limit upstream states as a requirement",
    },
    {
        "slug": "general",
        "quote": "should occupy less than 10 MB on disk",
        "file": "knowledge/development/general-dev.md",
        "note": "source build size - a recommendation, not a blocker",
    },
    {
        "slug": "general",
        "quote": "should require less than 10 minutes to run R CMD check",
        "file": "knowledge/development/general-dev.md",
        "note": "check duration - a recommendation, not a blocker",
    },
    {
        "slug": "general",
        "quote": (
            "it is recommended that the vignettes, man page examples, and unit tests do not "
            "require more than 8 GB of memory"
        ),
        "file": "knowledge/development/general-dev.md",
        "note": "memory ceiling - explicitly a recommendation",
    },
    {
        "slug": "versionnum",
        "quote": "should set version: 0.99.0 in the description file",
        "file": "knowledge/maintenance.md",
        "note": "the version every new submission starts at",
    },
    {
        "slug": "bioconductor-package-submissions",
        "quote": "the default branch must contain only package code",
        "file": "knowledge/01-submissions.md",
        "note": "a requirement",
    },
    {
        "slug": "bioconductor-package-submissions",
        "quote": "should be in a different branch",
        "file": "knowledge/01-submissions.md",
        "note": "CI helper files - a recommendation, and previously over-hardened here",
    },
    {
        "slug": "bioconductor-package-submissions",
        "quote": "a package can only be submitted to one or the other",
        "file": "knowledge/01-submissions.md",
        "note": "CRAN and Bioconductor are mutually exclusive",
    },
    {
        "slug": "bioconductor-package-submissions",
        "quote": "to submit a package to bioconductor the package should",
        "file": "knowledge/01-submissions.md",
        "note": "the eligibility list is stated as should, not must",
    },
]

# The tracker's issue template, not our prose, is the authority on what submission requires.
TRACKER_TEMPLATE = (
    "https://raw.githubusercontent.com/Bioconductor/Contributions/devel/issue_template.md"
)
TRACKER_QUOTES = [
    (
        "a minimum requirement for package acceptance",
        ["AGENTS.md", "skills/bioconductor-package-dev/SKILL.md"],
    ),
    (
        "does not result in automatic acceptance",
        ["AGENTS.md", "skills/bioconductor-package-dev/SKILL.md"],
    ),
]


# --------------------------------------------------------------------------------------------
# Pins recorded in knowledge/SOURCES.md
# --------------------------------------------------------------------------------------------

def pins() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in read("knowledge/SOURCES.md").splitlines():
        if not line.startswith("| ["):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        name, pin = cells[0], cells[1]
        sha = re.search(r"`([0-9a-f]{40})`", pin)
        tag = re.search(r"`(v[\d.]+)`", pin)
        rel = re.search(r"release ([\d.]+)", pin)
        dev = re.search(r"devel ([\d.]+)", pin)
        if "pkgrevdocs" in name and sha:
            out["pkgrevdocs"] = sha.group(1)
        elif "Contributions" in name and sha:
            out["contributions"] = sha.group(1)
        elif "BiocCheck" in name:
            if rel:
                out["bioccheck_release"] = rel.group(1)
            if dev:
                out["bioccheck_devel"] = dev.group(1)
        elif "biocthis" in name:
            if rel:
                out["biocthis_release"] = rel.group(1)
            if dev:
                out["biocthis_devel"] = dev.group(1)
        elif "bioc-actions" in name and tag:
            out["bioc_actions"] = tag.group(1)
    return out


def mapped_slugs() -> dict[str, str]:
    """slug -> knowledge file (or a 'not summarized' note), from the SOURCES.md chapter map."""
    out = {}
    for line in read("knowledge/SOURCES.md").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        _rmd, slug, _ch, target = cells
        slug = slug.strip("`")
        if slug != "-":
            out[slug] = target
    return out


def rmd_to_slugs() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in read("knowledge/SOURCES.md").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        rmd, slug, _ch, target = cells
        out.setdefault(rmd.strip("`"), []).append(f"{slug.strip('`')} -> {target}")
    return out


# --------------------------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------------------------

def check_commit_drift(res) -> None:
    """pkgrevdocs has moved: report which summaries the changed chapters map to."""
    pinned = pins().get("pkgrevdocs")
    if not pinned:
        res.fail("knowledge/SOURCES.md: no pkgrevdocs commit pin found")
        return
    head = fetch_json("https://api.github.com/repos/Bioconductor/pkgrevdocs/commits/devel")
    current = head["sha"]  # type: ignore[index]
    if current == pinned:
        return

    compare = fetch_json(
        f"https://api.github.com/repos/Bioconductor/pkgrevdocs/compare/{pinned}...{current}"
    )
    changed = [f["filename"] for f in compare.get("files", [])]  # type: ignore[union-attr]
    table = rmd_to_slugs()
    affected = sorted({t for name in changed for t in table.get(name, [])})
    res.fail(
        "pkgrevdocs moved from {} to {}. Changed files: {}. Affected summaries: {}. "
        "Compare: https://github.com/Bioconductor/pkgrevdocs/compare/{}...{}".format(
            pinned[:7], current[:7],
            ", ".join(changed) or "(none reported)",
            ", ".join(affected) or "(none mapped - check for a new chapter)",
            pinned, current,
        )
    )


def check_url_liveness(res) -> None:
    """Every canonical chapter URL cited by a summary still resolves."""
    cited = set()
    for dirpath, _dirs, names in os.walk(os.path.join(ROOT, "knowledge")):
        for name in names:
            if not name.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
            cited.update(re.findall(rf"{GUIDE}/([A-Za-z0-9._-]+)\.html", read(rel)))
    for slug in sorted(cited):
        code = status(f"{GUIDE}/{slug}.html")
        if code != 200:
            res.fail(f"{GUIDE}/{slug}.html returned {code} - chapter renamed or removed")


def check_quotations(res) -> None:
    """Load-bearing rules are quoted verbatim from upstream, in both places."""
    for claim in CLAIMS:
        quote = normalize(claim["quote"])
        try:
            upstream = chapter_text(claim["slug"])
        except OSError as exc:
            res.fail(f"cannot fetch {claim['slug']}.html: {exc}")
            continue
        if quote not in upstream:
            res.fail(
                f"upstream {claim['slug']}.html no longer contains {claim['quote']!r} "
                f"({claim['note']}) - re-read the chapter before touching {claim['file']}"
            )
            continue
        if quote not in normalize(read(claim["file"])):
            res.fail(
                f"{claim['file']} must quote upstream verbatim: {claim['quote']!r} "
                f"({claim['note']}). Paraphrasing here is how a recommendation "
                "silently becomes a requirement."
            )


def check_tracker_gate(res) -> None:
    """The submission tracker's checklist, not our prose, defines the gate."""
    pinned = pins().get("contributions")
    latest = fetch_json(
        "https://api.github.com/repos/Bioconductor/Contributions/commits"
        "?path=issue_template.md&per_page=1"
    )
    current = latest[0]["sha"]  # type: ignore[index]
    if pinned and current != pinned:
        res.fail(
            f"Contributions/issue_template.md moved from {pinned[:7]} to {current[:7]}. "
            "This template is the authoritative submission checklist - read the diff in full "
            "and update the gate in AGENTS.md, SKILL.md and agents/bioc-package-review.md. "
            "https://github.com/Bioconductor/Contributions/commits/devel/issue_template.md"
        )

    template = normalize(fetch(TRACKER_TEMPLATE))
    for quote, files in TRACKER_QUOTES:
        if normalize(quote) not in template:
            res.fail(f"issue_template.md no longer says {quote!r} - the gate wording is stale")
            continue
        for path in files:
            if normalize(quote) not in normalize(read(path)):
                res.fail(f"{path} does not carry the tracker's own wording {quote!r}")


def check_chapter_coverage(res) -> None:
    """A chapter added upstream is invisible to every per-file check, so diff the whole list."""
    index = fetch(f"{GUIDE}/index.html")
    upstream = []
    for m in re.finditer(r'href="([A-Za-z0-9._-]+)\.html"', index):
        if m.group(1) not in upstream:
            upstream.append(m.group(1))
    known = mapped_slugs()
    for slug in upstream:
        if slug not in known:
            res.fail(
                f"upstream chapter {slug}.html is absent from the SOURCES.md map - "
                "either summarize it or record it as deliberately not summarized"
            )
    for slug in known:
        if slug not in upstream and slug != "index":
            res.warn(f"SOURCES.md maps {slug}, which no longer appears in the guide TOC")


def check_tool_pins(res) -> None:
    """BiocCheck, biocthis and bioc-actions releases move independently of the guide."""
    recorded = pins()
    views = {}
    for channel in ("release", "devel"):
        pkg = None
        for line in fetch(f"https://bioconductor.org/packages/{channel}/bioc/VIEWS").splitlines():
            if line.startswith("Package:"):
                pkg = line.split(":", 1)[1].strip()
            elif line.startswith("Version:") and pkg in ("BiocCheck", "biocthis"):
                views[f"{pkg.lower()}_{channel}"] = line.split(":", 1)[1].strip()

    for key, label in (
        ("bioccheck_release", "BiocCheck release"),
        ("bioccheck_devel", "BiocCheck devel"),
        ("biocthis_release", "biocthis release"),
        ("biocthis_devel", "biocthis devel"),
    ):
        current = views.get(key)
        if current and recorded.get(key) and current != recorded[key]:
            res.warn(
                f"{label} is now {current}, pinned at {recorded[key]} in knowledge/SOURCES.md"
            )

    tags = fetch_json("https://api.github.com/repos/grimbough/bioc-actions/tags?per_page=1")
    if tags:
        newest = tags[0]["name"]  # type: ignore[index]
        if recorded.get("bioc_actions") and newest != recorded["bioc_actions"]:
            res.warn(
                f"bioc-actions latest tag is {newest}, pinned at {recorded['bioc_actions']} - "
                "read the action.yml diff before bumping .github/workflows/verify.yml"
            )


NETWORK_CHECKS = [
    ("commit-drift", check_commit_drift),
    ("url-liveness", check_url_liveness),
    ("quotations", check_quotations),
    ("tracker-gate", check_tracker_gate),
    ("chapter-coverage", check_chapter_coverage),
    ("tool-pins", check_tool_pins),
]
