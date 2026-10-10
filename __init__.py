"""Referentie-implementatie gemeenschapskwartiergelijktijdigheid en benuttingsgraad."""

from .referentie import (
    REFERENTIEVERSIE,
    Kwartier,
    Uitkomst,
    benuttingsgraad,
    gemeenschapskwartierafname,
    gemeenschapskwartiergelijktijdigheid,
    gemeenschapskwartierinvoeding,
)
from .modellen import (
    DynamischeSleutel,
    GemeenschapGelijk,
    GemeenschapMetVoorrang,
    GemeenschapNaarVerbruik,
    VasteSleutel,
    model_uit_config,
)

__version__ = REFERENTIEVERSIE

__all__ = [
    "REFERENTIEVERSIE",
    "Kwartier",
    "Uitkomst",
    "benuttingsgraad",
    "gemeenschapskwartierafname",
    "gemeenschapskwartiergelijktijdigheid",
    "gemeenschapskwartierinvoeding",
    "DynamischeSleutel",
    "GemeenschapGelijk",
    "GemeenschapMetVoorrang",
    "GemeenschapNaarVerbruik",
    "VasteSleutel",
    "model_uit_config",
]
