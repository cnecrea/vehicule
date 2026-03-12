"""
Diagnosticare pentru integrarea Vehicule.

Exportă informații de diagnostic pentru depanare, mascând datele sensibile.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_NR_INMATRICULARE,
    CONF_PROPRIETAR,
    CONF_RCA_NUMAR_POLITA,
    CONF_SERIE_CIV,
    CONF_VIN,
    DOMAIN,
)

# Câmpuri care conțin date sensibile și vor fi mascate
CAMPURI_SENSIBILE = {
    CONF_VIN,
    CONF_SERIE_CIV,
    CONF_NR_INMATRICULARE,
    CONF_RCA_NUMAR_POLITA,
    CONF_PROPRIETAR,
}


def _mascheaza_valoare(cheie: str, valoare: Any) -> Any:
    """Maschează valorile sensibile, păstrând primele și ultimele caractere."""
    if cheie not in CAMPURI_SENSIBILE:
        return valoare

    if valoare is None or valoare == "":
        return valoare

    text = str(valoare)
    if len(text) <= 4:
        return "****"

    # Păstrăm primul și ultimele 2 caractere
    return f"{text[:1]}{'*' * (len(text) - 3)}{text[-2:]}"


def _mascheaza_dict(date: dict[str, Any]) -> dict[str, Any]:
    """Maschează toate câmpurile sensibile dintr-un dicționar."""
    return {
        cheie: _mascheaza_valoare(cheie, valoare)
        for cheie, valoare in date.items()
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Returnează datele de diagnostic pentru o intrare de configurare."""
    return {
        "intrare": {
            "titlu": _mascheaza_valoare(
                CONF_NR_INMATRICULARE,
                entry.title,
            ),
            "versiune": entry.version,
            "domeniu": DOMAIN,
        },
        "date_configurare": _mascheaza_dict(dict(entry.data)),
        "optiuni": _mascheaza_dict(dict(entry.options)),
        "stare": {
            "numar_senzori": len(
                [
                    entitate
                    for entitate in hass.states.async_all("sensor")
                    if entitate.entity_id.startswith(
                        f"sensor.vehicule_{entry.data.get(CONF_NR_INMATRICULARE, '').lower().replace(' ', '_')}"
                    )
                ]
            ),
        },
    }
