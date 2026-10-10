# Gemeenschapskwartiergelijktijdigheid

**Een objectieve, narekenbare referentie voor de benutting van verdeelmodellen bij energiedelen.**

> Gemeenschapskwartiergelijktijdigheid is de kleinste van de totale gemeenschapskwartierinvoeding en de totale gemeenschapskwartierafname.

```
G(k) = min( Σ invoeding van de gemeenschap in kwartier k ,  Σ afname van de gemeenschap in kwartier k )
```

Gemeenschapskwartiergelijktijdigheid is een zeldzaam en vluchtig goed. Ze bestaat alleen in het kwartier waarin ze ontstaat, en wat dan niet wordt benut, is voorgoed verloren. Wetsvoorstellen en lobbyvoorstellen voor energiedelen missen een objectieve referentie om de benutting van de voorgestelde verdeelvormen te vergelijken. Deze repository levert die referentie: een precieze definitie, een berekeningsmethode en een referentie-implementatie die iedereen kan narekenen.

## De benuttingsgraad

Elk verdeelmodel, of het nu een vaste verdeelsleutel, een dynamische sleutel of een andere vorm is, wordt uitgedrukt in één getal:

```
benuttingsgraad = Σ benutte gedeelde elektriciteit  /  Σ gemeenschapskwartiergelijktijdigheid
```

Binnen een gemeenschap kan per kwartier nooit meer gedeelde elektriciteit worden benut dan *G(k)*. Verdeling naar gemeenschapskwartiergelijktijdigheid haalt dat maximum per definitie; elk ander model haalt evenveel of minder. De benuttingsgraad werkt daarmee zoals het Carnot-rendement voor warmtemotoren: geen oordeel, maar een nuchtere maat voor hoeveel van het fysisch mogelijke wordt gehaald.

Een fictief voorbeeld van één kwartier: A voedt 1,0 kWh in, D 0,2 kWh; B neemt 0,6 kWh af, C 0,1 kWh, E 0,4 kWh. Bilateraal deelt A met B en C, en D met E.

| Verdeelmodel | Benut (kWh) | Benuttingsgraad |
| --- | --- | --- |
| Vaste sleutel (A: ½ B, ½ C; D: alles E) | 0,8 | 73% |
| Dynamische sleutel (zelfde paren) | 0,9 | 82% |
| Gemeenschapskwartiergelijktijdigheid | 1,1 | 100% |

De referentie meet het totaal, niet de verdeling. Hoe de benutte elektriciteit over aansluitingen wordt verdeeld, blijft een keuze. Het is een eerlijke meetlat, geen eerlijke verdeling.

## Inhoud

| Bestand | Inhoud |
| --- | --- |
| [`REFERENTIE.md`](REFERENTIE.md) | De normatieve definitie, rekenregels, invarianten en een voorgestelde wettekst |
| [`DATAFORMAAT.md`](DATAFORMAAT.md) | Het formaat van meetgegevens, modelconfiguratie en uitkomsten |
| [`kwartiergelijktijdigheid/`](kwartiergelijktijdigheid/) | Referentie-implementatie in Python, zonder afhankelijkheden |
| [`tests/`](tests/) | Testgevallen, inclusief een controle van de invarianten op willekeurige gegevens |
| [`voorbeelden/`](voorbeelden/) | Een uitgewerkt voorbeeld met metingen en modelconfiguratie |

## Gebruik

Python 3.8 of nieuwer, geen extra pakketten.

```
python -m kwartiergelijktijdigheid voorbeelden/testgeval.csv voorbeelden/modellen.json
python -m unittest discover -s tests
```

De uitkomst bevat per verdeelmodel de referentieversie, de parameters, Σ benutting, Σ gelijktijdigheid, de benuttingsgraad en de dekking (het aandeel kwartieren met volledige meting).

## Status en doel

Versie 1.0.0, concept ter consultatie. Deze referentie wordt gepubliceerd om te dienen als maatstaf voor een lopend meet- en monitorproject. Dat project onderzoekt gemeten gelijktijdigheidsdata uit het net op benutting, vanuit diverse voorgestelde en toegepaste verdeelmodellen, en maakt de onderzoeksresultaten openbaar als evidentie in het wetgevend debat.

Het uiteindelijke doel is dat deze definitie en berekeningsmethode als referentie in de wet worden opgenomen, zodat voor elke regeling voor energiedelen de benuttingsgraad van de toegepaste verdeelmodellen wordt bepaald en openbaar gemaakt. Zolang dat niet het geval is, dient deze repository als publieke, onafhankelijk narekenbare referentie.

De referentie is partijdig in doel en onpartijdig in methode. Iedereen kan de definitie toetsen, de berekening herhalen en kritiek of verbeteringen voorstellen via issues en pull requests. Uitkomsten blijven altijd herleidbaar tot de versie van de referentie waarmee ze zijn berekend.

## English summary

*Community quarter-hour simultaneity* is the lesser of a community's total feed-in and total consumption in a 15-minute settlement period. It is the maximum amount of shared electricity the community can use in that period. The *utilisation rate* of any energy-sharing allocation model is its shared-and-consumed electricity divided by the community quarter-hour simultaneity, summed over a period. This repository provides the normative definition (in Dutch), a dependency-free Python reference implementation and test cases, proposed as an objective benchmark for energy-sharing rules under the EU electricity market design.

## Licentie

Code: MIT-licentie, zie [`LICENSE`](LICENSE). Teksten (REFERENTIE.md, DATAFORMAAT.md, README.md): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.nl). Hergebruik, ook in wetgeving en beleid, is uitdrukkelijk welkom met bronvermelding.
