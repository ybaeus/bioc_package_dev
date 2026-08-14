# Behavioral evals

Layer 4 of the verification described in the top-level README. The other three layers check what
the files say; these check what the plugin does.

```
claude plugin eval . --ablation with-without --scaffold
claude plugin eval . --case trigger-conversion --verbose
```

`--scaffold` is required for the two agent cases: it runs each case's `scaffold_script`, which
builds the deliberately broken fixture package they audit. The flag is off by default because a
`scaffold_script` is author-supplied shell; these were authored here.

`--ablation with-without` adds a no-plugin baseline arm and reports the delta. That delta is the
evidence, not the absolute score - a model can answer "what version for a new submission" from
memory, and a case that passes equally well without the plugin is a case that is not measuring
this plugin.

## Why these cases

| Case | What breaks if it fails |
|---|---|
| `trigger-conversion` | the skill no longer fires for the audience it was written for |
| `trigger-cran-move` | someone is told they can be on CRAN and Bioconductor at once |
| `trigger-implicit` | the skill only works when the user already knows the word "Bioconductor" |
| `anti-trigger` | the skill fires on everything, spending context and dragging Bioconductor rules into CRAN answers |
| `facts-version` | the single most asked question gets a plausible wrong answer |
| `router-large-data` | large data advice stops at "compress it" instead of ExperimentHub |
| `style-bioc` | generated code uses tidyverse habits and `1:n`, which BiocCheck flags |
| `workflow-after-submission` | the post-submission sequence is missing or out of order |
| `agent-review` | the review agent misses planted defects, or invents ones that are not there |
| `agent-verdict` | the agent hedges instead of answering, or reports a recommendation as a blocker |

The trigger cases are the highest-value three. The `description` field in `SKILL.md` is the
single point of failure that can make the whole plugin inert while every static check still
passes, and nothing but a behavioral eval can see it.

## How the graders are built

Deterministic regex wherever the claim is checkable that way, which is most of them and costs
nothing. LLM graders only on the two agent cases, where the thing being judged is whether a
report is accurate and correctly scoped - and there the criteria name the specific findings that
count and the specific false positives that do not, because a vague criterion just moves the
judgement somewhere it cannot be inspected.

The agent cases grade the content of the answer rather than asserting that the subagent was
spawned. Whether the work happens in the main loop or in `bioc-package-review`, the user-visible
requirement is the same: find the real defects, invent none, and do not claim a check result that
was never measured.

## Keeping this in step with the README

Every prompt in the top-level README's "Example prompts" section appears verbatim as some case's
`execution.prompt`. `scripts/verify.py` enforces it, so a documented prompt is always one CI has
an opinion about, and editing either side without the other fails the static check.

## Not yet executed

`claude plugin eval` is early access and was not available in the CLI on the machine where these
were written, so the cases are authored against the schema the CLI validates against but have
never been run. Expect the first run to need adjustment - most likely to the regex graders, which
assert on phrasing rather than on meaning. The evals job is dispatch-only, so a broken case here
cannot break anything else.
