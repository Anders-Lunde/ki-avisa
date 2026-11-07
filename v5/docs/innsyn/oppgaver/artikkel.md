# Artikkel: <<CASE_REL>>

Oppgave <<TASK_ID>>, laget <<CREATED_AT>>. Rollen løses fra kanalfilen; ikke velg
eller endre modell.

Les AGENTS.md, `v5/docs/innsyn/ARBEIDSKORT.md` og avsnittene «Fakta, regning og
tolkning» og «Presseetikk» i `REDAKSJON.md`. Les i saksmappen <<CASE>>:
`writer_handoff.md` (siste daterte handoff), `claims.md`, `sources.md`,
`calculations/` og «Bestilling» og siste beslutning i `editorial_review.md`. Åpne
originalen for hver passasje du siterer eller tolker. Ikke åpne `correspondence/`,
`reporting.md` eller kvitteringer; kontaktstatus står i handoffen, og du skal ikke
sende e-post i dette steget. <<EPISODE_CONTEXT>>

## Før du skriver

Les researchens anbefaling. Sier den vent eller parker, eller mangler den avgjørende
kilden slik at artikkelen bare ville gjentatt den offisielle opplysningen med
forbehold: skriv ikke artikkelen. Før et datert avsnitt i `editorial_review.md` med
grunnen og hva som må til, og stopp. Det er et riktig resultat. Et fullt dokumentert
mindre svar med egen verdi for leseren kan derimot skrives selv om andre svar
ventes; skriv da bare det dokumentene bærer.

## Slik skrives artikkelen

- **Skriv for en vanlig leser, ikke for kontrolløren** (eierens presisering 6.11.2026).
  Still spørsmålet: hvorfor skulle noen som ikke følger saken, lese dette og fortelle
  det videre? Begynn med en konkret scene, person eller handling fra kildene der det
  finnes. Mennesker, steder og øyeblikk går foran tall og arkivreferanser.
- **Lengde:** forklaringer og dokumentsaker sikter mot 500–900 ord i brødteksten,
  undersøkelser mot 900–1 500. Lengre tekst må begrunnes i handoffen. Kalendere,
  tidsforløp, pengestrømmer og steder vises som grafikk (`figure`, se under) med kort
  tekst rundt. Ikke skriv lange lister.
- **Forbehold der de betyr noe.** Ett tydelig forbehold ved påstanden det gjelder er
  bedre enn gjentatte reservasjoner i hver setning. Detaljert lesescope, filer og
  arbeidsprosess hører hjemme i saksmappen, ikke i artikkelen.
- **Led med svaret** og det sterkeste dokumenterte poenget leseren ikke kjenner.
  Tittelen sier hva som er nytt. Den gjentar ikke den offisielle linjen, med mindre
  det å bekrefte eller avkrefte den er nyheten. Tittel og ingress skal kunne leses
  sammen på én mobilskjerm; sikt mot en tittel under 70 tegn.
- **Fire slags setninger:** kildefakta (attribuert, datert), egen regning (vist i
  metoden), tolkning (vis til det som støtter betydningen) og åpne spørsmål (sagt som
  åpne). En definisjon, fotnote eller historisk modell beviser ikke dagens tilstand.
  Daterte tilstander skal stå som daterte.
- **Nye tolkninger** som ikke står i `claims.md`, føres der som tolkning med
  grunnlag før du bruker dem, og listes i handoffen din.
- Forklar systemet gjennom det konkrete eksemplet. Bevar motforklaringer, vesentlige
  svar og meningsbærende usikkerhet ved påstanden de gjelder.
- Kildehenvisning [1], [2] osv. ved sentrale faktapåstander; tallene viser til
  rekkefølgen i `sources`. Kildetittelen navngir dokument, dato og side, avsnitt eller
  tabell. Skill egen kontroll fra andre mediers funn og krediter dem.
- Kort metodedel som siste seksjon, høyst 150 ord: faktakutt, sentrale beregninger,
  definisjoner, vesentlige mangler og hva materialet ikke kan vise. Ikke fortell om
  verktøy, søkeprosesser, mislykkede nettkall eller interne kontroller.
- Lengden følger materialet. Ikke fyll, og ikke legg til sidespor for å virke grundig.
- Skriv om henvendelser bare det handoffen dokumenterer. Stillhet er ikke et svar.

Skriv <<CASE>>/article.json som ett JSON-objekt, ren tekst uten HTML:

```json
{"slug":"kort-ascii-slug","title":"Norsk tittel","deck":"Ingress",
"summary":["Punkt 1","Punkt 2","Punkt 3"],
"kind":"Undersøkelse / Forklart / Dokumentar","date":"YYYY-MM-DD",
"status":"draft","sections":[{"heading":"Mellomtittel","paragraphs":["Tekst"],
  "figure":{"file":"slug-kart.svg","alt":"Beskrivelse for skjermleser","caption":"Bildetekst med kilde"}}],
"sources":[{"title":"Originalkildens navn, dato og relevant side","url":"https://..."}],
"updates":[]}
```

`figure` er valgfritt per seksjon og vises under seksjonens avsnitt. Filen er en SVG du
lager i `v5/sites/innsyn/graphics/`. Den skal være uten skript og uten eksterne ressurser,
og alle tall og datoer i den må stå i brødteksten eller i kildene.

`summary` er et kort sammendrag øverst i artikkelen (eierkrav 6.11.2026). Det skal ha 3–4 punkter på én–to setninger hver, høyst 260 tegn per punkt, uten kildehenvisninger. Ta med de viktigste svarene, og ett punkt om den viktigste usikkerheten eller grensen når den betyr noe for leseren. Hvert punkt må være dekket av brødteksten; sammendraget kan ikke inneholde nye påstander, tall eller sterkere formuleringer. Kontrollen sjekker sammendraget mot teksten.

Finnes `article.json` fra før, er dette en ny versjon av saken etter ny research:
bevar slug og før en datert opplysning i `updates` dersom versjonen har vært vist
utenfor redaksjonen. Ingen private dokumenter, kildeidentiteter eller korrespondanse
i artikkel-JSON. Status forblir `draft`; oppgaven gir ikke rett til publisering.

## Handoff

Før et datert avsnitt «Artikkelutkast» i `editorial_review.md`: tittel, hovedsvaret,
hva som er nytt, listen over nye tolkninger med grunnlag, kjente begrensninger og hva
kontrollen bør se på først. Avslutt med samme oppsummering. Ikke påstå uavhengig
kontroll eller beslutning.
