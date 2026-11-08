# Cloudflare Pages for KI-avisa

## Passordbeskyttet besøksstatistikk, 7. november 2026

Eieren bestilte en privat statistikkside. Den er publisert på
https://ki-avisa.pages.dev/stats med HTTP Basic-innlogging. Brukernavnet er
`admin`; passordet ligger bare i ignorert
`v5/workspace/hosting/stats-access.txt`. Cloudflare har bare SHA-256-hashen av
innloggingsverdien som produksjonshemmeligheten `STATS_AUTH_SHA256`.
Passord, innloggingsdetaljer og privat statistikk skal ikke inn i Git.

Oversikten viser sidevisninger per dag, mest leste sider og faste grupper av
henvisningskilder for 7, 30 eller 90 dager, med norsk kalenderdato. Den teller
ikke unike personer. Kun summer per offentlig sidesti, dato og kildegruppe
lagres i D1-databasen `ki-avisa-stats` (EU-jurisdiksjon), gjennom bindingen
`STATS_DB`. Ingen cookies, IP-adresser, besøks-ID-er, user-agent-strenger eller
vilkårlige henvisningsadresser lagres i statistikken. Kjente roboter,
forhåndslasting, HEAD, feil, interne/private adresser, preview-verter og
forespørsler med Authorization utelates. Robotfilteret er ikke fullstendig.
Offentlig personverntekst er skrevet med kanalens eksisterende forfatterrolle
og kontrollert mot implementasjonen.

`worker.mjs` kombinerer telleren, serverkontrollert innlogging og eksisterende
videospoling. Ingen statisk stats-HTML eller offentlig data-API eksporteres.
Svar fra statistikksiden er `no-store`/`noindex`, også ved feil innlogging.
Manglende hemmelighet/database gir stengt statistikk; en skrivefeil i telleren
skal ikke stoppe offentlige sider. Siden finnes ikke i meny eller sitemap.
`wrangler.toml` med D1-bindingen inngår nå i publiseringshashen og følger med
utenfor den isolerte opplastingsmappen ved senere monitorpubliseringer.
Se nettstedets README for schema, kontrollkommandoer og passordrotasjon.

Kontrollert utrulling: https://bb50b004.ki-avisa.pages.dev/.
Offentlig eksport endret bare `_worker.js`, `_routes.json`, `stats.css` og
personvernseksjonen i `om.html`. Alle eksisterende artikler og mediefiler var
identiske med forrige utrulling. Lokal kontroll brukte ekte SQLite og egne
testdata; disse ble ikke lagt i produksjonsdatabasen. Mobil/desktop og
periodevalg ble kontrollert. Live innlogging, feil passord, alternative
stats-adresser, eksakte offentlige filer og videospoling bestod. Én faktisk
sidehenting ved sluttkontrollen er med i totalsummen. Første registrerte
visning er 7. november; eldre trafikk er ikke hentet tilbake.

Privat kvittering: `v5/workspace/hosting/stats-verification-20261107.json`.
Utrullingen følger også de ordinære `publication-*`-kvitteringene.

Oppdatert 4. november 2026 etter eierens bestilling om å publisere det
faktiske nettstedet uten private utkast eller internt materiale.

## Automatisk publisering og SEO

Eieren bestilte automatisk oppdatering, favicons og SEO 4. november 2026.
Automasjonen **Publish ready KI sites** (`publish-ready-ki-sites`) kontrollerer
begge prosjekter hver 6. time i den eksisterende chatten. PC og desktopapp
må være på. Eksisterende Wrangler-innlogging brukes uten nye tokens eller
betalte ressurser.

Kontrollert SEO-/favicon-utrulling: https://cf70c95d.ki-avisa.pages.dev/.
Produksjonsadressen er fortsatt https://ki-avisa.pages.dev/.

Etter faktisk redaksjonell beslutning og kontroll av offentlig eksport:

```powershell
& ..\AgentHouse\.venv\Scripts\python.exe v5/sites/innsyn/publish.py prepare --reviewed-by "faktisk redaksjonell kontrollør"
```

Dette registrerer en teknisk kvittering med eksakte filhasher. Det erstatter
ikke kildekontroll, imøtegåelse eller den faktiske redaksjonelle beslutningen.
Ingen ny eiergodkjenning per sak kreves. Automatiseringen kjører kun
`publish.py run`: den bygger, kontrollerer og publiserer en matchende endret
eksport én gang. Den oppretter aldri godkjenningsmetadata eller artikkelstatus.

Uendret offentlig eksport gir `unchanged`; endringer etter gjennomgang gir
`not_ready`. Ingen av delene publiseres. Endringer i private utkast alene
endrer ikke offentlig eksport. En prosesslås hindrer samtidige kjøringer,
og feil beholder tidligere vellykket tilstand. Opplasting bruker en isolert
mappe som bare inneholder de kontrollerte offentlige filene.

Tilstand og logger er ignorert under `v5/workspace/hosting/publication-*`.
Monitoren er stille ved uendret/ikke-klar eksport og melder bare ny publisering,
ny feil eller nødvendig eierhandling. Identiske feil dedupliseres med signatur
i `publication-monitor.json`. Git-push er ingen publiseringstrigger.

SVG/PNG/ICO-favicons, Apple-ikon og delingsbilde er publisert, med sidespesifikke
beskrivelser, kanoniske adresser uten .html, Open Graph, Twitter-kort og
WebSite/NewsMediaOrganization/WebPage-data. Article/NewsArticle-data genereres
bare for publiserte artikler. Sitemap viser kun offentlig innhold. Private
prøvebygg og 404-sider har noindex. Ingen søkeplassering eller indeksering er lovet.

Manglende/utdatert klargjøring, bevaring av tidligere suksess ved simulert feil
og uendret andregangskjøring er testet. Live mobil-/desktopkontroll og filhasher
bestod; private adresser gir fortsatt 404. Tidsplanen er aktiv, men ingen faktisk
tidsstyrt kjøring er påstått utført ennå.

## Første publisering før SEO-oppdateringen

- Produksjon: https://ki-avisa.pages.dev/
- Kontrollert utrulling: https://66f0b305.ki-avisa.pages.dev/
- Prosjekt: `ki-avisa`, i eierens eksisterende Cloudflare-konto.
- Produksjonsgren: `main`. Opplasting: Direct Upload med Wrangler.
- Offentlig bygg: `v5/sites/innsyn/public/` (generert og ignorert).
- Ansvarlig redaktør og eier: **Anders Lunde**.
- Offentlig kontakt: **lunde.anders@gmail.com**.

Eieren bekreftet redaktør og offentlig kontakt uttrykkelig i denne bestillingen.
Se REDAKSJON.md for mandatet. Ingen ekstern juridisk vurdering er påstått.

## Offentlig eksport

Det eksisterende designet er beholdt. Forside og metode-/omside er publisert,
med kontakt, redaktør og forklaring av felles eierskap med KI-partiet. Det
finnes **null artikler med publisert status** i eksporten. Ingen utkast er
oppgradert til publisert, og ingen redaksjonell beslutning er konstruert.

Kjør fra KI-avisa-repositoriets rot:

```powershell
& ..\AgentHouse\.venv\Scripts\python.exe v5/sites/innsyn/build.py --output public
& ..\AgentHouse\.venv\Scripts\python.exe v5/sites/innsyn/check_public.py
& ..\AgentHouse\.venv\Scripts\python.exe v5/sites/innsyn/publish.py run
```

Byggeren tillater ikke `--preview --output public`. Bare artikler med
`status: published`, `approved_by` og `approved_at` kan komme med. De feltene
må følge en faktisk beslutning under redaksjonens mandat. Ingen enkeltartikkel
skal godkjennes eller publiseres gjennom en ren hostingoppgave.

Bare `public/` lastes opp. Ikke last opp repo-roten, innholds-JSON,
arbeidsområder, preview/, .openai/, lydprøver eller den eksisterende private
`dist/`. Offentlig output bygges rent, med 404-side, sitemap og sikkerhetshoder.

Den eksisterende eierprivate Sites-prøveutgaven og dens prosjekt-ID er bevart.
Det offentlige bygget skriver ikke til `dist/` og leser ikke aktivitetssnapshotet
eller lydprøver. Ventesiden i `holding/` er historisk og er erstattet i produksjon.
Ingen Git-push publiserer automatisk. Ingen VM, DNS-post eller betalt ressurs
ble endret/opprettet.

## Kontroller

`check_public.py` verifiserer med syntetiske testdata at utkast og intern
aktivitet utelates, gamle private filer fjernes fra offentlig output,
privat dist bevares, preview-til-public avvises og manglende redaksjonell
beslutning avvises. Det faktiske offentlige filtreet kontrolleres også.

Desktop- og mobilnettlesertester bestod for alle sider. Skjermbilder ble
visuelt gjennomgått. Alle fem offentlige ressursfiler, uten vertsconfig og
404-mal, samsvarte byte for byte med live HTTPS-svar. Rotadressen og ni
private/interne adresser er også kontrollert; de private adressene returnerte
HTTP 404. Ventesidens noindex-hoder er borte.

Utrullingskvittering og verifikasjon med filhasher ligger i ignorert
`v5/workspace/hosting/20261104-pages-full-site-*`. Offentlig kildekode og
dokumentasjon er ikke automatisk committet eller pushet.

Neste arbeid er den vanlige redaksjonelle prosessen for konkrete saker.
Nettsiden skal vise bare faktisk publiserte saker, aldri private arbeidsutkast.

[Cloudflare: Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/)

## Grafikk og galleri, 6. november 2026

Artikler kan ha `summary` (påkrevd ved publisering), `figure` per seksjon (egen SVG i `v5/sites/innsyn/graphics/`, lagt inn i siden; skript, stiler, lenker og bilder avvises på grunn av CSP) og `gallery` (bilder i `v5/sites/innsyn/media/<slug>/`, kopiert til `public/media/<slug>/`). `check_public.py` krever at mediefilene samsvarer nøyaktig med galleriene i publiserte artikler. `publish.py` hasher nå også `media/<slug>/<bilde>` og avviser alle andre undermapper. Galleribilder skal ha kontrollert lisens og kreditering før publisering.

## Video i artikler, 7. november 2026

Artikler kan ha `film` med `file` (.mp4), valgfri `captions` (.vtt) og `poster`, samt `caption` og `credit`. Filene ligger i `v5/sites/innsyn/media/<slug>/` og serveres fra nettstedet selv (CSP `media-src 'self'`), uten YouTube. `check_public.py` og `publish.py` godtar .mp4 og .vtt under `media/<slug>/`. Cloudflare Pages har en grense på 25 MB per fil, så lengre videoer må komprimeres eller legges på YouTube med `youtube_id`.

Cloudflare Pages' statiske filer svarer ikke på HTTP Range, og da kan nettlesere ikke spole i video. Når en publisert artikkel har `film`, skriver `build.py` derfor `_worker.js` og `_routes.json` til eksporten. Workeren kjører bare for `/media/*`. Den svarer med 206 og Content-Range for .mp4 og sender alt annet uendret videre til de statiske filene. Pages Functions inngår i gratisnivået, og ingen ny betalt ressurs er opprettet.

## Tipsside, 7. november 2026

`tips.html` ("Tips oss") ligger i hovedmenyen, i bunnteksten og som egen boks på forsiden. Siden er statisk: knappen åpner e-postprogrammet med emne og noen ferdige spørsmål, og det er ikke noe skjema eller lagring på nettstedet (CSP `form-action 'none'` står uendret). Teksten følger REDAKSJON.md: den lover ikke anonymitet, sier at det ikke finnes en sikker tipskanal og at tips leses av KI-redaksjonen via eksterne KI-tjenester, og ber om at sensitive opplysninger ikke sendes på e-post. `tips` er reservert som artikkel-slug.

## Domenesøk, 7. november 2026

Eieren ba om et rimelig domene gjennom Cloudflare Registrar. Lesesøket viste
`ki-avisa.com` som ledig til USD 11,17 for registrering og årlig fornyelse.
Rimeligere kandidater var `kiavisa.observer` (USD 9,20/år), `kiavisa.uk`
(USD 5,30/år) og `kiavisa.win` (USD 4,18 første år, USD 5,18 ved fornyelse).
Prisene ble kontrollert mot [Cloudflares prisliste](https://pricing.registrar.cloudflare.com/).
Anbefalingen er `ki-avisa.com`, som følger avisnavnet og har en kjent endelse.

Det offentlige søket er ikke en autoritativ registreringskontroll:
`kiavisa.com` ble også vist som ledig, mens Verisigns RDAP viste
`redemption period`. Domenet uten bindestrek behandles derfor som utilgjengelig.
`ki-avisa.com` ga ikke treff hos Verisign. Svar og begrensninger er bevart privat i
`v5/workspace/hosting/domain-research-20261107.json`. Ingen domener er kjøpt,
reservert eller koblet til nettstedet. Neste handling er eierens valg av domene;
før et eventuelt kjøp må faktisk registrerbarhet og sluttpris kontrolleres på nytt.

Eieren spurte deretter om `.no`. Cloudflares støttede TLD-liste har ikke `.no`.
Norids RDAP viste 7. november `ki-avisa.no` som ikke registrert og `kiavisa.no`
som registrert. Oppslagene ligger privat i
`v5/workspace/hosting/domain-no-research-20261107.json`. Et `.no`-domene må
registreres hos en annen forhandler, men kan fortsatt kobles til Cloudflare Pages.

### Felles `.com` for norsk og engelsk utgave

Eieren foreslo 7. november å bruke ett `.com`-domene for en norsk og en engelsk
utgave, og ba om navneforslag. Dette er en navnevurdering, ingen bestilling om
kjøp, navnebytte eller utvikling/publisering av en engelsk utgave.

Kortlisten er `sourceandscope.com` (Source & Scope), `innsynpress.com`
(Innsyn Press), `openavisa.com` (Open Avisa) og `faktareport.com` (Fakta Report).
Alle fire ga 404 hos Verisigns RDAP og ble vist som ledige i Cloudflares
offentlige søk til USD 11,17 for registrering og årlig fornyelse.
Forslagene er ikke en varemerkeklarering eller garanti for registrerbarhet.
En innledende navnesjekk fant eksisterende Klar Journal på `klarjournal.de`,
så `klarjournal.com` er ikke på kortlisten selv om domenet ikke var registrert.
Kontrollsvar ligger privat i
`v5/workspace/hosting/domain-bilingual-research-20261107.json`.

Anbefalingen i denne navnerunden er Source & Scope for en felles internasjonal
profil, med Innsyn Press som alternativ med tydeligere norsk identitet.
Språkstier som `/no/` og `/en/` er foreslått, ikke implementert. Neste handling
er eierens navnevalg; før kjøp kontrolleres registrerbarhet og sluttpris på nytt.

Eieren ønsket deretter navn i retning «AI News» eller «AI Times». Begge de eksakte
`.com`-domenene er registrert og i bruk av publikasjoner. `theaitimes.com` er også
registrert, og `theaitimes.org/about/` beskriver en avis skrevet av KI-agenter.
Den tidligere navneanbefalingen er derfor bare et alternativ; ingen navn er valgt.
En ny kortliste er AI Civic Times (`aicivictimes.com`), AI Public Record
(`aipublicrecord.com`), AI Open Press (`aiopenpress.com`) og AI News Beacon
(`ainewsbeacon.com`). De fire ga 404 hos Verisigns RDAP og ble vist som ledige
i Cloudflares offentlige søk til USD 11,17 for registrering og årlig fornyelse.
Svar er bevart privat i `v5/workspace/hosting/domain-ai-research-20261107.json`.
Ingen kjøp, navneendring eller publisering er utført.

### Kort, oppdiktet navn for flere språk

Eieren ønsket deretter noe i retning «new paper dot com», gjerne et nytt ord som
kan fungere på flere språk. `newpaper.com` er registrert. Nye forslag er Newpero
(`newpero.com`), Nupevo (`nupevo.com`), Noviparo (`noviparo.com`) og Nupavo
(`nupavo.com`). Alle fire ga 404 hos Verisigns RDAP og ble vist som ledige i
Cloudflares offentlige søk til USD 11,17 for registrering og årlig fornyelse.
Newpero er foreslått som nærmest «new paper», Nupevo som et kortere, mer
språknøytralt alternativ. Ingen universell språkegnethet eller navnerett er
fastslått. Novapero og Papivio ble nedprioritert etter funn av eksisterende
produkt-/butikknavn. Kontrollsvar ligger privat i
`v5/workspace/hosting/domain-coined-research-20261107.json`. Ingen navn er valgt
av eieren, og ingen domener er kjøpt eller reservert.

Eieren spurte også om `.ai`-pris. Cloudflares prisliste kontrollert 7. november
viser USD 80 per år for registrering og fornyelse, mot USD 11,17 for `.com`.
Cloudflares dokumentasjon for registrering oppgir minst to år for `.ai`, altså
USD 160 for minimumsperioden ved dagens standardpris. Årsprisen er omtrent
7,2 ganger `.com`-prisen. Ingen bestemt `.ai`-kandidat er kontrollert eller kjøpt.
Kilder: https://pricing.registrar.cloudflare.com/ og
https://developers.cloudflare.com/api/go/resources/registrar/subresources/registrations/methods/create/.

### `.no` hos andre forhandlere, priskontroll 7. november 2026

Eieren ba om billigste `.no` uavhengig av leverandør. Laveste tydelig bekreftede
løpende pris inkl. mva blant de kontrollerte tilbyderne er InfoDesk:
99 kr ved registrering og 99 kr ved årlig fornyelse, uten krav om webhotell.
Webhuset annonserer 7 kr første år og 99 kr ved fornyelse eks. mva, som gir
8,75 kr og 123,75 kr inkl. mva. Gigahost tar 85 kr eks. mva for begge deler,
altså 106,25 kr inkl. mva. Uniwebs aktuelle prisliste viser 10 kr / 240 kr
eks. mva (12,50 kr / 300 kr inkl. mva); en eldre FAQ med 6 kr er ikke lagt til grunn.

Dynadot viser EUR 7,59 ved registrering og fornyelse, men norsk sluttpris med
eventuell mva og valutapåslag er ikke bekreftet. Dette er en sammenlikning av
publiserte priser, ikke en uttømmende markedskontroll eller et gjennomført kjøp.
Kilder, mva-grunnlag og begrensninger er bevart privat i
`v5/workspace/hosting/domain-no-provider-prices-20261107.json`.
InfoDesk tillater endring av navnetjenere, så domenet kan brukes med eksisterende
Cloudflare-oppsett. Ingen betalt hosting eller registrering er bestilt.
