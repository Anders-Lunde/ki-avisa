# Cloudflare Pages for KI-avisa

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
