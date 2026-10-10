# Referentie: gemeenschapskwartiergelijktijdigheid en benuttingsgraad

**Versie 1.0.0 — concept ter consultatie**

Dit document is de normatieve tekst van de referentie. Waar dit document en de referentie-implementatie verschillen, gaat dit document voor en geldt het verschil als fout in de implementatie.

## 1. Doel

Deze referentie maakt het mogelijk om de benutting van verdeelmodellen voor energiedelen objectief en narekenbaar te vergelijken. Ze legt vast hoeveel gedeelde elektriciteit een gemeenschap in elk kwartier ten hoogste kon benutten, gegeven wat er gemeten is. Elk verdeelmodel wordt daartegen afgemeten.

De referentie schrijft geen verdeelmodel voor. Ze bepaalt alleen de maatstaf.

## 2. Definities

**2.1 Gemeenschap.** Een vooraf vastgelegde, eindige verzameling aansluitingen *A* waarvoor de benutting wordt bepaald. De samenstelling geldt voor een vastgelegde periode en wordt bij elke uitkomst vermeld.

**2.2 Kwartier.** Een tijdvak van 15 minuten, beginnend op een veelvoud van 15 minuten in UTC. Dit sluit aan bij de onbalansverrekenperiode van de Europese elektriciteitsmarkt.

**2.3 Kwartierinvoeding.** *i(a,k)*: de elektriciteit in kWh die aansluiting *a* in kwartier *k* aan het net levert, zoals gemeten op het invoedingsregister van de meter.

**2.4 Kwartierafname.** *o(a,k)*: de elektriciteit in kWh die aansluiting *a* in kwartier *k* van het net afneemt, zoals gemeten op het afnameregister van de meter.

**2.5 Gemeenschapskwartierinvoeding.** De som van de kwartierinvoeding over alle aansluitingen van de gemeenschap:

```
I(k) = Σ_{a ∈ A} i(a,k)
```

**2.6 Gemeenschapskwartierafname.** De som van de kwartierafname over alle aansluitingen van de gemeenschap:

```
O(k) = Σ_{a ∈ A} o(a,k)
```

**2.7 Gemeenschapskwartiergelijktijdigheid.** De kleinste van de gemeenschapskwartierinvoeding en de gemeenschapskwartierafname:

```
G(k) = min( I(k), O(k) )
```

*G(k)* is de hoeveelheid elektriciteit die in kwartier *k* binnen de gemeenschap ten hoogste als gedeelde elektriciteit kon worden benut.

**2.8 Benutting van een verdeelmodel.** *B_m(k)*: de hoeveelheid elektriciteit die verdeelmodel *m* in kwartier *k* als gedeelde elektriciteit toerekent aan afname binnen de gemeenschap, en die in datzelfde kwartier door de ontvangende aansluitingen ook werkelijk is afgenomen. Toegewezen maar niet afgenomen elektriciteit telt niet mee.

**2.9 Benuttingsgraad.** De benutting van verdeelmodel *m* over een periode *P*, gedeeld door de gemeenschapskwartiergelijktijdigheid over dezelfde periode:

```
β_m(P) = Σ_{k ∈ P} B_m(k)  /  Σ_{k ∈ P} G(k)
```

## 3. Rekenregels en conventies

**3.1 Geen saldering binnen het kwartier per aansluiting.** Invoeding en afname worden per aansluiting gebruikt zoals ze op de afzonderlijke registers zijn gemeten. Een aansluiting kan in hetzelfde kwartier zowel invoeden als afnemen; beide tellen mee. Dit volgt de meting en de officiële kwartierwaarden.

**3.2 Geen overdracht tussen kwartieren.** Elk kwartier staat op zichzelf. Niet benutte gemeenschapskwartiergelijktijdigheid gaat verloren en wordt niet opgeslagen of meegenomen naar een ander kwartier. De referentie beschrijft geen buffer of opslag.

**3.3 Verhouding van sommen.** De benuttingsgraad is een verhouding van sommen over de periode, geen gemiddelde van verhoudingen per kwartier. Kwartieren met veel gelijktijdigheid wegen daardoor zwaarder dan kwartieren met weinig.

**3.4 Ontbrekende gegevens.** Een kwartier waarin voor één of meer aansluitingen van de gemeenschap geen gemeten waarde beschikbaar is, wordt voor alle verdeelmodellen buiten de berekening gelaten. Het aandeel uitgesloten kwartieren wordt bij elke uitkomst vermeld als dekking. Aangevulde of geschatte waarden worden niet gebruikt, tenzij dit expliciet wordt vermeld.

**3.5 Lege periode.** Is Σ G(k) over de periode gelijk aan nul, dan is de benuttingsgraad niet gedefinieerd en wordt die ook zo gerapporteerd.

**3.6 Eenheden en nauwkeurigheid.** Hoeveelheden in kWh. Berekeningen worden uitgevoerd zonder tussentijdse afronding. Uitkomsten worden gerapporteerd met de gebruikte meetresolutie.

## 4. Invarianten

Voor elk verdeelmodel *m* en elk kwartier *k* geldt:

```
0 ≤ B_m(k) ≤ G(k)
```

Dit volgt uit de definities: gedeelde elektriciteit kan niet meer zijn dan wat binnen de gemeenschap is ingevoed, en niet meer dan wat binnen de gemeenschap is afgenomen. Een berekening die dit schendt, is fout. Daaruit volgt:

```
0 ≤ β_m(P) ≤ 1
```

Een verdeelmodel dat in elk kwartier *B_m(k) = G(k)* haalt, heeft een benuttingsgraad van 1. Verdeling naar groepskwartiergelijktijdigheid binnen de gemeenschap haalt dit per definitie.

## 5. Wat de referentie niet bepaalt

- **Verdeling.** Hoe de benutte elektriciteit over aansluitingen wordt verdeeld, is een keuze die buiten de referentie valt. De referentie meet het totaal, niet de verdeling.
- **Prijzen en belastingen.** De referentie rekent in kWh. Financiële waardering is een aparte stap.
- **Gedrag.** De referentie gaat uit van gemeten gedrag. Wat een gemeenschap met ander gedrag had kunnen bereiken, valt erbuiten.
- **Netbelasting.** Energiedelen is administratief. De referentie zegt niets over de fysieke stroom in het net.

## 6. Rapportage

Elke uitkomst op basis van deze referentie vermeldt ten minste:

1. de versie van deze referentie;
2. de samenstelling van de gemeenschap (aantal aansluitingen en, waar mogelijk, kenmerken);
3. de periode, en het aantal kwartieren in en buiten de berekening (dekking);
4. de herkomst van de meetgegevens (bijvoorbeeld P1-uitlezing of officiële kwartierwaarden);
5. per verdeelmodel: de parameters, Σ B_m, Σ G en β_m.

## 7. Versiebeheer

Deze referentie volgt semantische versienummers. Een wijziging die uitkomsten kan veranderen, verhoogt het hoofdnummer. Verduidelijkingen zonder gevolg voor uitkomsten verhogen het tweede of derde nummer. Uitkomsten blijven altijd herleidbaar tot de versie waarmee ze zijn berekend.

## 8. Voorgestelde wettekst

Ter illustratie een formulering die als referentie in wet- of regelgeving kan worden opgenomen:

> *Gemeenschapskwartiergelijktijdigheid*: voor een gemeenschap van aansluitingen en een kwartier, de kleinste van de totale in dat kwartier door de aansluitingen van de gemeenschap ingevoede elektriciteit en de totale in dat kwartier door die aansluitingen afgenomen elektriciteit, zoals gemeten.
>
> *Benuttingsgraad*: voor een verdeelmodel en een periode, de som over de kwartieren van die periode van de door het verdeelmodel toegerekende en in hetzelfde kwartier afgenomen gedeelde elektriciteit, gedeeld door de som over dezelfde kwartieren van de gemeenschapskwartiergelijktijdigheid.
>
> Bij de evaluatie van een regeling voor energiedelen wordt voor elk toegepast verdeelmodel de benuttingsgraad bepaald en openbaar gemaakt.
