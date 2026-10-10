# Wijzigingen

Deze referentie volgt semantische versienummers (REFERENTIE.md 7). Een wijziging die uitkomsten kan veranderen, verhoogt het hoofdnummer.

## 1.0.0 — 2026-10-10 — concept ter consultatie

- Definitie van gemeenschapskwartierinvoeding, gemeenschapskwartierafname en gemeenschapskwartiergelijktijdigheid.
- Definitie van benutting en benuttingsgraad als verhouding van sommen over een periode.
- Conventies: kwartier in UTC, geen saldering binnen het kwartier per aansluiting, geen overdracht tussen kwartieren, uitsluiting van onvolledig gemeten kwartieren.
- Invariant 0 ≤ B(k) ≤ G(k).
- Referentie-implementatie in Python met vijf verdeelmodellen: gemeenschap naar verbruik, gemeenschap gelijk, gemeenschap met voorrang, vaste sleutel en dynamische sleutel.
