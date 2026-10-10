"""Inlezen van kwartierwaarden volgens DATAFORMAAT.md."""

from __future__ import annotations

import csv
from collections import OrderedDict
from typing import List, Set, Tuple

from .referentie import Kwartier

KOLOMMEN = ("aansluiting", "kwartier_start", "invoeding_kwh", "afname_kwh")


def _getal(tekst: str, rij: int, kolom: str):
    tekst = (tekst or "").strip()
    if tekst == "":
        return None  # ontbrekende meting
    try:
        return float(tekst)
    except ValueError as fout:
        raise ValueError(f"Rij {rij}, kolom {kolom}: geen getal: {tekst!r}") from fout


def lees_kwartieren(pad: str) -> Tuple[List[Kwartier], Set[str]]:
    """Lees een CSV in lang formaat en groepeer per kwartier.

    Een lege cel betekent een ontbrekende meting; dat kwartier valt dan buiten
    de berekening (REFERENTIE.md 3.4).
    """
    per_kwartier: "OrderedDict[str, tuple]" = OrderedDict()
    aansluitingen: Set[str] = set()
    with open(pad, newline="", encoding="utf-8") as f:
        lezer = csv.DictReader(f)
        ontbreekt = [k for k in KOLOMMEN if k not in (lezer.fieldnames or [])]
        if ontbreekt:
            raise ValueError(f"Ontbrekende kolommen in {pad}: {', '.join(ontbreekt)}")
        for nummer, rij in enumerate(lezer, start=2):
            a = rij["aansluiting"].strip()
            k = rij["kwartier_start"].strip()
            aansluitingen.add(a)
            invoeding, afname = per_kwartier.setdefault(k, ({}, {}))
            i = _getal(rij["invoeding_kwh"], nummer, "invoeding_kwh")
            o = _getal(rij["afname_kwh"], nummer, "afname_kwh")
            if a in invoeding or a in afname:
                raise ValueError(f"Rij {nummer}: dubbele waarde voor {a} in kwartier {k}")
            if i is not None:
                invoeding[a] = i
            if o is not None:
                afname[a] = o
    kwartieren = [
        Kwartier(start=k, invoeding=inv, afname=af)
        for k, (inv, af) in sorted(per_kwartier.items())
    ]
    return kwartieren, aansluitingen
