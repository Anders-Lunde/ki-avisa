# KI-redaksjonens daglige arbeid

Eierens presisering 31.10.2026: KI-journalistene utfører arbeidet, Anders Lunde
er eier. Les [ARBEIDSKORT.md](ARBEIDSKORT.md) først, og REDAKSJON.md og KILDER.md
når oppgaven krever det. Fra eierinstruksen 7.11.2026 er selvstendig e-postsending
stanset: hver utgående e-post krever eierens uttrykkelige godkjenning, i alle saker.
Se REDAKSJON.md og kontrollen under «Saksarbeid og korrespondanse». Oppgaven er å
gjennomføre researchen, ikke gi eieren eller leserne en oppskrift.

## Faste kjøringer

| Kjøring | Hva den gjør | Status |
|---|---|---|
| Daglig 08.00 | Forfalte oppfølginger i sakene først, deretter YouTube-inntak etter [YOUTUBE_DRIFT.md](YOUTUBE_DRIFT.md). | Aktiv siden 31.10.2026. |
| Søndag 10.00 | Ukeoversikt, sveip over kontrollorganer og redaksjonsmøte (under). | Aktiv siden 31.10.2026; redaksjonsmøtet ble lagt til 31.10.2026. |
| Tirsdag 09.00 | Ukentlig saksarbeid (under). | Aktiv fra 31.10.2026; første planlagte kjøring 3.11.2026. |

Tidene er Europe/Oslo og forutsetter at maskinen og Codex-appen er tilgjengelige.
En konfigurert kjøring er ikke bevis på at den har lykkes; les kjøringens egne
kvitteringer. Svar som kommer mellom kjøringene, er ikke lest før neste kjøring.
Det er ingen kontinuerlig postkontroll, og ingen sak skal være avhengig av den.
Ingen fast kjøring publiserer, laster opp eller produserer film på egen hånd.

Fra 1.11.2026 er de tre faste kjøringene selvstendige planlagte oppgaver: hver
kjøring starter i en ny chat i `J:\CODE_REPOS\KI-avisa`, uten denne samtalens
historikk. De bruker den lokale hovedmappen, slik at private saksfiler og arkiv
er de samme mellom kjøringene. Resultater vises som egne kjøringer under
«Planlagt» i appen. Tidsplanen er uendret. Kjøringsagenten bruker GPT-6.1 Sol
med `xhigh`; journalistikkfasene løser fortsatt sine roller og modeller fra
kanalfilen.

Prosjektminnet er filene, ikke forrige chat: les ARBEIDSKORT.md og oppgavens
driftsavsnitt, siste relevante brief og nødvendige saksfiler. For hver sak gir
`editorial_review.md` bestilling, siste beslutning og neste handling;
`reporting.md` gir kontakt og frister; `writer_handoff.md` og kildekvitteringene
gir underlaget. Åpne lengre dokumenter og originalkilder når oppgaven krever
dem. Ikke les gamle chattråder eller sesjonslogger for å gjenskape kontekst i
vanlige redaksjonelle kjøringer. Før nye funn, reelle feil og neste handling i
de eksisterende filene før avslutning. Hver kjøring kontrollerer fortsatt for
duplikater og faktisk levering før ny handling.

## Redaksjonsmøte (søndag)

Møtet er slutten på den ukentlige oversikten. Det tar beslutningene; saksarbeidet
utfører dem.

1. Les hver saksmappe under `v5/workspace/journalism/innsyn/`: siste daterte
   beslutning, «Bestilling», frister i `reporting.md` og siste `writer_handoff.md`.
2. Før en datert beslutning i hver sak: **undersøk nå** med neste konkrete steg,
   **følg med** til en navngitt dato eller hendelse, eller **parker** med grunn og hva
   som kan åpne saken igjen. Er ingenting endret, holder én linje om det.
3. Åpne en ny sak med `journalism_desk init` bare når et spor består bestillingstesten
   i ARBEIDSKORT.md, og skriv bestillingen øverst i sakens `editorial_review.md`.
   Prioriter gravende saker og etterprøving etter STRATEGI.md. Hold sakslisten liten
   nok til at saksarbeidet faktisk kan ta den videre.
4. Pek ut **én sak** som tirsdagens saksarbeid skal ta videre, med fasen det skal
   begynne med. Finnes ingen sak som er klar, si det rett ut.
5. En film bestilles bare etter filmprøven i STRATEGI.md, ved å skrive det inn i
   sakens bestilling. Filmproduksjon er en egen, bevisst kjøring (se README.md).
6. Skriv beslutningene til slutt i ukebriefen med lenker til sakene.

## Ukentlig saksarbeid (tirsdag)

1. Kontroller at saksarbeid ikke allerede kjører: en `runs/*/status.json` med
   `running` i en saksmappe betyr at en fase pågår. Ikke start et duplikat.
2. Ta saken redaksjonsmøtet pekte ut. Mangler det, ta saken med et innkommet,
   vesentlig svar eller nærmeste frist, ellers den sterkeste bestillingen.
3. Før saken så langt den faktisk er klar, i denne rekkefølgen:
   `research` → `article` → `review` → `revision` → `verify`. Lag hver oppgave og kjør
   den med kanalens rolle:

   ```powershell
   python agenthouse.py journalism task --case-root v5/workspace/journalism/innsyn/<sak> --phase research
   python agenthouse.py journalism run-task --task <oppgavefilen fra forrige kommando>
   ```

   Les handoffen (sakens filer og `runs/<oppgave>/last_message.md`) før neste fase.
   Hopp over faser som ikke trengs: `revision` og `verify` bare når kontrollen krever
   retting. Nye svar eller dokumenter i en sak med artikkel starter med `research`.
4. Stopp ved første reelle venting: svarfrist, manglende dokument, eller anbefaling om
   å vente eller parkere. Før datert neste handling i sakens `editorial_review.md`.
5. Overleverer en fase en utsending, kontroller først e-postinstruksen 7.11.2026
   etter «Saksarbeid og korrespondanse» under, også når oppgaven ble laget før
   instruksen. Klargjør meldingen for eierens uttrykkelige godkjenning; send bare
   etter godkjenning av den konkrete meldingen og mottakerne. Hold resten tilbake
   som utkast og før kontaktgapet; ikke be eieren sende. Mangler verktøyene for en
   godkjent utsending, før det som en mangel.
6. Etter `verify` eller en kontroll som sier klar: før **KI-redaktørens beslutning**
   kort i `editorial_review.md`: privat kontrollert utkast, venter på navngitt svar,
   eller parkert. Offentlig utgivelse krever etablert lansering (REDAKSJON.md).
7. Oppdater eiervisningens kilde `v5/sites/innsyn/preview/activity.json` fra faktiske
   kvitteringer når status har endret seg (README for nettstedet). Ikke publiser
   eller deploy; det gjøres i en økt med Sites-verktøyene.
8. Rapporter hva som faktisk ble gjort, hva som venter og neste dato.

Én fase har en tidsgrense på 60 minutter som standard (`--timeout-minutes`). En
mislykket fase gir `status: failed` i sin kjøremappe og stopper saksarbeidet; ikke
start den på nytt uten å ha lest kvitteringen.

## Saksarbeid og korrespondanse

**Før enhver utsending, også klargjorte meldinger og retry:** Les eierinstruksen
7.11.2026 i REDAKSJON.md. Hver e-post krever eierens uttrykkelige godkjenning av
den konkrete meldingen, alle mottakere og vedlegg. Dette gjelder også eksisterende
saker, svar, purringer, klager og imøtegåelse. Klargjør alt for gjennomgang før
godkjenning bes om, og før godkjenningen privat i `reporting.md`. Endret innhold,
vedlegg eller mottakere krever ny godkjenning. Stående mandat, eldre oppgaver og
frister gir ingen sendefullmakt. Ikke omgå kravet med annen avsender eller tjeneste.
Uten godkjenning: før «ikke sendt – venter på eierens uttrykkelige godkjenning»
og hva kontaktgapet betyr, fortsett uavhengig research og avgrens eller vent/parker
dersom nødvendig dokumentasjon eller imøtegåelse mangler. Overlever bare som
utkast som venter på godkjenning. Lesing av relevante innkomne svar fortsetter.
En ny utsending ved retry krever egen godkjenning; kontroller først faktisk levering.

De tre eksisterende planlagte redaksjonskjøringene fikk samme godkjenningskrav
uttrykkelig inn i promptene 7.11.2026. Tidspunkter, modeller, prosjekt og aktive
statuser ble beholdt. Dette er ingen sendekvittering.

1. Les aktive saksmapper i `v5/workspace/journalism/innsyn/`. Velg konkret neste
   handling ut fra dokumentmangler, innkomne svar og frister. Les forrige
   beslutning før nye spor prioriteres; en mappe alene er ikke en aktiv sak.
   Fortsett åpne kildesøk mens en annen del av saken venter på svar.
2. Kontroller Gmail-profilen mot kanalens `correspondence.from_address`. Les
   eksisterende sendekvitteringer og tråder før en ny henvendelse. Søk bare etter
   relevant korrespondanse; ikke samle eierens øvrige e-post som research.
3. Finn mottakerens offisielle adresse og før adressekilden i `reporting.md`.
   Skriv presist innsynskrav eller spørsmål med korrekt sak, formål og frist.
   Oppgi KI-redaksjonen og eieren sannferdig. Bruk journalism_desk `request-prepare`
   med kanalfil. Legg frem nøyaktig melding, mottakere og vedlegg for eierens
   uttrykkelige godkjenning; kall `mail-payload` først når godkjenningen foreligger.
4. Send med den tilkoblede Gmail-tjenesten bare etter godkjenning av den konkrete
   utsendingen etter kontrollen over. Lagre den faktiske leverandørresponsen og
   kall `record-sent` med neste oppfølgingsdato
   etter tidsreglene i REDAKSJON.md (fem arbeidsdager for et innsynskrav).
   Ved usikker levering: kontroller Sendt/tråden før ny utsending.
5. Les relevante svar og vedlegg i riktig tråd. Bevar originalen privat, før
   kildehenvisning, vurder hva svaret faktisk dokumenterer og oppdater påstander
   og tidslinje. Klargjør purring, presisering eller begrunnet klage ved behov;
   hver utgående melding krever egen uttrykkelig godkjenning. Ikke
   røp fortrolige kilder eller send uvedkommende personopplysninger. Er svaret
   vesentlig for et utkast, før det som neste handling for saksarbeidet.
6. Utarbeid journalistikken når dokumentasjonen bærer den, gjennom fasene i
   «Ukentlig saksarbeid». Researcher, forfatter og kontroll følger kanalens løste
   roller. Lansering bruker bare den faktisk konfigurerte kanalidentiteten; ingen
   opplastingskonto skal gjettes.

Avslutt et saksarbeid med hva som faktisk ble avklart eller utført, hvilke
påstander det endrer, og neste handling med dato eller utløsende hendelse.
Oppdater sakens eksisterende `editorial_review.md` og kontaktlogg, ikke et nytt
styringssystem. «Mer research» alene er ingen handoff. Gjenta ikke uendret
research bare for å holde saken aktiv. Ved fortsatt blokkering: navngi den
avgjørende mangelen, gjør den lovlige neste handlingen som er mulig nå, og
avgrens eller parker resten. Et nødvendig eieravklaringspunkt skal ha konkret
grunnlag og gjelde mandat, tilgang, ressursbruk eller lansering, ikke vanlig
rapportering eller godkjenning av hver artikkel.

## Daglig og ukentlig kildeinntak

Eieren valgte **daglig YouTube-inntak og ukentlig oversikt** 31.10.2026.
Konkrete kommandoer, arkiv og arbeidsoppdrag står i [YOUTUBE_DRIFT.md](YOUTUBE_DRIFT.md).
Nye videoer og tilgjengelige transkripsjoner skal gi tips, påstander å kontrollere,
originalkilder å oppsøke og oversikt over andres dekning. Popularitet er ikke
sannhetsbevis. Skill nyhetsrapportering, intervju, kommentar og partsutsagn;
bevar avsender, dato, lenke, tidskode og transkripsjonens opprinnelse. Vurder
relevansen semantisk, ikke gjennom en liste med politiske nøkkelord.

KI-redaksjonen velger selv videre saker ut fra mandat, offentlig interesse,
dokumentasjon og hva som kan tilføre publikum noe. En kildevideo oppretter ikke
automatisk en ny produksjonsbestilling eller gjør dens påstander til fakta.
Ukentlig oversikt skal peke ut nye funn/leads, gjentatte kildekjeder, motsigelser,
manglende transkripsjoner og konkrete neste journalistiske handlinger, og ender
med redaksjonsmøtet.

Den daglige kjøringen begynner med **forfalte oppfølginger**: sendte henvendelser i
`reporting.md` der oppfølgingsdato eller klagefrist er i dag eller passert. Les
tråden, purr, vurder klage og før resultatet i saken før nytt kildeinntak tar tid.
Er Gmail-verktøyene ikke tilgjengelige i kjøringen, skriv det som en mangel i
dagbriefen; ikke skriv «ingen svar». Vis planlagt og faktisk utført arbeid hver
for seg i rapporten til eieren og i nettstedets daterte status.


## Migrering 4. november 2026 – gjeldende arbeidsrot

Arbeidet skjer i `J:/CODE_REPOS/KI-avisa`. Bruk `python agenthouse.py` for
AgentHouse-verktøy. De tre eksisterende automasjonene er oppdatert med denne
arbeidsroten, KI-avisa-navnet og skillet mot KI-partiet, uten endring i tid,
modell eller id. Appens registrerte startprosjekt er fortsatt AgentHouse;
prompten krever bytte til KI-avisa før fil-/CLI-arbeid. Det er ikke en annen
aktiv arkivkopi. Ingen ny jobb eller offentlig deploy er laget.

Ta også forfalte, allerede mandaterte utsendinger med leveringsfeil i
reporting.md før nytt inntak, men ikke send på nytt uten egen uttrykkelig
eiergodkjenning etter instruksen 7.11.2026. Kontroller Sendt/tråden før eventuell retry og
bruk den eksisterende forberedte meldingen. Kvotefeil er ikke bekreftet sending.
