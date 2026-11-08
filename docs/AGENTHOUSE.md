# Shared AgentHouse tools

Each project owns its mandate, channel configuration, site sources and private
workspace. AgentHouse owns the Python environment, model resolver, prompts,
skills, media tooling and shared resources. No submodule, copied engine or
second virtual environment is needed. `.agenthouse.json` locates the sibling
checkout; change `tool_root` if the checkout moves.

The shared project-root support is in AgentHouse commit `d81f9c50`, available
on `origin/codex/windows`. A fresh AgentHouse clone needs that integration.

From this repository:

```powershell
python agenthouse.py doctor
python agenthouse.py models
python agenthouse.py journalism --help
python agenthouse.py intake --help
python agenthouse.py tool v5/skills/paper_pdf_extract/scripts/paper_pdf_extract.py --help
python agenthouse.py episode --help
```

The bootstrap reexecutes with AgentHouse's `.venv` and loads its existing local
environment without copying credentials. It sets `AGENTHOUSE_PROJECT_ROOT` so
case creation, agent working directories and source-intake archives belong to
this project. Model roles merge AgentHouse's `v5/config/llm.yaml` with this
project's channel file. Never pick a model in a task prompt.

Read the relevant `../AgentHouse/v5/skills/<name>/SKILL.md` before using a skill.
Use `tool <relative-script> <arguments>` for paper discovery/extraction, public
data acquisition, subtitles, media search/download/probing, diagrams, animation,
TTS and video. Give explicit project-local output paths where the skill asks
for them. Shared skill defaults are not an output-routing contract. Episode
commands receive this channel and this project's `v5/workspace/episodes` by
default; choose an explicit episode root when resuming. Source rights,
provenance and synthetic-media labels still apply.

The local `.venv`, `v5/skills`, `v5/scripts`, `v5/lib`, `v5/prompts` and
`v5/resources` junctions are convenience links to the sibling checkout. They
are ignored by Git. The bootstrap works without those links. Old AgentHouse
Innsyn archive paths also link to KI-avisa so immutable historical receipts
remain usable. New work belongs in the new repository; never launch an old
task just because its original path still resolves.

After a fresh clone, install/prepare AgentHouse normally, copy the committed
`*.example.yaml` channel to the corresponding `*.yaml`, and configure local
identity where required. Run `doctor`; missing tools/configuration fail loudly.
The migration was verified against the local AgentHouse checkout on 4 November
2026. Tool availability does not prove that a research or production run was
executed. Publishing, political submissions and video production require their
actual project mandate.

From 4 November 2026, AgentHouse also supplies a shared prior-coverage check in
`v5/prompts/includes/prior_coverage_check.md`. New journalism `research` tasks
and episode research tasks include it automatically, including channel-specific
templates. The check records exact-angle searches, closest original coverage,
actual read scope/access gaps, the concrete audience contribution and a dated
decision before wider research and routine contact. New cases mark the check as
unfinished; existing tasks and historical receipts are preserved. Keep this
project's dated check in the case's `editorial_review.md` and carry it into the
writer handoff. The shared rule supplements the channel's mandate and editorial
guidance; judgment still requires reading the relevant sources.

The shared check also requires a separate audience-value assessment before
commissioning wider work or routine contact: concrete reader payoff, verified
basis and significance, strongest contrary evidence and its effect, and a
proportionate next step or decision to park. New reporting cases mark
`Nyhetsvurdering` unfinished. Renew the assessment before the next inquiry when
new evidence weakens the premise; adding caveats alone does not justify
continuing. This editorial assessment remains the newsroom agent's judgment,
not an automated keyword score. Sending any email separately requires the owner's
explicit approval under the 7 November 2026 instruction below.

Private archives, mail originals, licensed papers, credentials, audition audio,
run logs and generated site previews remain local and ignored. GitHub is a
source repository, not a backup of private reporting. Preserve the local archive
and checked migration backup with the project's normal private backup process.

The owner's 7 November 2026 email instruction in this project's AGENTS.md,
REDAKSJON.md and DRIFT.md limits the shared skill's general correspondence
guidance: autonomous email sending is stopped immediately. Every outgoing email
requires explicit owner approval of that exact message, all recipients and
attachments before sending, in existing and new cases alike. Check the current
rule even for older prepared tasks, queued messages and retries; a prepared
payload or an older authorization receipt is not permission. The local and example
channel configurations now set `autonomous_reporting_authorized: false`.
Keep shared AgentHouse tooling and other channels unchanged.
