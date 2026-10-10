"""Opdrachtregel: bereken de benuttingsgraad van verdeelmodellen op meetgegevens.

Gebruik:

    python -m kwartiergelijktijdigheid metingen.csv modellen.json

metingen.csv volgt DATAFORMAAT.md; modellen.json bevat een lijst modelconfiguraties
en optioneel de samenstelling van de gemeenschap. De uitkomst gaat als JSON naar
standaarduitvoer, met alle velden die REFERENTIE.md 6 voorschrijft.
"""

from __future__ import annotations

import argparse
import json
import sys

from .inlezen import lees_kwartieren
from .modellen import model_uit_config
from .referentie import REFERENTIEVERSIE, benuttingsgraad


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m kwartiergelijktijdigheid",
        description="Benuttingsgraad van verdeelmodellen ten opzichte van de "
        "gemeenschapskwartiergelijktijdigheid (referentie " + REFERENTIEVERSIE + ").",
    )
    parser.add_argument("metingen", help="CSV met kwartierwaarden per aansluiting")
    parser.add_argument("modellen", help="JSON met gemeenschap en modelconfiguraties")
    args = parser.parse_args(argv)

    kwartieren, aansluitingen = lees_kwartieren(args.metingen)
    with open(args.modellen, encoding="utf-8") as f:
        config = json.load(f)
    gemeenschap = config.get("gemeenschap") or sorted(aansluitingen)

    uitkomsten = []
    for modelconfig in config["modellen"]:
        model = model_uit_config(modelconfig)
        uitkomsten.append(benuttingsgraad(kwartieren, gemeenschap, model).als_dict())

    json.dump(
        {
            "referentieversie": REFERENTIEVERSIE,
            "gemeenschap": gemeenschap,
            "aantal_aansluitingen": len(gemeenschap),
            "bron_metingen": config.get("bron_metingen"),
            "uitkomsten": uitkomsten,
        },
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
