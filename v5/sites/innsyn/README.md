# Innsyn article site

The owner requested the actual public website on 4 November 2026, confirmed
Anders Lunde as responsible editor and lunde.anders@gmail.com as public contact,
and authorized use of the existing design. https://ki-avisa.pages.dev/ now
serves the clean public export, with zero published articles at deployment.
See `docs/HOSTING.md` for deployment details. `holding/` is historical.

Public builds use `build.py --output public`, followed by `check_public.py`.
Only generated `public/` is uploaded to Cloudflare. Preview builds cannot target
that output. The existing private `dist/` and Sites preview are preserved.

After an actual editorial publication decision and public-export review,
`publish.py prepare --reviewed-by <actual reviewer>` records exact export
hashes. The active local monitor invokes `publish.py run` every 6 hours.
It deploys matching changed releases once, skips unchanged/unreviewed exports
and never changes editorial decisions. See `docs/HOSTING.md`. `assets/` contains
only public favicon files and the social image. Public SEO metadata and sitemap
are generated; private previews retain noindex.

Buildless static article site. `content/*.json` contains only text deliberately
prepared for readers. Never point it at a case directory or raw correspondence.
`build.py` validates source URLs and escapes text; `dist/` is generated output.
No external scripts, tracking, tip form or invented contact. The hosted preview
uses the existing owner-only Sites access gate; the static app adds no account UI.

From the repository root, using the project's Python environment:

```powershell
.\.venv\Scripts\python.exe v5/sites/innsyn/build.py --preview --auditions v5/experiments/innsyn_voice_20261031
```

The preview includes draft articles (marked «Utkast»), a noindex notice and
internal voice tests. The front page leads with the newest published story;
until one exists it leads with the editorial promise, never with a draft.
`stemmer.html` lists every sample registered in the audition folder's
`samples.json`, grouped by provider (`#gemini`, `#speechify`). The build fails
if a registered sample has no completed result or audio, or if `results.json`
reports errors. Samples may set `display_name` and `provider`; Gemini samples
without `provider` are recognised by model ID.
`voices.js` adds provider filtering and a two-sample comparison without changing
the audio, its URLs, or the audition registry. Playing one sample pauses the
others. Selection lasts only for the current page and is not a voice approval.
All players, the transcript and download links work without JavaScript.
The audition registry's `listening_status: selected_for_channel` records the
owner's permanent voice choice. The owner and listening pages display it;
comparison controls do not change that recorded choice. Kore · journalistisk
was selected on 31 October 2026, matching the channel's Gemini Flash batch
voice/direction settings. The builder rejects multiple permanent selections.

The preview-only `redaksjonen.html` shows article/audio counts from the build.
An optional `preview/activity.json` supplies a deliberately prepared, safe
activity snapshot: `updated_at` (ISO timestamp with timezone), `items` (each
with text `label`, `value`, `detail`) and text `notes`. The renderer dates it
and labels it as a snapshot, never live status. Missing snapshot data is shown
as unavailable; malformed supplied data fails the build. Do not feed the builder
raw case files or Gmail data. The snapshot must distinguish configured inputs,
completed actions, receipt coverage and unresolved work. The JSON itself is not
copied to `dist/`. Public builds omit the owner page, voice script and audio.
Optional `priorities` uses the same `label`, `value`, `detail` text fields for a
small, curated description of the newsroom's next work. It is visibly labelled
planned, never a claim of work in progress or an executable task queue. Keep
unperformed work explicit and distinguish retrieved transcripts from texts
actually read. The owner page separates that newsroom work from launch/voice
choices; it has no fake task controls or approval buttons. The snapshot date
is when the view was compiled; each historical count keeps its own scope in
the text. Refresh it from receipts, never by changing only the date.
Optional `schedule` uses the same fields for configured recurring work and its
stated status (for example active, proposed, not automatic). It renders as «Fast
drift», labelled as configuration, never as evidence that a run succeeded. Mark
proposed automations as proposed until they actually exist. The weekly casework
run (docs/innsyn/DRIFT.md) updates this file when status changes; publishing the
owner view is a separate Sites step.

Articles expose a contents navigation, numbered sources with return links to
each citation, source domains, and a permanent changes/corrections section.
Published reporting and method/draft texts occupy separate homepage sections.
AI newsroom attribution does not imply a human byline or owner approval gate.
Host preview builds only in an owner-private Site. `.openai/hosting.json` retains
the Sites project identity; use the Sites skill workflow for source sync,
packaging and publication, never another channel's hosting/OAuth.

For a public build, omit both preview/audition flags and pass `--output public`. Only articles with
`status: published`, `approved_by` and `approved_at` appear. Those fields record
the actual editorial decision under the channel mandate, with the deciding editor/agent and time. They must never be invented. The
builder validates mechanics; it cannot judge evidence, privacy or fairness.
Keep the decision in the private case too. All draft pages and auditions are
removed on a clean rebuild. Editor/contact identity was established by the owner
on 4 November 2026 and is included in the footer and about page. Under the Norwegian
media responsibility act (§§ 3-5, see docs/innsyn/REDAKSJON.md) the editor is a
natural person whose name and contact details readers can see; the footer and
about page must show them at launch, and the builder does not check this.

An article has `slug`, `title`, `deck`, `kind`, `date`, `status`, a `sections`
list (`heading` and plain-text `paragraphs`), `sources` (`title`, `url`) and
optional plain-text `updates`. An actual published film may add `youtube_id`.
Put `[1]`, `[2]`, etc. beside material factual claims in paragraph text. The
numbers refer to the existing `sources` list; the builder makes accessible
links to that numbered list and fails if a reference has no source. Name the
specific document/date/page or table selection in its source title. Include a
short method section for the evidence cutoff, important calculations and
limits. Sources at the foot of a page are not proof that each claim was checked.
No source archive is copied. Source credentials remain in memory, never files.
Articles can stand alone before or without a film. The existing source, reply
and editorial decision requirements apply; a missing film is not a publication
blocker. The site's current public launch configuration must still be established.
