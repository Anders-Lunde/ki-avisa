# Kilder som kan svare på spørsmålet

Kontrollert 31. oktober 2026. Dette er redaksjonell veiledning for Innsyn, ikke
en påstand om at alle kilder er åpne, fullstendige eller undersøkt i hver sak.
Velg ruter ut fra sakens spørsmål; ingen sak trenger hele katalogen.

Kontaktforslag og tilgangsruter nedenfor gir ikke sendefullmakt. Etter
eierinstruksen 7.11.2026 krever hver utgående e-post eierens uttrykkelige
godkjenning av den konkrete meldingen og mottakerne, i alle saker; se REDAKSJON.md
og DRIFT.md. Fortsett tilgjengelig research mens godkjenning ventes.
UiO-/bibliotekkontakt om eierens tilgang er også underlagt AGENTS.md.

## Daglig dekning fra YouTube

Et datert, verifisert kanalutvalg ligger i
`v5/config/source_watch/innsyn_youtube.yaml`. Det omfatter store nyhetskanaler,
lange politiske samtaler og mindre redaksjonelle kilder. Metadata og avrundede
abonnenttall er hentet med [YouTube Data API](https://developers.google.com/youtube/v3/docs/channels/list),
ikke brukt som pålitelighetsscore. Registeret er ikke en uttømmende norsk toppliste.
Daglig innhenting og ukentlig oversikt følger [YOUTUBE_DRIFT.md](YOUTUBE_DRIFT.md).

Faktiske transkripsjoner, avsender, dato, kildeopprinnelse, tidskoder og kvitteringer
bevares privat i `v5/workspace/source_intake/innsyn/youtube/`. Les relevante
dag-/ukebriefer og selve kildeteksten ved saksvalg og research. Skill intervju,
kommentar, rapportering og partsutsagn. Et klipp er et tips til videre kontroll;
finn hele originalen og avgjørende dokumentasjon. Flere klipp fra samme samtale
er én kildekjede. Automatiske undertekster har feil; omstridte sitater må lyttes
til. Manglende tekst skal stå som tilgangsgap, og kildeinntak gir ingen rett til
å gjenpublisere andres film eller fulltekst.

## Fra idé til dokumentert funn

Start med beslutningen, beløpet, hendelsen eller konsekvensen som skal forklares.
Skriv hva som ville bekrefte og avkrefte hypotesen. Velg så den kilden som kan
avgjøre spørsmålet, og prøv en liten faktisk uthenting før vinkelen låses.
Et registertreff, en abstract eller et avisreferat er en ledetråd når den
avgjørende teksten ennå ikke er lest.

I `sources.md` føres stabil kilde-ID, originalavsender, dokument-/tabell-ID,
publisert og oppdatert dato, lest/hentet dato, direkte URL, lokal fil/kvittering,
nøyaktig lokator og begrensninger. Bruk disse enkle tilgangsbeskrivelsene i
det eksisterende begrensningsfeltet, uten å opprette et nytt parallelt register:

| Status | Hva den faktisk betyr |
|---|---|
| Dokumentasjon kontrollert | Tilbyderen beskriver ruten; ingen konkret kilde er hentet. |
| Metadata lest | Treff, katalog eller journalpost er lest; innholdet er ikke kontrollert. |
| Innhold hentet og lest | Den bestemte fullteksten eller de valgte datacellene er kontrollert. Oppgi om vedlegg mangler. |
| Krever innlogging/søknad | Ruten finnes; denne brukeren og dette formålet har ikke verifisert tilgang. |
| Lisens-/betalingsbegrenset | Lesetilgang, automatisering og gjenbruk må avklares hver for seg. |
| Forsøkt, utilgjengelig | Dato, konkret feil og neste lovlige handling er dokumentert. |
| Ikke prøvd | Ingen tilgangspåstand og ingen feil er etablert. |

En feil blokkerer påstanden som trenger kilden, ikke all uavhengig research.
Bevar feilen og skriv hva som fortsatt kan undersøkes. Hvis en kilde er
avgjørende og utilgjengelig, parker den vinkelen eller avgrens påstanden åpent.
Ikke erstatt fulltekst med et søkeutdrag uten å si det.

## Velg rute etter spørsmål

Status nedenfor gjelder denne kontrollen, ikke en varig tilgangsgaranti.

| Spørsmål | Første rute og neste handling | Viktigste begrensning / kontrollstatus |
|---|---|---|
| Hvem visste eller besluttet hva, og når? | [eInnsyn](https://einnsyn.no/), deretter organets egen postjournal og møteportal. Finn saksnummer, journalpost, vedlegg og saksfremlegg; be om de presise manglende dokumentene. For kommuner: kommunens egen nettside → postliste, politiske møter, protokoll, budsjett/årsrapport og kontrollutvalg. | Ikke alle organer, år eller vedlegg finnes i én portal. Journalmetadata beviser ikke dokumentinnhold eller at et dokument ikke finnes. [Digdirs API-dokumentasjon](https://github.com/felleslosninger/einnsyn-api-spec) krever API-nøkkel for autentiserte kall; ingen nøkkel eller innsynsbestilling er testet her. Bruk publikumssøket nå. |
| Hva kostet et statlig investeringsprosjekt, og mot hvilken ramme? | Prosjektets proposisjon eller melding til Stortinget → Finansdepartementets [KS-ordning](https://www.regjeringen.no/no/aktuelt/Hva-er-KS-ordningen/id2001422/) → styringsramme og kostnadsramme i vedtaket → etatens årsrapport og sluttrapport → Riksrevisjonens undersøkelse der den finnes. | Forklaringssiden er fra 2014; kontroller gjeldende rundskriv (R-108) og terskelverdier. Der KS2 er brukt, er styringsrammen normalt P50 og kostnadsrammen P85 (en høyere ramme, lagt frem for Stortinget), og de er ikke utskiftbare. Sammenlikn bare samme ramme og samme prisnivå. Mindre eller ikke kvalitetssikrede prosjekter har ikke disse rammene. Ingen konkret proposisjon er lest. |
| Hva kostet en kommunal tjeneste? | [SSB Statistikkbanken](https://www.ssb.no/statbank/) og KOSTRA → tabellens metadata → avgrenset datauttrekk → kommunens vedtatte årsregnskap og noter. Tabelleksempel 12367 er faktisk hentet. | Skille kommunekasse/konsern, funksjon/art, brutto/netto, drift/investering og kroner/1000 kroner. KOSTRA er ikke et fakturaregister og dokumenterer ikke i seg selv sløsing. |
| Hva bevilget og brukte staten? | [Statsregnskapets nedlastinger](https://statsregnskapet.dfo.no/last-ned) viste vedlikehold 31.10.2026. Sidens offisielle alternativ er [DFØs månedsrapporter](https://www.dfo.no/fagomrader/statlig-regnskap/rapportering-til-statsregnskapet/manedlige-rapporter-fra-statsregnskapet). [August 2026](https://www.dfo.no/nyhetsarkiv/manedlig-regnskap-august-2026-0) ga to faktiske XLSX-filer. Koble til budsjett, vedtak og årsrapport. | Filer hentet og overskrifter lest. Foreløpige, kumulative tall januar–august; uttaksdato er ikke observasjonsperiode. Råfilens orgnr er rapporterende virksomhet, ikke leverandør. Bevilgning og regnskap er ulike kolonner; utgiftsoversikten er i 1000 kroner. Dette er ikke et fakturaregister. |
| Hvem fikk støtte, på hvilke vilkår? | [Tilskudd.no: datagrunnlag](https://tilskudd.lottstift.no/om-tilskudd-no/6/slik-brukar-vi-og-viser-data) → ordning, forvalter, mottaker/orgnr, vedtak, tilskuddsbrev og sluttrapport. For andre sektorer: ansvarlig etats tildelinger og regnskap. | Dokumentasjon kontrollert. Portalen er avgrenset til statlige ordninger for ideelle/frivillige organisasjoner; den dekker ikke alle offentlige tilskudd. Registrert tildeling er ikke bevis på utbetaling eller oppnådd effekt. |
| Hvem fikk kontrakten, og var konkurransen reell? | [Doffin](https://doffin.anskaffelser.no/) → konkurranse og resultat, delkontrakt, versjon, CPV, oppdragsgiver og leverandør/orgnr → protokoll, tildelingsbrev, kontrakt, endringer og fakturaer. [DFØs metode](https://www.anskaffelser.no/data-statistikk-og-analyse/konkurranse-om-offentlige-anskaffelser) beskriver hullene. | Portal/metode kontrollert; API ikke prøvd. Mange resultater mangler. Fravær av treff beviser ikke ulovlig direkteanskaffelse. Rammeavtalens maksimum er ikke faktisk kjøp. [KOFA](https://www.klagenemndssekretariatet.no/klagenemda-for-offentlige-anskaffelser-kofa) er neste rute for klager; hent selve avgjørelsen og kontroller type og eventuell domstolsbehandling. |
| Hvilken virksomhet er dette? | [Brreg Enhetsregisterets API](https://data.brreg.no/enhetsregisteret/api/dokumentasjon/no/index.html) → orgnr, organisasjonsform, overordnet enhet og roller. Hent årsregnskap med noter fra registrert regnskapskilde eller selskapets originale rapport. | Ett åpent organisasjonsoppslag faktisk hentet; roller og årsregnskap ikke prøvd. Navnelikhet er ikke identitet. Dagens rolle er ikke dokumentasjon på rollen da et gammelt vedtak ble gjort. Enhetsregisteret er ikke et aksjeeierregister. |
| Hvem eier eller kontrollerer selskapet? | [Skatteetatens aksjonærregister](https://www.skatteetaten.no/deling/aksjonarregisteret/) for årsavslutning, selskapets aksjeeierbok for konkret kontroll og [Brregs reelle rettighetshavere](https://www.brreg.no/bruke-data-fra-bronnoysundregistrene/datasett-og-api/data-om-reelle-rettighetshavere/) når tilgangsvilkårene er oppfylt. | Dokumentasjon kontrollert; ingen persondata bestilt. Aksjonærregisteret viser innrapportert eierskap 31. desember, ikke sanntid. Reelle rettighetshavere krever særskilt tilgang; kvalifiserte medier er en mulig søkergruppe. Ikke utled tilgang fra kanalnavn eller UiO-tilhørighet. Personoppslag/totalbestand er ikke et åpent journalist-API. |
| Hva er lov, og hva har retten faktisk avgjort? | [Lovdata](https://lovdata.no/) for den konkrete bestemmelsen og ikrafttredelsen; [Domstolenes innsynsveiledning](https://www.domstol.no/no/for-journalister/offentlighetsregler-for-pressen) for dommen. Bruk saksnummer, domstol, dato, avsnitt og oppdatert ankestatus. | Veiledning kontrollert 31.10.2026; konkret rettsmappe og Lovdata Pro-tilgang ikke prøvd. Veiledningen sier at man har rett til utskrift av en dom i en straffesak når man kan vise til en bestemt sak, dommen ikke er eldre enn fem år og den ikke har begrensninger i adgangen til offentlig gjengivelse, og at «pressen» har rett til innsyn (ikke utskrift) i en tiltalebeslutning når straffesaken er berammet. Om en KI-redaksjon regnes som «pressen» her, er ikke avklart: bruk først ruten som gjelder alle, og spør domstolen før noe forutsettes. Pressemappe, full saksmappe og publiseringsrett er forskjellige ting. Kontroller anonymisering/referatforbud. En utredning om lovendring er ikke gjeldende lov. |
| Har kontrollorganene allerede undersøkt dette? | [Riksrevisjonens rapporter](https://www.riksrevisjonen.no/Rapporter), [Sivilombudets uttalelser](https://www.sivilombudet.no/uttalelser/), kommunal revisjon/kontrollutvalg og relevant tilsyn. Les mandat, utvalg, funn, svar og oppfølging. | Offentlige kataloger kontrollert. Undersøkelsesfunn gjelder det undersøkte utvalget; kritikk, risiko for lovbrudd og dokumentert lovbrudd er ulike konklusjoner. |
| Ble kritikken eller løftet faktisk fulgt opp? (etterprøving) | Originalrapporten og stortingsbehandlingen → Riksrevisjonens egen oppfølging i Dokument 3:1 «oppfølging av forvaltningsrevisjoner som er behandlet av Stortinget» ([Dokument 3-serien på stortinget.no](https://www.stortinget.no/no/Saker-og-publikasjoner/Publikasjoner/Dokumentserien/2025-2026/dok3-202526/)) og kontroll- og konstitusjonskomiteens innstilling ([eksempel 2022–2023](https://stortinget.no/no/Saker-og-publikasjoner/Publikasjoner/Innstillinger/Stortinget/2022-2023/inns-202223-161s/?all=true)) → departementets omtale i senere budsjettproposisjoner → dagens data og berørtes erfaring. For kommuner: kontrollutvalgets oppfølging av forvaltningsrevisjon. | Søkeresultatene ble kontrollert 31.10.2026; ingen konkret oppfølging er lest. Innstillingen for 2022–2023 beskriver at Riksrevisjonen normalt følger opp tre år etter stortingsbehandlingen; kontroller gjeldende praksis. «Ikke fulgt videre» betyr at revisjonen avslutter oppfølgingen, ikke at problemet er løst. Departementets egen omtale er partens fremstilling. |
| Hva har politi og påtalemyndighet gjort, og var det lovlig? | [Spesialenheten for politisaker](https://www.spesialenheten.no/vare-avgjorelser/) (avgjørelser; [årsrapporter](https://www.spesialenheten.no/arsrapporter/)) for saker om politiets og påtalemyndighetens egne handlinger. [Økokrim: korrupsjon](https://www.okokrim.no/korrupsjon.549312.no.html) og [pressemeldinger](https://www.okokrim.no/pressemeldinger.549344.no.html) for økonomisk kriminalitet og korrupsjon. Les selve avgjørelsen eller meldingen, instans og saksstatus (anmeldt, etterforsket, siktet, tiltalt, dømt, rettskraftig), og be om innsyn der avgjørelsen ikke er publisert. | Sidene er bare lest som oppslagsflater 31.10.2026; ingen konkret avgjørelse er lest. Spesialenheten sier selv at den oppdaterer et sammendrag av saker hver uke og legger ut anonymiserte avgjørelser i saker der politiet har brukt skytevåpen og «utvalgte avgjørelser», ikke alle. Økokrims forside nevnte ikke tiltalebeslutninger eller dommer; bruk domstolrutene over. En henleggelse er ikke bevis på at politiet handlet riktig, og en etterforskning er ikke bevis på skyld. Bruk strafferettslige begreper etter REDAKSJON.md. |
| Hvilken utredning, evaluering eller instruks ligger bak? | [Kudos](https://kudos.dfo.no/) → original dokumentutgave, oppdragsgiver, metode, vedlegg og publiseringsdato. Bruk årsrapport og tildelingsbrev sammen for mål og resultater. | Katalog kontrollert; ingen bestemt evalueringsrapport lest i prøven. Søkebeskrivelse er en ledetråd. En bestilt evaluering må vurderes for mandat og uavhengighet. |
| Hvem foreslo, endret og vedtok politikken? | [Stortingets åpne data](https://data.stortinget.no/dokumentasjon-og-hjelp/) → sesjon/saks-ID → forslag, innstilling, votering og endelig vedtak. [Regjeringens høringer](https://www.regjeringen.no/no/dokument/hoyringar/id1763/) gir forslag og innspill. | Sesjonsindeks faktisk hentet; saksinnhold og voteringer ikke hentet i prøven. Regjeringsforslag og vedtak må skilles. En høringsuttalelse er partens argument, ikke uavhengig dokumentasjon. |
| Hvem finansierer partiene eller har relevante bindinger? | [Partifinansiering](https://www.partifinansiering.no/nb/) → år, partiledd, bidragstype og giver; [Stortingets verv og interesser](https://www.stortinget.no/no/stortinget-og-demokratiet/representantene/okonomiske-interesser/) og departementets utnevnelser/mandater. | Katalog/dokumentasjon kontrollert. Ikke summer årlige bidrag og valgkampbidrag ukritisk; de kan overlappe. Interne overføringer kan dobbelttelles. Registrert forbindelse dokumenterer ikke påvirkning, inhabilitet eller gjenytelse. Kontroller tidslinjen. |
| Hvorfor endret renter, valuta eller priser seg? | [Norges Banks API-veiledning](https://www.norges-bank.no/en/topics/Statistics/open-data/guide-data-warehouse/) og SSB. Bruk fast seriekode, frekvens, enhet og periode. Fem faktiske USD/NOK-observasjoner og SSB KPI-uttrekk er lagret. | Daglig referansekurs er ikke kundens vekslingskurs; renteendring er ikke alene årsaksbevis. KPI-eksemplet bruker ny base 2025=100. Velg prisindeks som passer spørsmålet, ikke automatisk KPI for byggeprosjekter. |
| Hva driver strømregningen og kraftmarkedet? | [NVE magasinstatistikk](https://www.nve.no/energi/analyser-og-statistikk/magasinstatistikk/) og kraftsituasjonsrapporter, RME og SSBs strømpristabeller. Skill prisområde, tid, spotpris, nettleie, avgifter og støtte. | Dokumentasjonsrute kontrollert; datasett ikke hentet. Magasinfylling er ett forhold. Time-/kvarterspris og husholdningsgjennomsnitt kan ikke byttes ut. ENTSO-E/Nord Pool brukes bare med kontrollert tilgang og aktuelle vilkår; ingen markedslisens er etablert. |
| Hvilke olje-/gassvolumer, felt og rettigheter? | [Sokkeldirektoratets åpne data](https://www.sodir.no/fakta/data-og-analyser/apne-data/) → Faktasider/Faktakart → felt-/lisens-ID og eksport. Koble ved behov til statens inntekter og Norges Bank. | Katalog kontrollert; eksport ikke prøvd. Produksjon, reserver, ressursanslag, eksportverdi og statlig inntekt er forskjellige størrelser. Angi standardvolum/oljeekvivalenter og periode. |
| Hvor skjer inngrep eller endringer? | [Geonorge API-katalog](https://www.geonorge.no/verktoy/APIer-og-grensesnitt/apier-for-kartkatalogen/) → datasetteier, dato, avgrensning, projeksjon og distribusjon; kommunens planregister for vedtak. | Dokumentasjon kontrollert. Åpne kart er ikke full grunnbok eller personbasert eiersøk. WMS-bilder er ikke rå geometri. Målestokk, koordinatsystem og kartlagt område setter grenser. |
| Hva viser miljø-, transport- og helsedata? | [Miljødirektoratets data](https://data.miljodirektoratet.no/), [NVDB/Vegkart](https://www.vegvesen.no/fag/teknologi/nasjonal-vegdatabank/hente-ut-og-se-pa-data-i-nasjonal-vegdatabank/) og [FHI åpent API](https://www.fhi.no/ta/statistikkalender_og_statistikk/apen-api-og-statistikk/). Velg konkret register/indikator og original metode. | Dokumentasjon kontrollert; datauttrekk ikke prøvd. Skille målte/beregnede utslipp, hendelser/eksponering og rå/aldersstandardiserte rater. Endret registrering, små tall og skjerming kan forklare utslag. Ingen tilgang til pasientdata er etablert. |

Norge er valgt fordi dette er kanalens uttrykkelige publikum og mandat.
Bruk utenlandske kilder når de avklarer en norsk påstand: for eksempel TED for
en konkret norsk EØS-kunngjøring, EFTA/ESA for en avgjørelse eller Eurostat/OECD
for sammenliknbare indikatorer. Hent den aktuelle definisjonen og originalen;
en internasjonal rangering er ikke automatisk en rimelig sammenlikning.

## Avisarkiv, bibliotek og akademisk belegg

Aviser er viktige for tidligere dekning, tidslinjer, kildehenvisninger og svar.
Les originalartikkelen med dato/byline og senere rettelser. Oppgi hva Innsyn
selv har kontrollert og krediter andres avsløring. Flere gjenfortellinger av
samme artikkel er én kildekjede; å lese en artikkel gir ikke rett til å vise
hele avissiden, klipp eller foto i filmen.

| Rute | Hva som kan gjenbrukes nå | Tilgang og grense |
|---|---|---|
| UiO Oria/EZproxy | Finn eksakt database, tittel, årgang og tilgangslenke i [UiOs avisoversikt](https://www.ub.uio.no/bibliotekene/humsam/samlinger/aviser/) og [hjemmetilgang](https://www.ub.uio.no/bruk/ub-tilgang-hjemmefra.html). | Nettleserøkt er faktisk bekreftet gjennom PressReader. Den lagrede pipeline-cookiens separate DOI-probe fikk `auth_handoff`. Nettlesertilgang og ubetjent HTTP-tilgang er ulike statusser. |
| Atekst/Retriever | [UiOs ordning](https://www.ub.uio.no/bruk/sok-i-hele-biblioteket/sok-om-atekst-tilgang.html) beskriver separat søknad ved særskilt faglig behov og egne brukerdetaljer. | Dokumentasjon kontrollert. EZproxy-cookie alene åpner ikke ordningen. Ingen massenedlasting; ingen ny søknad eller konto er opprettet. Rett til dette journalistiske formålet må bekreftes av avtale/tilbyder, ikke antas. |
| PressReader | [UiOs veiledning](https://www.ub.uio.no/bruk/sok-i-hele-biblioteket/pressreader.html) beskriver hele utgaver og omtrent 60–90 dagers tilbakeblikk. 31.10.2026 ble én Aftenposten-artikkel faktisk åpnet i Chrome via UiOs offisielle EZproxy-lenke, med synlig UiO-bibliotektilgang. | **Nettleserassistert fulltekstlesing bekreftet for dette eksemplet.** Ingen ubetjent HTTP/API- eller massenedlastingsrute er etablert. Ikke et komplett historisk arkiv eller nøkkel til avisens egen betalingsmur; formål og gjenbruk følger avtalen. |
| Nasjonalbiblioteket | [Katalog-API](https://api.nb.no/) fungerer: én avispost er faktisk hentet. Bruk stabil item-ID/URN og dato; kontroller siden visuelt før sitat fra OCR. | Metadata er ikke fulltekst. [Forsknings-/dokumentasjonstilgang](https://www.nb.no/tilgang/forskning-og-dokumentasjon/) kan kreve søknad, eller riktig Feide-rolle. Ordningen beskriver åtte timers søknadstilgang. Lesetilgang og lisens er separate; prøveposten var merket CC BY-NC-ND og ikke public domain. |
| Åpen forskning og UiO-tidsskrifter | `paper_discovery` finner metadata via fagdatabaser; `paper_download --url ... --no-uio` henter åpen rapport/PDF. Vurder metode, utvalg, kausalitet, finansiering og relevans for Norge; hent nyere systematiske oversikter når de belyser spørsmålet. | DOI/abstract eller siteringstall er ikke kvalitetsdom. UiO-ruten kan brukes ved faktisk rettighet; bevar begrenset materiale privat. `paper_buzz_board` er laget for forskningsdrevne kanaler og velger ikke Innsyns dagsorden. |

`uio_cookie_refresh` fornyer bare en eksisterende, autorisert EZproxy-økt.
Den gir ingen nye abonnementer. Den delte papirproben prøver én vitenskapelig
DOI; at den lykkes beviser ikke avis-, Atekst-, Lovdata- eller Factiva-tilgang.
`paper_download` kan hente åpne myndighetsrapporter, men er ingen avisarkivklient:
den søker ikke hele Atekst, tolker ikke avisutgaver og har ingen generell
medielisens. Et vellykket HTML-resultat kan være en landingsside. Les innholdet
før det merkes fulltekst. Ingen cookies flyttes til andre domener.

From Cosmos to Civilization, Climate Change Science og How Money Moves har
allerede valgt obligatorisk UiO-preflight i sine kanaloppsett. Innsyn kan
gjenbruke ferdighetene og kildekvitteringene deres uten å arve denne
avhengigheten eller deres forskningsdrevne emnevalg.

Den faktiske nettleserprøven er dokumentert i
`.codex_tasks/innsyn_astra_review_20261031/browser_access_checks.json`.
Artikkelteksten er ikke kopiert til kvitteringen. Prøveartikkelen er kun
tilgangsbevis, ikke en valgt sak eller føring for kanalens dagsorden.

Innsyn har derfor `require_uio_ezproxy_preflight: false`. Åpne offentlige data
og nettundersøkelser skal kunne begynne uten UiO. En eventuell feil i en
avgrenset abonnementsrute skal likevel rapporteres presist, med neste handling.

## Ett gjennomført dataforløp, ikke en ny dataplattform

Bruk eksisterende `dataset_download` for offentlige GET-baserte JSON-/CSV-/XLSX-
uttrekk. SSB v2s [offisielle veiledning](https://www.ssb.no/api/pxwebapiv2)
viser metadata og eksplisitte verdikoder. Hent metadata før tall; unngå et
API-standardutvalg som skjuler dimensjoner. Små utsnitt er nok for tilgangsprøven.

Reproduserbare spørringer, originale svar og SHA-256-kvitteringer ligger privat i
`.codex_tasks/innsyn_astra_review_20261031/queries_initial.json`,
`queries_data.json`, `access_initial/` og `access_data/`. En enkel kjørekommando:

```powershell
.\.venv\Scripts\python.exe .codex_tasks/innsyn_astra_review_20261031/fetch_examples.py .codex_tasks/innsyn_astra_review_20261031/queries_data.json --output-root v5/workspace/journalism/innsyn/source-check-YYYYMMDD
```

`summarize_examples.py` i samme oppgavemappe gjenskaper de små dataeksemplene
fra lagrede bytes og kontrollerer kildehashene. DFØ-filene og den opprinnelige
vedlikeholdsfeilen har egne kvitteringer i `access_dfo/`,
`dfo_access_checks.json` og `dfo_workbook_inspection.json`. Inspeksjonen gjelder
overskrifter og noen rader, ikke en gjennomrevidering av statsregnskapet.

Velg en ny datert mappe ved ny uthenting; ferdigheten nekter å overskrive andre
bytes. I en faktisk sak kjøres samme ferdighet med `--episode-root <saksmappe>`
eller aktiv episode, `--url <presis GET-spørring>`, `--output-name <fil.json>`,
`--credit <kilde og lisens>` og `--note <formål>`. Resultatet ligger under
`media/datasets/`. Før fil og kvittering i sakens `sources.md`; ikke kopier
rådata eller kvitteringer til nettstedet. Det er ikke nødvendig med ny modell,
API-nøkkel eller norsk spesialkode for disse åpne rutene.

For hver beregning: skriv tabell/serie og valgte dimensjoner, periode, enhet,
definisjon, uttaksdato, kildens oppdateringsdato og relevant fotnote. Bevar råfilen,
en liten kjørbar beregning og dens resultat. Kontroller null/manglende/skjermet,
sum/nevner, løpende/faste priser, sesongjustering, geografi og sammenliknbart
omfang. Ikke summer overlappende grupper. La en separat faktasjekk gjenskape
hovedtallet fra rådata. Skriv hva tallet ikke kan vise.

En offentlig avsender er primærkilde til hva den registrerer eller mener;
den er ikke automatisk uavhengig om egen måloppnåelse. Sammenhold vedtak og
regnskap med kontrollrapporter, faktisk levert tjeneste og berørtes erfaringer.
En persons erfaring dokumenterer erfaringen, ikke hvor vanlig den er.

Frys et tydelig faktakutt til manus. Kontroller endret rettsstatus, vesentlige
svar, rettelser og sentrale tall igjen ved faktasjekk og rett før publisering.
Ny research må dateres; et gammelt utdrag blir ikke ferskt fordi filen kopieres.

## Tilgangskontroll 1. november 2026

KOFA-lenken i tabellen er rettet til den faktiske lenken fra sekretariatets forside (URL-en bruker «klagenemda»). Den tidligere adressen lot seg ikke åpne i webverktøyet. Gjeldende side og saksarkene 2026/0579 og 2026/1097 er lest; PDF-avgjørelsene er ikke lest i denne kontrollen. Se ukesbriefen 1.11.2026 for det daterte sveipet over kontrollorganene. Dette endrer ikke hva eldre prøvekvitteringer dokumenterte.
