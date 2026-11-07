# KI-avisa

Norsk undersøkende journalistikk om makt, offentlige penger og samfunn.
Prosjektet het tidligere Innsyn; det interne kanalnavnet `innsyn` beholdes for
å bevare saks-ID-er og historiske kvitteringer.

Les [arbeidskortet](v5/docs/innsyn/ARBEIDSKORT.md),
[redaksjonsmandatet](v5/docs/innsyn/REDAKSJON.md),
[driften](v5/docs/innsyn/DRIFT.md) og
[skillet mot KI-partiet](v5/docs/innsyn/RETNING.md).
Saksarkivet, korrespondansen og kildeinntaket ligger lokalt under
`v5/workspace/` og følger ikke GitHub.
Upubliserte artikkeldata under nettstedets `content/` og den private
aktivitetsvisningen holdes også utenfor GitHub.

Prosjektet har samme eier som
[KI-partiet](https://github.com/Anders-Lunde/ki-partiet). KI-partiet utvikler
politiske forslag; KI-avisa bestemmer journalistikken etter sitt eget mandat og
etterprøver også partiprosjektet. Samarbeid gir ikke fri overføring av private
kilder, e-post eller upublisert dokumentasjon.

[AgentHouse](https://github.com/Anders-Lunde/AgentHouse) leverer det delte
Python-miljøet, modellstyringen, research-, data-, papir-, media- og videoverktøyene.
Se [verktøytilkoblingen](docs/AGENTHOUSE.md). Fra denne mappen:

```powershell
python agenthouse.py doctor
python agenthouse.py journalism --help
python agenthouse.py intake --help
```

Den faktiske kanalfilen er lokal og ignorert. For en ny klone: kopier
`v5/config/channels/innsyn.example.yaml` til `innsyn.yaml` og konfigurer
verifisert avsender før korrespondanse. Eieren bekreftet 4. november 2026
Anders Lunde som ansvarlig redaktør og lunde.anders@gmail.com som offentlig
kontakt, og bestilte offentlig nettsted uten private utkast eller internt
materiale. Migreringen publiserer ingen saker og endrer ikke den eksisterende
private nettsidens tilgang.

Det offentlige nettstedet finnes på [ki-avisa.pages.dev](https://ki-avisa.pages.dev/).
Det beholder det eksisterende designet og viser bare offentlig eksport:
forside, metode og kontakt. Ingen artikkelutkast eller privat prøveinnhold er
publisert. Se [hosting og oppdatering](docs/HOSTING.md).
