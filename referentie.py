"""Normatieve rekenregels uit REFERENTIE.md (versie 1.0.0).

Geen afhankelijkheden buiten de standaardbibliotheek. Alle hoeveelheden in kWh.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Mapping, Optional

REFERENTIEVERSIE = "1.0.0"

#: Tolerantie voor afrondingsverschillen bij het controleren van invarianten.
TOLERANTIE = 1e-9

#: Rapportage in 9 decimalen: ruim fijner dan elke meetresolutie (1 Wh = 0,001 kWh),
#: en vrij van artefacten van drijvendekommaberekening.
DECIMALEN = 9


@dataclass(frozen=True)
class Kwartier:
    """Gemeten waarden van alle aansluitingen in één kwartier.

    invoeding[a] = i(a,k), afname[a] = o(a,k), in kWh (REFERENTIE.md 2.3 en 2.4).
    """

    start: str
    invoeding: Mapping[str, float]
    afname: Mapping[str, float]

    def __post_init__(self) -> None:
        for naam, waarden in (("invoeding", self.invoeding), ("afname", self.afname)):
            for aansluiting, waarde in waarden.items():
                if waarde is None or waarde < 0:
                    raise ValueError(
                        f"{naam} van {aansluiting} in kwartier {self.start} "
                        f"moet een niet-negatief getal zijn, niet {waarde!r}"
                    )


def gemeenschapskwartierinvoeding(kwartier: Kwartier) -> float:
    """I(k) = som van i(a,k) over de gemeenschap (REFERENTIE.md 2.5)."""
    return math.fsum(kwartier.invoeding.values())


def gemeenschapskwartierafname(kwartier: Kwartier) -> float:
    """O(k) = som van o(a,k) over de gemeenschap (REFERENTIE.md 2.6)."""
    return math.fsum(kwartier.afname.values())


def gemeenschapskwartiergelijktijdigheid(kwartier: Kwartier) -> float:
    """G(k) = min(I(k), O(k)) (REFERENTIE.md 2.7)."""
    return min(gemeenschapskwartierinvoeding(kwartier), gemeenschapskwartierafname(kwartier))


def controleer_benutting(benutting: float, gelijktijdigheid: float, start: str, model: str) -> None:
    """Invariant 0 <= B_m(k) <= G(k) (REFERENTIE.md 4)."""
    if benutting < -TOLERANTIE or benutting > gelijktijdigheid + TOLERANTIE:
        raise AssertionError(
            f"Invariant geschonden in kwartier {start} voor model {model}: "
            f"B = {benutting} valt buiten [0, G = {gelijktijdigheid}]"
        )


@dataclass
class Uitkomst:
    """Benuttingsgraad van één verdeelmodel over een periode (REFERENTIE.md 2.9 en 6)."""

    model: str
    parameters: dict
    som_benutting: float
    som_gelijktijdigheid: float
    kwartieren_in_berekening: int
    kwartieren_uitgesloten: int
    referentieversie: str = REFERENTIEVERSIE

    @property
    def benuttingsgraad(self) -> Optional[float]:
        """None als de som van G nul is (REFERENTIE.md 3.5)."""
        if self.som_gelijktijdigheid <= 0:
            return None
        return self.som_benutting / self.som_gelijktijdigheid

    @property
    def dekking(self) -> Optional[float]:
        totaal = self.kwartieren_in_berekening + self.kwartieren_uitgesloten
        return None if totaal == 0 else self.kwartieren_in_berekening / totaal

    def als_dict(self) -> dict:
        return {
            "referentieversie": self.referentieversie,
            "model": self.model,
            "parameters": self.parameters,
            "som_benutting_kwh": round(self.som_benutting, DECIMALEN),
            "som_gelijktijdigheid_kwh": round(self.som_gelijktijdigheid, DECIMALEN),
            "benuttingsgraad": None if self.benuttingsgraad is None
            else round(self.benuttingsgraad, DECIMALEN),
            "kwartieren_in_berekening": self.kwartieren_in_berekening,
            "kwartieren_uitgesloten": self.kwartieren_uitgesloten,
            "dekking": None if self.dekking is None else round(self.dekking, DECIMALEN),
        }


def volledige_kwartieren(kwartieren: Iterable[Kwartier], gemeenschap: Iterable[str]):
    """Splits in kwartieren met en zonder volledige meting (REFERENTIE.md 3.4).

    Een kwartier is volledig als voor elke aansluiting van de gemeenschap zowel
    invoeding als afname bekend is. Aansluitingen buiten de gemeenschap worden
    genegeerd.
    """
    leden = list(gemeenschap)
    volledig: List[Kwartier] = []
    uitgesloten = 0
    for kwartier in kwartieren:
        if all(a in kwartier.invoeding and a in kwartier.afname for a in leden):
            volledig.append(
                Kwartier(
                    start=kwartier.start,
                    invoeding={a: kwartier.invoeding[a] for a in leden},
                    afname={a: kwartier.afname[a] for a in leden},
                )
            )
        else:
            uitgesloten += 1
    return volledig, uitgesloten


def benuttingsgraad(
    kwartieren: Iterable[Kwartier],
    gemeenschap: Iterable[str],
    model,
) -> Uitkomst:
    """Bereken de benuttingsgraad van een verdeelmodel over een periode.

    `model` is een object met een attribuut `naam`, een attribuut `parameters`
    en een methode `benutting(kwartier) -> float` die B_m(k) teruggeeft.
    """
    volledig, uitgesloten = volledige_kwartieren(kwartieren, gemeenschap)
    benuttingen: List[float] = []
    gelijktijdigheden: List[float] = []
    for kwartier in volledig:
        g = gemeenschapskwartiergelijktijdigheid(kwartier)
        b = model.benutting(kwartier)
        controleer_benutting(b, g, kwartier.start, model.naam)
        benuttingen.append(b)
        gelijktijdigheden.append(g)
    som_b = math.fsum(benuttingen)
    som_g = math.fsum(gelijktijdigheden)
    return Uitkomst(
        model=model.naam,
        parameters=model.parameters,
        som_benutting=som_b,
        som_gelijktijdigheid=som_g,
        kwartieren_in_berekening=len(volledig),
        kwartieren_uitgesloten=uitgesloten,
    )
