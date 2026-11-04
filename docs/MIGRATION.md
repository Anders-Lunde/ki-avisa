# Migration receipt · 4 November 2026

The canonical newsroom is now `J:/CODE_REPOS/KI-avisa`, with source repository
`https://github.com/Anders-Lunde/ki-avisa`. Its legacy internal ID is `innsyn`.
Policy development belongs to the separate KI-partiet repository.

The six transferred trees (documentation, site, cases, source intake, brief
queue and voice experiments) contained 1,109 files. Every copied file matched
its original SHA-256 before source-path, mandate and current-status updates.
All original files remain present; pre-migration copies and the exact inventory
are retained privately in AgentHouse's `.codex_tasks/ki_split_20261104/`.
All five prior successful mail receipts still match their original MIME bytes.
No active case run was present during transfer. Old archive paths are local
compatibility junctions, preserving immutable historical receipt references.

The shared-tool integration is recorded in local AgentHouse commit `d81f9c50`
on `codex/windows`: the case tool accepts a project root; source intake routes
archives to it. That commit was pushed to `origin/codex/windows` separately.
This project uses that sibling working checkout; a new machine needs the same
integration before running these workflows. No code or environment is vendored.

Both projects passed role/template resolution, command launch checks for the
video pipeline and PDF extraction, and local Markdown link validation. The
newsroom preview built locally with its retained auditions. These checks do
not assert that a video, external research call or public release occurred.

Three existing scheduled jobs retain their IDs, times, models and active
status. Their prompts now require work in KI-avisa. The app's registered launch
project remains AgentHouse because KI-avisa was not returned by the project
tool; no duplicate job or invented project ID was created. The jobs must
change working directory before action, as their saved prompts explicitly say.

Private workspace, sender configuration, original mail, licensed documents,
draft article data, preview/activity data, auditions and hosting metadata are
ignored by Git. They are preserved locally, not backed up by the GitHub source
push. The existing private Site identity stays here. No deployment or audience
change was performed.
