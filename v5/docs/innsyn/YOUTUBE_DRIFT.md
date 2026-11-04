# YouTube som daglig researchkilde

Valgt rytme: **daglig innhenting kl. 08.00 og ukentlig oversikt søndag kl. 10.00,
Europe/Oslo**. Kalenderen ligger i Codex-appens automasjoner. Lokal gjennomføring
krever at maskinen og appen er tilgjengelige. Hver kjøring starter i en ny chat
i den lokale prosjektmappen; nødvendig kontekst hentes fra filene etter
ARBEIDSKORT.md og DRIFT.md. Dette er kildearbeid, ikke automatisk
publisering eller en ny episodebestilling for hvert videofunn.

Les `ARBEIDSKORT.md` og `v5/skills/youtube_source_intake/SKILL.md`. Bruk
`DRIFT.md` for oppfølginger og korrespondanse, og `REDAKSJON.md` og `KILDER.md`
når et spor krever det. Jobb fra `J:\CODE_REPOS\KI-avisa`
med `.\.venv\Scripts\python.exe`. Registeret er
`v5/config/source_watch/innsyn_youtube.yaml`; privat arkiv er
`v5/workspace/source_intake/innsyn/youtube/`.

Inntaket er best til tre ting: påstander som sprer seg og kan avklares mot en
original, levende debatter der tall kan avgjøre en del av uenigheten, og andres
journalistikk som skal krediteres. Gravende saker og etterprøving kommer oftere
fra dokumenter, derfor sveipet over kontrollorganene i ukeoversikten.

## Daglig inntak

0. Se først etter forfalte oppfølginger i `reporting.md` i saksmappene og ta dem etter
   DRIFT.md før noe nytt. Finnes ingen sendte henvendelser, er det intet å gjøre.
1. Les siste dagbrief, `latest_run.json` og åpne feil fra tidligere run. Kontroller
   at et inntak ikke allerede kjører; ikke start et parallelt duplikat. Ta med
   tidligere prioriterte tekster som ennå ikke er lest. Vurder dem før nye
   metadatafunn fortrenger dem; velg hva som fortsatt fortjener lesetid.
2. Kjør `python agenthouse.py intake collect --config v5/config/source_watch/innsyn_youtube.yaml`.
   Standardvinduet er sju døgn for å fange forsinkede undertekster og korte driftsavbrudd.
   Hvis siste vellykkede kontroll er eldre, utvid vinduet eksplisitt med `--days`.
   Les delvise feil og API-kvoter; ikke kall en ufullstendig kontroll fullført.
3. Sammenhold video-ID-er med tidligere `selection.json` og tilhørende kandidater
   før hele kandidatlisten legges i LLM-konteksten. Bruk eksakt sammenlikning til
   bokføringen. Gjenbruk en tidligere begrunnet vurdering når tittel, beskrivelse,
   avsender og publiseringsdato er uendret og ingen konkret ny opplysning eller
   aktiv sak gir grunn til å åpne den igjen. Endrede visnings-/abonnenttall alene
   krever ingen ny vurdering. Mangler tidligere vurdering eller underlag, vurder
   videoen som ny. Les faktiske metadata for nye og endrede kandidater, og velg
   semantisk relevante nyheter, samtaler, politikk og undersøkelser etter mandatet.
   Skriv `selection.json` med begrunnelse per valgt og fravalgt video. Ved gjenbruk
   videreføres begrunnelsen med lenke til vurderingen der den først ble gjort;
   unngå kjeder av henvisninger gjennom hver mellomliggende dag.
   Prioriter hele originalintervjuet fremfor mange klipp fra samme samtale.
   Velg med tanke på hva redaksjonen rekker å lese og følge opp. Hentede tekster
   som ikke blir lest, merkes fortsatt som ulest; de er ikke ferdige researchfunn.
   Et politisk ubalansert døgn er ikke grunn til å finne på en motvekt eller
   gi alle meninger lik bevisverdi. Sjekk bredere kilder til den konkrete saken.
4. Kjør `fetch --run-root <run> --selection <run>/selection.json`. Les kvitteringene.
   Skill teknisk feil, manglende tekst og faktisk lest transkripsjon. Ikke bruk
   Qwen-ASR til norsk. Manglende opptak/tekst beholdes som tydelig gap og prøves
   igjen fra original-run, også etter at videoen faller utenfor dagens vindu.
5. Les nye og tidligere uleste tekster som skal inngå i dagbriefen. For allerede
   analyserte tekster brukes eksisterende brief og lesekvittering først. Åpne
   originalen ved nye opplysninger, motstrid, endret transkripsjon eller et konkret
   spørsmål som den tidligere analysen ikke besvarer. Les relevant passasje med
   nok kontekst; les hele teksten når spørsmålet eller mangelfulle notater krever
   det. Det er ingen daglig plikt til å lese alt på nytt. Noter navn, kilde, dato,
   videolenke med relevant `&t=<sekunder>`, transkripsjonens kilde/språk og faktisk
   lest omfang.
   Automatisk tekst er feilbarlig, særlig navn, tall og benektelser. Lytt til
   nødvendig avsnitt før et omstridt sitat brukes som dokumentasjon.
6. Skriv `daily/YYYY-MM-DD.md`: dekning, faktisk hentet/lest omfang og åpne feil;
   skill førstegangslesing, målrettet gjenlesing og gjenbrukt analyse. Lenke til en
   eldre lesekvittering er ikke ny lesing. Ved gjenlesing: noter kort spørsmålet
   og faktisk lest omfang i dagens lesekvittering eller brief.
   Oppgi gjenbrukte utvalgsbeslutninger som et samlet antall, med sporbarhet i
   `selection.json`, fremfor å gjenta alle begrunnelser i briefen.
   Beskriv deretter de få sporene som fortjener oppmerksomhet. For hvert prioritert spor:
   attribuert påstand, publikumets interesse, hva egen journalistikk kan tilføre,
   avgjørende originalkilde og beslutning **undersøk nå**, **følg med** eller
   **parker**. Før neste konkrete kildekontroll, hendelse eller begrunnelse.
   Skillet er redaksjonelt skjønn, ikke en poengsum eller obligatorisk ny sak.
   Oppdater relevante eksisterende saksmapper og lenk dit; ikke lag parallelle
   handlingslister. Bevar tidskoder, motforestillinger, duplikate kildekjeder og
   tilgangsgap. En påstand fra en kildevideo er ikke redaksjonens konklusjon.
   En stille dag gir en kort brief; ikke lag sammendrag av hver video. Nye saker
   opprettes i redaksjonsmøtet, ikke i det daglige inntaket.
7. Rapporter kort hva som faktisk ble hentet/lest og eventuelle feil. Ingen nye
   abonnementer, betalte kjøp eller publisering følger av kildeinntaket.

## Ukentlig oversikt

Les siste sju døgns dagbriefer og kontroller utvalg og kvitteringer for dekning og
åpne mangler. Bruk eksisterende analyser først. Gå tilbake til originalpassasjer
som trengs for nye beslutninger, motstrid, kildekontekst eller kontroll av et
avgjørende poeng; les hele teksten når det kreves. Les ikke alle tidligere
analyserte transkripsjoner på nytt som en rutine. Gjenbruk merkes som gjenbruk,
og faktisk ny lesing føres med omfang og grunn. Skriv
`weekly/YYYY-MM-DD.md` med presist datointervall og faktisk dekningsgrad.

Som ukentlig sikkerhetsnett: gjør én kort tittelsjekk av tidligere fravalgte
videoer i ukens innsamlede kandidatmateriale, også dem som nå er utenfor dagens
sjudøgnsvindu. Vurder dem sammen med endringer i aktive saker og ulest restanse.
Åpne bare beskrivelse eller tekst når et konkret spor fortjener ny vurdering.
Et kapasitetsbegrunnet fravalg er ikke en permanent redaksjonell avvisning.
Sjekken gir ingen kvote for nye saker eller ny lesing.

Velg de viktigste nye researchsporene ut fra offentlig interesse, dokumentasjon
og originalt bidrag. For hvert spor: hva ble hevdet, hvem er opprinnelig avsender,
hvilke tidskoder støtter sammendraget, hva er motbeviset/uenigheten, hvilken
originalkilde eller hvilket datasett kan avklare spørsmålet, og hva gjør
KI-journalisten videre? Flere omtaler av én original er én kildekjede.

Begynn med hva som har endret seg siden forrige prioritering: avklart, avkreftet,
fortsatt verdt å undersøke eller parkert. Les de eldre prioriterte tekstene som
ennå mangler analyse når de kan avklare et viktig spørsmål; ikke la restansen
vokse skjult bak nye hentetall. Et rolig døgn eller en uke uten sterke nye spor
skal sies rett ut. Ikke lag en sakskvote eller et sammendrag av hver video.
Se kildeutvalget opp mot mandatet: mange klipp om en strid viser dekning i
dette utvalget, ikke nødvendigvis hva som er viktigst i Norge. Oppsøk relevante
originaldokumenter og erfaringer utenfor videostrømmen når et prioritert spor
trenger det. Ingen partipolitisk motkvote eller registerutvidelse kreves.

**Ett sveip utenfor YouTube.** Utvalget er tungt på samtaler og kommentar, mens
kanalens kjerne (korrupsjon, lovbrudd, maktmisbruk, politi og domstoler, offentlige
penger) først og fremst ligger i dokumenter. Se derfor også over hva kontrollorganene
og påtalemyndigheten selv har publisert siden forrige oversikt: Riksrevisjonens
rapporter, Sivilombudets uttalelser, KOFA-avgjørelser, Spesialenhetens avgjørelser
og Økokrims pressemeldinger (adresser i KILDER.md). Les det som er relevant, ikke
bare overskrifter. Skriv i ukesbriefen hva som ble sett over og hva som faktisk ble
lest. Før bare spor som er verdt et spørsmål inn i en saksmappe, med originalen som
kilde. Stille uker sies rett ut. Dette er kilder til spor, ikke en dagsorden eller
en kvote, og ingen myndighet er riktig fordi den publiserer.

Vis manglende tekst og skjevheter i faktisk kildeutvalg. Kontroller kanalregisteret
mot verifiserte kanal-ID-er og aktuelle metadata når det trengs. Abonnenttallene
er avrundede API-tall fra en datert kontroll, ikke mål på sannhet eller en
fullstendig rangering av all norsk politisk journalistikk.

Avslutt med **redaksjonsmøtet** i DRIFT.md: en datert beslutning for hver sak, nye
saker bare når et spor består bestillingstesten i ARBEIDSKORT.md, og én sak pekt ut
til tirsdagens saksarbeid. KI-redaksjonen kan selv opprette og undersøke en sak og
sende nødvendige henvendelser under stående mandat. Ikke gi eieren eller leserne
oppgavene med å be om innsyn.

Denne gjenbruken gjelder rutinemessig kildeinntak. Den uavhengige kontrollen av
en artikkel skal fortsatt lese de avgjørende originalkildene; en tidligere
dagbrief erstatter ikke dokumentasjon for en publiserbar påstand. Tilgangsfeil
og prioriterte uleste tekster er fortsatt åpne oppgaver, ikke ferdige analyser.

## Første kontroll

31.10.2026: 17 konfigurerte kanaler kontrollert, 50 nye videoer i et avgrenset
todøgnsvindu, 20 valgt ved redaksjonelt skjønn og 20 transkripsjoner lagret med
tidskoder. Alle disse kom fra automatiske undertekster; ingen norsk ASR ble
brukt. Dette dokumenterer henting, ikke at alle påstander er faktasjekket.
Detaljer ligger i arkivets `daily/2026-10-31.md` og run-kvitteringene.


## Migrering 4. november 2026 – gjeldende arbeidsrot

Arbeidet skjer i `J:/CODE_REPOS/KI-avisa`. Bruk `python agenthouse.py` for
AgentHouse-verktøy. De tre eksisterende automasjonene er oppdatert med denne
arbeidsroten, KI-avisa-navnet og skillet mot KI-partiet, uten endring i tid,
modell eller id. Appens registrerte startprosjekt er fortsatt AgentHouse;
prompten krever bytte til KI-avisa før fil-/CLI-arbeid. Det er ikke en annen
aktiv arkivkopi. Ingen ny jobb eller offentlig deploy er laget.

Ta også forfalte, allerede mandaterte utsendinger med leveringsfeil i
reporting.md før nytt inntak. Kontroller Sendt/tråden før eventuell retry og
bruk den eksisterende forberedte meldingen. Kvotefeil er ikke bekreftet sending.
