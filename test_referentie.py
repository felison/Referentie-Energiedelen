"""Tests voor de referentie en de verdeelmodellen. Alleen standaardbibliotheek:

    python -m unittest discover -s tests
"""

import json
import os
import random
import subprocess
import sys
import unittest

HIER = os.path.dirname(os.path.abspath(__file__))
WORTEL = os.path.dirname(HIER)
sys.path.insert(0, WORTEL)

from kwartiergelijktijdigheid import (  # noqa: E402
    DynamischeSleutel,
    GemeenschapGelijk,
    GemeenschapMetVoorrang,
    GemeenschapNaarVerbruik,
    Kwartier,
    VasteSleutel,
    benuttingsgraad,
    gemeenschapskwartiergelijktijdigheid,
)

GEMEENSCHAP = ["A", "B", "C", "D", "E"]
VAST = VasteSleutel({"A": {"B": 0.5, "C": 0.5}, "D": {"E": 1.0}})
DYNAMISCH = DynamischeSleutel({"A": ["B", "C"], "D": ["E"]})


def kwartier(start, a_in, d_in=0.2, b=0.6, c=0.1, e=0.4):
    return Kwartier(
        start=start,
        invoeding={"A": a_in, "B": 0.0, "C": 0.0, "D": d_in, "E": 0.0},
        afname={"A": 0.0, "B": b, "C": c, "D": 0.0, "E": e},
    )


# Testgeval uit het handboek: overschot in de gemeenschap
OVERSCHOT = kwartier("k1", 1.0)
# Variant met tekort: A levert 0,5 kWh in plaats van 1,0 kWh
TEKORT = kwartier("k2", 0.5)


class TestGelijktijdigheid(unittest.TestCase):
    def test_overschot(self):
        self.assertAlmostEqual(gemeenschapskwartiergelijktijdigheid(OVERSCHOT), 1.1)

    def test_tekort(self):
        self.assertAlmostEqual(gemeenschapskwartiergelijktijdigheid(TEKORT), 0.7)

    def test_negatieve_meting_geweigerd(self):
        with self.assertRaises(ValueError):
            Kwartier("x", {"A": -0.1}, {"A": 0.0})


class TestModellenPerKwartier(unittest.TestCase):
    def test_vaste_sleutel_overschot(self):
        v = VAST.verdeling(OVERSCHOT)
        self.assertAlmostEqual(v["B"], 0.5)
        self.assertAlmostEqual(v["C"], 0.1)
        self.assertAlmostEqual(v["E"], 0.2)
        self.assertAlmostEqual(VAST.benutting(OVERSCHOT), 0.8)

    def test_dynamische_sleutel_overschot(self):
        self.assertAlmostEqual(DYNAMISCH.benutting(OVERSCHOT), 0.9)

    def test_vaste_sleutel_tekort(self):
        self.assertAlmostEqual(VAST.benutting(TEKORT), 0.55)

    def test_dynamische_sleutel_tekort_haalt_toevallig_het_maximum(self):
        self.assertAlmostEqual(DYNAMISCH.benutting(TEKORT), 0.7)

    def test_gemeenschapsmodellen_halen_altijd_het_maximum(self):
        for model in (GemeenschapNaarVerbruik(), GemeenschapGelijk(),
                      GemeenschapMetVoorrang(["C", "E"])):
            for k in (OVERSCHOT, TEKORT):
                self.assertAlmostEqual(
                    model.benutting(k), gemeenschapskwartiergelijktijdigheid(k),
                    msg=f"{model.naam} in {k.start}",
                )

    def test_verdeling_gemeenschap_tekort(self):
        verbruik = GemeenschapNaarVerbruik().verdeling(TEKORT)
        self.assertAlmostEqual(verbruik["B"], 0.6 * 0.7 / 1.1)
        gelijk = GemeenschapGelijk().verdeling(TEKORT)
        self.assertAlmostEqual(gelijk["B"], 0.3)
        self.assertAlmostEqual(gelijk["C"], 0.1)
        self.assertAlmostEqual(gelijk["E"], 0.3)
        voorrang = GemeenschapMetVoorrang(["C", "E"]).verdeling(TEKORT)
        self.assertAlmostEqual(voorrang["C"], 0.1)
        self.assertAlmostEqual(voorrang["E"], 0.4)
        self.assertAlmostEqual(voorrang["B"], 0.2)

    def test_ongeldige_fracties(self):
        with self.assertRaises(ValueError):
            VasteSleutel({"A": {"B": 0.7, "C": 0.6}})

    def test_ontvanger_met_twee_gevers_geweigerd(self):
        with self.assertRaises(ValueError):
            DynamischeSleutel({"A": ["B"], "D": ["B"]})


class TestBenuttingsgraad(unittest.TestCase):
    def test_periode_is_verhouding_van_sommen(self):
        uitkomst = benuttingsgraad([OVERSCHOT, TEKORT], GEMEENSCHAP, VAST)
        self.assertAlmostEqual(uitkomst.som_gelijktijdigheid, 1.8)
        self.assertAlmostEqual(uitkomst.som_benutting, 1.35)
        self.assertAlmostEqual(uitkomst.benuttingsgraad, 0.75)

    def test_testgeval_handboek(self):
        self.assertAlmostEqual(
            benuttingsgraad([OVERSCHOT], GEMEENSCHAP, VAST).benuttingsgraad, 0.8 / 1.1)
        self.assertAlmostEqual(
            benuttingsgraad([OVERSCHOT], GEMEENSCHAP, DYNAMISCH).benuttingsgraad, 0.9 / 1.1)
        self.assertAlmostEqual(
            benuttingsgraad([OVERSCHOT], GEMEENSCHAP, GemeenschapNaarVerbruik()).benuttingsgraad,
            1.0)

    def test_onvolledig_kwartier_uitgesloten(self):
        onvolledig = Kwartier("k3", {"A": 0.8}, {"A": 0.0, "B": 0.5})
        uitkomst = benuttingsgraad([OVERSCHOT, onvolledig], GEMEENSCHAP, VAST)
        self.assertEqual(uitkomst.kwartieren_in_berekening, 1)
        self.assertEqual(uitkomst.kwartieren_uitgesloten, 1)
        self.assertAlmostEqual(uitkomst.dekking, 0.5)

    def test_lege_periode_niet_gedefinieerd(self):
        nul = Kwartier("k0", {a: 0.0 for a in GEMEENSCHAP}, {a: 0.0 for a in GEMEENSCHAP})
        self.assertIsNone(benuttingsgraad([nul], GEMEENSCHAP, VAST).benuttingsgraad)


class TestInvarianten(unittest.TestCase):
    """0 <= B_m(k) <= G(k) voor willekeurige meetgegevens (REFERENTIE.md 4)."""

    def test_willekeurige_kwartieren(self):
        rng = random.Random(20271014)
        leden = [f"H{n}" for n in range(12)]
        vast = VasteSleutel({
            "H0": {"H1": 0.3, "H2": 0.3, "H3": 0.4},
            "H4": {"H5": 0.5, "H6": 0.5},
            "H7": {"H8": 0.6},
        })
        dynamisch = DynamischeSleutel({"H0": ["H1", "H2", "H3"], "H4": ["H5", "H6"], "H7": ["H8"]})
        modellen = [vast, dynamisch, GemeenschapNaarVerbruik(), GemeenschapGelijk(),
                    GemeenschapMetVoorrang(["H9", "H10"])]
        kwartieren = []
        for n in range(2000):
            kwartieren.append(Kwartier(
                start=f"k{n}",
                invoeding={a: rng.choice([0.0, rng.uniform(0, 1.5)]) for a in leden},
                afname={a: rng.choice([0.0, rng.uniform(0, 1.0)]) for a in leden},
            ))
        for model in modellen:
            uitkomst = benuttingsgraad(kwartieren, leden, model)  # controleert per kwartier
            self.assertGreaterEqual(uitkomst.benuttingsgraad, 0.0)
            self.assertLessEqual(uitkomst.benuttingsgraad, 1.0 + 1e-12)
        for model in modellen[2:]:
            self.assertAlmostEqual(benuttingsgraad(kwartieren, leden, model).benuttingsgraad, 1.0)


class TestOpdrachtregel(unittest.TestCase):
    def test_voorbeeld(self):
        uitvoer = subprocess.run(
            [sys.executable, "-m", "kwartiergelijktijdigheid",
             os.path.join(WORTEL, "voorbeelden", "testgeval.csv"),
             os.path.join(WORTEL, "voorbeelden", "modellen.json")],
            cwd=WORTEL, capture_output=True, text=True, check=True,
        ).stdout
        resultaat = json.loads(uitvoer)
        graden = {u["model"]: u["benuttingsgraad"] for u in resultaat["uitkomsten"]}
        self.assertAlmostEqual(graden["vaste_sleutel"], 0.75)
        self.assertAlmostEqual(graden["dynamische_sleutel"], 1.6 / 1.8)
        self.assertAlmostEqual(graden["gemeenschap_naar_verbruik"], 1.0)
        self.assertEqual(resultaat["uitkomsten"][0]["kwartieren_uitgesloten"], 1)


if __name__ == "__main__":
    unittest.main()
