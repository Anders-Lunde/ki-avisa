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

Private archives, mail originals, licensed papers, credentials, audition audio,
run logs and generated site previews remain local and ignored. GitHub is a
source repository, not a backup of private reporting. Preserve the local archive
and checked migration backup with the project's normal private backup process.
