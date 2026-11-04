# KI-avisa (tidligere Innsyn)

Start i [arbeidskortet](ARBEIDSKORT.md). Derfra brukes
[redaksjonsmandatet](REDAKSJON.md), [kildene](KILDER.md), [driften](DRIFT.md),
[strategien](STRATEGI.md) og [YouTube-inntaket](YOUTUBE_DRIFT.md).
Prosjektskillet står i [RETNING.md](RETNING.md).

Lokal hovedmappe er `J:/CODE_REPOS/KI-avisa`. Bruk `python agenthouse.py`;
det kjører med AgentHouse-Python og setter riktig prosjektrot. Eksempler:

```powershell
python agenthouse.py journalism task --case-root v5/workspace/journalism/innsyn/<sak> --phase research
python agenthouse.py journalism run-task --task <oppgave>
python agenthouse.py intake collect --config v5/config/source_watch/innsyn_youtube.yaml
```

Nettstedets builder er prosjekteid, ikke et delt AgentHouse-verktøy. Kjør den
direkte med `..\AgentHouse\.venv\Scripts\python.exe v5/sites/innsyn/build.py`.
Se [nettstedets README](../../sites/innsyn/README.md). Den eksisterende private
Sites-identiteten er bevart bare her; ingen deploy er utført ved migreringen.

Korrespondansemandatet og plikten til faktiske Gmail-kvitteringer står fast.
Private arkiver og lokale avsenderinnstillinger følger ikke GitHub. Navnet
KI-avisa er valgt av eieren, men offentlig kanalidentitet, redaktør og
kontaktadresse må fortsatt etableres før offentlig lansering.
