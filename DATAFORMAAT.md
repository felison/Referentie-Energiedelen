# Dataformaat

## Metingen

Kwartierwaarden staan in één CSV-bestand in lang formaat: één rij per aansluiting per kwartier. UTF-8, komma als scheidingsteken, punt als decimaalteken.

| Kolom | Inhoud | Voorbeeld |
| --- | --- | --- |
| `aansluiting` | Gepseudonimiseerde code van de aansluiting | `HH0042` |
| `kwartier_start` | Begin van het kwartier in UTC, ISO 8601 | `2027-03-14T10:15:00Z` |
| `invoeding_kwh` | Kwartierinvoeding *i(a,k)* in kWh, gemeten op het invoedingsregister | `0.412` |
| `afname_kwh` | Kwartierafname *o(a,k)* in kWh, gemeten op het afnameregister | `0.000` |

Een lege cel betekent een ontbrekende meting. Het kwartier valt dan voor alle verdeelmodellen buiten de berekening (REFERENTIE.md 3.4).

Kwartierwaarden worden afgeleid uit tellerstanden op de grenzen van het kwartier: het verschil van de invoedingsregisters (beide tarieven opgeteld) en het verschil van de afnameregisters. Invoeding en afname worden niet met elkaar gesaldeerd (REFERENTIE.md 3.1).

## Modelconfiguratie

Een JSON-bestand met de samenstelling van de gemeenschap, de herkomst van de metingen en de te vergelijken verdeelmodellen. Ontbreekt `gemeenschap`, dan geldt elke aansluiting in de metingen als lid.

```json
{
  "gemeenschap": ["A", "B", "C", "D", "E"],
  "bron_metingen": "P1-uitlezing meetgroep [naam], kwartierwaarden uit tellerstanden",
  "modellen": [
    {"model": "gemeenschap_naar_verbruik"},
    {"model": "gemeenschap_gelijk"},
    {"model": "gemeenschap_met_voorrang", "voorrang": ["C", "E"]},
    {"model": "vaste_sleutel", "fracties": {"A": {"B": 0.5, "C": 0.5}, "D": {"E": 1.0}}},
    {"model": "dynamische_sleutel", "koppelingen": {"A": ["B", "C"], "D": ["E"]}}
  ]
}
```

| Model | Parameters | Beschrijving |
| --- | --- | --- |
| `gemeenschap_naar_verbruik` | geen | Gemeenschapskwartiergelijktijdigheid, verdeeld naar verhouding van de afname. Benuttingsgraad per definitie 1. |
| `gemeenschap_gelijk` | geen | Idem, gelijk verdeeld met plafond per afnemer. Benuttingsgraad per definitie 1. |
| `gemeenschap_met_voorrang` | `voorrang`: lijst aansluitingen | Idem, eerst de voorranggroep. Benuttingsgraad per definitie 1. |
| `vaste_sleutel` | `fracties`: gever → ontvanger → fractie | Vooraf vastgelegde fracties per gever, som per gever ten hoogste 1. |
| `dynamische_sleutel` | `koppelingen`: gever → ontvangers | Gever verdeelt naar actuele afname van zijn eigen ontvangers; één gever per ontvanger. |

De drie gemeenschapsmodellen verschillen alleen in de verdeling over aansluitingen, niet in de benutting. Ze zijn opgenomen om verdelingsanalyses mogelijk te maken.

## Uitkomst

De opdrachtregel geeft per model de velden die REFERENTIE.md 6 voorschrijft: referentieversie, model en parameters, Σ B, Σ G, benuttingsgraad, en het aantal kwartieren in en buiten de berekening.
