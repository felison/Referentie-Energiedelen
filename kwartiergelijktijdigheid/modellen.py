"""Verdeelmodellen die tegen de referentie kunnen worden afgemeten.

Elk model geeft per kwartier een verdeling terug: ontvanger -> benutte gedeelde
elektriciteit in kWh. De benutting B_m(k) is de som daarvan (REFERENTIE.md 2.8).

De modellen zijn voorbeelden van voorgestelde en toegepaste verdeelvormen. Ze
zijn geen onderdeel van de normatieve referentie; de referentie meet ze.
Nieuwe modellen kunnen worden toegevoegd door dezelfde interface te volgen.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, Mapping

from .referentie import TOLERANTIE, Kwartier


class Verdeelmodel:
    naam = "verdeelmodel"

    @property
    def parameters(self) -> dict:
        return {}

    def verdeling(self, kwartier: Kwartier) -> Dict[str, float]:
        raise NotImplementedError

    def benutting(self, kwartier: Kwartier) -> float:
        return math.fsum(self.verdeling(kwartier).values())


# --------------------------------------------------------------------------
# Verdeling binnen de gemeenschap per kwartier (gemeenschapskwartiergelijktijdigheid)
# --------------------------------------------------------------------------


class GemeenschapNaarVerbruik(Verdeelmodel):
    """Totale invoeding wordt per kwartier naar verhouding van de afname verdeeld.

    Haalt per definitie B(k) = G(k). Iedere afnemer krijgt hetzelfde deel van
    zijn afname gedekt. Dit is de voorgestelde referentieverdeling.
    """

    naam = "gemeenschap_naar_verbruik"

    def verdeling(self, kwartier: Kwartier) -> Dict[str, float]:
        totaal_in = math.fsum(kwartier.invoeding.values())
        totaal_af = math.fsum(kwartier.afname.values())
        if totaal_af <= 0:
            return {a: 0.0 for a in kwartier.afname}
        fractie = min(1.0, totaal_in / totaal_af)
        return {a: o * fractie for a, o in kwartier.afname.items()}


class GemeenschapGelijk(Verdeelmodel):
    """Totale invoeding wordt gelijk verdeeld, nooit meer dan iemands afname.

    Wat overblijft wordt opnieuw gelijk verdeeld over wie nog tekort heeft.
    """

    naam = "gemeenschap_gelijk"

    def verdeling(self, kwartier: Kwartier) -> Dict[str, float]:
        beschikbaar = math.fsum(kwartier.invoeding.values())
        rest = {a: o for a, o in kwartier.afname.items()}
        toegekend = {a: 0.0 for a in kwartier.afname}
        actief = [a for a, o in rest.items() if o > TOLERANTIE]
        while beschikbaar > TOLERANTIE and actief:
            deel = beschikbaar / len(actief)
            nieuw_actief = []
            for a in actief:
                gift = min(deel, rest[a])
                toegekend[a] += gift
                rest[a] -= gift
                beschikbaar -= gift
                if rest[a] > TOLERANTIE:
                    nieuw_actief.append(a)
            actief = nieuw_actief
        return toegekend


class GemeenschapMetVoorrang(Verdeelmodel):
    """Een vooraf vastgelegde groep krijgt eerst haar afname gedekt.

    Het restant gaat naar verhouding van de afname naar de overige aansluitingen.
    """

    naam = "gemeenschap_met_voorrang"

    def __init__(self, voorrang: Iterable[str]):
        self.voorrang = sorted(set(voorrang))

    @property
    def parameters(self) -> dict:
        return {"voorrang": self.voorrang}

    def verdeling(self, kwartier: Kwartier) -> Dict[str, float]:
        beschikbaar = math.fsum(kwartier.invoeding.values())
        voor = {a: o for a, o in kwartier.afname.items() if a in self.voorrang}
        overig = {a: o for a, o in kwartier.afname.items() if a not in self.voorrang}
        toegekend = {a: 0.0 for a in kwartier.afname}
        voor_totaal = sum(voor.values())
        if voor_totaal > 0:
            fractie = min(1.0, beschikbaar / voor_totaal)
            for a, o in voor.items():
                toegekend[a] = o * fractie
            beschikbaar -= voor_totaal * fractie
        overig_totaal = sum(overig.values())
        if overig_totaal > 0 and beschikbaar > 0:
            fractie = min(1.0, beschikbaar / overig_totaal)
            for a, o in overig.items():
                toegekend[a] = o * fractie
        return toegekend


# --------------------------------------------------------------------------
# Bilaterale modellen
# --------------------------------------------------------------------------


class VasteSleutel(Verdeelmodel):
    """Elke gever wijst vooraf vaste fracties van zijn invoeding toe aan ontvangers.

    fracties[gever][ontvanger] = f, met per gever een som van ten hoogste 1.
    Benut wordt per ontvanger het kleinste van de toegewezen hoeveelheid en de
    eigen afname. Toegewezen maar niet afgenomen elektriciteit gaat verloren.
    """

    naam = "vaste_sleutel"

    def __init__(self, fracties: Mapping[str, Mapping[str, float]]):
        for gever, verdeling in fracties.items():
            som = sum(verdeling.values())
            if any(f < 0 for f in verdeling.values()) or som > 1 + TOLERANTIE:
                raise ValueError(
                    f"Fracties van gever {gever} moeten niet-negatief zijn en samen "
                    f"ten hoogste 1; nu {som}"
                )
        self.fracties = {g: dict(v) for g, v in fracties.items()}

    @property
    def parameters(self) -> dict:
        return {"fracties": self.fracties}

    def verdeling(self, kwartier: Kwartier) -> Dict[str, float]:
        toegewezen: Dict[str, float] = {}
        for gever, verdeling in self.fracties.items():
            r = kwartier.invoeding.get(gever, 0.0)
            for ontvanger, f in verdeling.items():
                toegewezen[ontvanger] = toegewezen.get(ontvanger, 0.0) + f * r
        return {
            j: min(x, kwartier.afname.get(j, 0.0)) for j, x in toegewezen.items()
        }


class DynamischeSleutel(Verdeelmodel):
    """Elke gever verdeelt zijn invoeding over zijn eigen ontvangers naar hun afname.

    Basisvariant: elke ontvanger heeft ten hoogste één gever. Een gever geeft
    nooit meer dan de afname van zijn ontvangers; wat overblijft gaat verloren.
    """

    naam = "dynamische_sleutel"

    def __init__(self, koppelingen: Mapping[str, Iterable[str]]):
        gezien: Dict[str, str] = {}
        for gever, ontvangers in koppelingen.items():
            for j in ontvangers:
                if j in gezien:
                    raise ValueError(
                        f"Ontvanger {j} is gekoppeld aan {gezien[j]} en {gever}; "
                        "de basisvariant staat één gever per ontvanger toe"
                    )
                gezien[j] = gever
        self.koppelingen = {g: list(o) for g, o in koppelingen.items()}

    @property
    def parameters(self) -> dict:
        return {"koppelingen": self.koppelingen}

    def verdeling(self, kwartier: Kwartier) -> Dict[str, float]:
        toegekend: Dict[str, float] = {}
        for gever, ontvangers in self.koppelingen.items():
            r = kwartier.invoeding.get(gever, 0.0)
            vraag = {j: kwartier.afname.get(j, 0.0) for j in ontvangers}
            totaal = sum(vraag.values())
            if totaal <= 0:
                for j in ontvangers:
                    toegekend[j] = toegekend.get(j, 0.0)
                continue
            fractie = min(1.0, r / totaal)
            for j, o in vraag.items():
                toegekend[j] = toegekend.get(j, 0.0) + o * fractie
        return toegekend


def model_uit_config(config: Mapping) -> Verdeelmodel:
    """Maak een model uit een configuratie, bijvoorbeeld uit een JSON-bestand."""
    soort = config["model"]
    if soort == GemeenschapNaarVerbruik.naam:
        return GemeenschapNaarVerbruik()
    if soort == GemeenschapGelijk.naam:
        return GemeenschapGelijk()
    if soort == GemeenschapMetVoorrang.naam:
        return GemeenschapMetVoorrang(config["voorrang"])
    if soort == VasteSleutel.naam:
        return VasteSleutel(config["fracties"])
    if soort == DynamischeSleutel.naam:
        return DynamischeSleutel(config["koppelingen"])
    raise ValueError(f"Onbekend model: {soort}")
