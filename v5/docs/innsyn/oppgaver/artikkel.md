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
- Kort metodedel: faktakutt, sentrale beregninger, definisjoner, vesentlige mangler
  og hva materialet ikke kan vise.
- Lengden følger materialet. Ikke fyll, og ikke legg til sidespor for å virke grundig.
- Skriv om henvendelser bare det handoffen dokumenterer. Stillhet er ikke et svar.

Skriv <<CASE>>/article.json som ett JSON-objekt, ren tekst uten HTML:

```json
{"slug":"kort-ascii-slug","title":"Norsk tittel","deck":"Ingress",
"kind":"Undersøkelse / Forklart / Dokumentar","date":"YYYY-MM-DD",
"status":"draft","sections":[{"heading":"Mellomtittel","paragraphs":["Tekst"]}],
"sources":[{"title":"Originalkildens navn, dato og relevant side","url":"https://..."}],
"updates":[]}
```

Finnes `article.json` fra før, er dette en ny versjon av saken etter ny research:
bevar slug og før en datert opplysning i `updates` dersom versjonen har vært vist
utenfor redaksjonen. Ingen private dokumenter, kildeidentiteter eller korrespondanse
i artikkel-JSON. Status forblir `draft`; oppgaven gir ikke rett til publisering.

## Handoff

Før et datert avsnitt «Artikkelutkast» i `editorial_review.md`: tittel, hovedsvaret,
hva som er nytt, listen over nye tolkninger med grunnlag, kjente begrensninger og hva
kontrollen bør se på først. Avslutt med samme oppsummering. Ikke påstå uavhengig
kontroll eller beslutning.
