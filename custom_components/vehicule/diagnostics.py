"""
Diagnosticare pentru integrarea Vehicule.

Exportă informații de diagnostic structurate pe categorii,
mascând datele sensibile (VIN, serie CIV, nr. poliță, etc.).
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_AN_FABRICATIE,
    CONF_AN_PRIMA_INMATRICULARE,
    CONF_ANVELOPE_COST,
    CONF_ANVELOPE_IARNA_DATA,
    CONF_ANVELOPE_VARA_DATA,
    CONF_BATERIE_COST,
    CONF_BATERIE_DATA_SCHIMB,
    CONF_CAPACITATE_CILINDRICA,
    CONF_CASCO_COMPANIE,
    CONF_CASCO_COST,
    CONF_CASCO_DATA_EMITERE,
    CONF_CASCO_DATA_EXPIRARE,
    CONF_CASCO_NUMAR_POLITA,
    CONF_COMBUSTIBIL,
    CONF_DISCURI_FRANA_COST,
    CONF_DISCURI_FRANA_DATA,
    CONF_DISCURI_FRANA_KM_ULTIMUL,
    CONF_DISCURI_FRANA_KM_URMATOR,
    CONF_DISTRIBUTIE_COST,
    CONF_DISTRIBUTIE_DATA,
    CONF_DISTRIBUTIE_KM_ULTIMUL,
    CONF_DISTRIBUTIE_KM_URMATOR,
    CONF_EXTINCTOR_DATA_EXPIRARE,
    CONF_IMPOZIT_LOCALITATE,
    CONF_IMPOZIT_SCADENTA,
    CONF_IMPOZIT_SUMA,
    CONF_ISTORIC,
    CONF_ITP_DATA_EXPIRARE,
    CONF_ITP_KILOMETRAJ,
    CONF_ITP_STATIE,
    CONF_KM_CURENT,
    CONF_LEASING_DATA_EXPIRARE,
    CONF_MARCA,
    CONF_MODEL,
    CONF_MOTORIZARE,
    CONF_NR_INMATRICULARE,
    CONF_PLACUTE_FRANA_COST,
    CONF_PLACUTE_FRANA_DATA,
    CONF_PLACUTE_FRANA_KM_ULTIMUL,
    CONF_PLACUTE_FRANA_KM_URMATOR,
    CONF_PROPRIETAR,
    CONF_PUTERE_CP,
    CONF_PUTERE_KW,
    CONF_RCA_COMPANIE,
    CONF_RCA_COST,
    CONF_RCA_DATA_EMITERE,
    CONF_RCA_DATA_EXPIRARE,
    CONF_RCA_NUMAR_POLITA,
    CONF_REVIZIE_ULEI_COST,
    CONF_REVIZIE_ULEI_DATA,
    CONF_REVIZIE_ULEI_KM_ULTIMUL,
    CONF_REVIZIE_ULEI_KM_URMATOR,
    CONF_ROVINIETA_CATEGORIE,
    CONF_ROVINIETA_DATA_INCEPUT,
    CONF_ROVINIETA_DATA_SFARSIT,
    CONF_ROVINIETA_PRET,
    CONF_SERIE_CIV,
    CONF_TIP_PROPRIETATE,
    CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE,
    CONF_VIN,
    DOMAIN,
    normalizeaza_numar,
)

# ─────────────────────────────────────────────
# Câmpuri sensibile (se maschează în diagnostic)
# ─────────────────────────────────────────────
CAMPURI_SENSIBILE: frozenset[str] = frozenset(
    {
        CONF_VIN,
        CONF_SERIE_CIV,
        CONF_NR_INMATRICULARE,
        CONF_RCA_NUMAR_POLITA,
        CONF_CASCO_NUMAR_POLITA,
        CONF_PROPRIETAR,
    }
)


# ─────────────────────────────────────────────
# Structura categoriilor pentru export
# ─────────────────────────────────────────────
# Fiecare categorie: (titlu_secțiune, [(eticheta, cheie_const), ...])
_CATEGORII_DIAGNOSTIC: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "identificare",
        [
            ("nr_inmatriculare", CONF_NR_INMATRICULARE),
            ("serie_civ", CONF_SERIE_CIV),
            ("vin", CONF_VIN),
            ("marca", CONF_MARCA),
            ("model", CONF_MODEL),
            ("an_fabricatie", CONF_AN_FABRICATIE),
            ("an_prima_inmatriculare", CONF_AN_PRIMA_INMATRICULARE),
            ("motorizare", CONF_MOTORIZARE),
            ("combustibil", CONF_COMBUSTIBIL),
            ("capacitate_cilindrica", CONF_CAPACITATE_CILINDRICA),
            ("putere_kw", CONF_PUTERE_KW),
            ("putere_cp", CONF_PUTERE_CP),
            ("proprietar", CONF_PROPRIETAR),
            ("tip_proprietate", CONF_TIP_PROPRIETATE),
        ],
    ),
    (
        "kilometraj",
        [
            ("km_curent", CONF_KM_CURENT),
        ],
    ),
    (
        "rca",
        [
            ("numar_polita", CONF_RCA_NUMAR_POLITA),
            ("companie", CONF_RCA_COMPANIE),
            ("data_emitere", CONF_RCA_DATA_EMITERE),
            ("data_expirare", CONF_RCA_DATA_EXPIRARE),
            ("cost", CONF_RCA_COST),
        ],
    ),
    (
        "casco",
        [
            ("numar_polita", CONF_CASCO_NUMAR_POLITA),
            ("companie", CONF_CASCO_COMPANIE),
            ("data_emitere", CONF_CASCO_DATA_EMITERE),
            ("data_expirare", CONF_CASCO_DATA_EXPIRARE),
            ("cost", CONF_CASCO_COST),
        ],
    ),
    (
        "itp",
        [
            ("data_expirare", CONF_ITP_DATA_EXPIRARE),
            ("statie", CONF_ITP_STATIE),
            ("kilometraj", CONF_ITP_KILOMETRAJ),
        ],
    ),
    (
        "rovinieta",
        [
            ("data_inceput", CONF_ROVINIETA_DATA_INCEPUT),
            ("data_sfarsit", CONF_ROVINIETA_DATA_SFARSIT),
            ("categorie", CONF_ROVINIETA_CATEGORIE),
            ("pret", CONF_ROVINIETA_PRET),
        ],
    ),
    (
        "administrativ",
        [
            ("impozit_suma", CONF_IMPOZIT_SUMA),
            ("impozit_scadenta", CONF_IMPOZIT_SCADENTA),
            ("impozit_localitate", CONF_IMPOZIT_LOCALITATE),
            ("leasing_data_expirare", CONF_LEASING_DATA_EXPIRARE),
        ],
    ),
    (
        "revizie_ulei",
        [
            ("km_ultimul", CONF_REVIZIE_ULEI_KM_ULTIMUL),
            ("km_urmator", CONF_REVIZIE_ULEI_KM_URMATOR),
            ("data", CONF_REVIZIE_ULEI_DATA),
            ("cost", CONF_REVIZIE_ULEI_COST),
        ],
    ),
    (
        "distributie",
        [
            ("km_ultimul", CONF_DISTRIBUTIE_KM_ULTIMUL),
            ("km_urmator", CONF_DISTRIBUTIE_KM_URMATOR),
            ("data", CONF_DISTRIBUTIE_DATA),
            ("cost", CONF_DISTRIBUTIE_COST),
        ],
    ),
    (
        "anvelope",
        [
            ("data_vara", CONF_ANVELOPE_VARA_DATA),
            ("data_iarna", CONF_ANVELOPE_IARNA_DATA),
            ("cost", CONF_ANVELOPE_COST),
        ],
    ),
    (
        "baterie",
        [
            ("data_schimb", CONF_BATERIE_DATA_SCHIMB),
            ("cost", CONF_BATERIE_COST),
        ],
    ),
    (
        "frane",
        [
            ("placute_km_ultimul", CONF_PLACUTE_FRANA_KM_ULTIMUL),
            ("placute_km_urmator", CONF_PLACUTE_FRANA_KM_URMATOR),
            ("placute_data", CONF_PLACUTE_FRANA_DATA),
            ("placute_cost", CONF_PLACUTE_FRANA_COST),
            ("discuri_km_ultimul", CONF_DISCURI_FRANA_KM_ULTIMUL),
            ("discuri_km_urmator", CONF_DISCURI_FRANA_KM_URMATOR),
            ("discuri_data", CONF_DISCURI_FRANA_DATA),
            ("discuri_cost", CONF_DISCURI_FRANA_COST),
        ],
    ),
    (
        "echipament_obligatoriu",
        [
            ("trusa_prim_ajutor_data_expirare", CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE),
            ("extinctor_data_expirare", CONF_EXTINCTOR_DATA_EXPIRARE),
        ],
    ),
]


# ─────────────────────────────────────────────
# Funcții de mascare
# ─────────────────────────────────────────────


def _mascheaza(cheie: str, valoare: Any) -> Any:
    """Maschează valorile sensibile, păstrând primul și ultimele 2 caractere."""
    if cheie not in CAMPURI_SENSIBILE:
        return valoare
    if valoare is None or valoare == "":
        return valoare
    text = str(valoare)
    if len(text) <= 4:
        return "****"
    return f"{text[:1]}{'*' * (len(text) - 3)}{text[-2:]}"


# ─────────────────────────────────────────────
# Construcție diagnostic structurat
# ─────────────────────────────────────────────


def _extrage_categorie(
    sursa: dict[str, Any],
    campuri: list[tuple[str, str]],
) -> dict[str, Any]:
    """Extrage și maschează câmpurile unei categorii din datele vehiculului."""
    rezultat: dict[str, Any] = {}
    for eticheta, cheie_const in campuri:
        val = sursa.get(cheie_const)
        if val is not None and val != "":
            rezultat[eticheta] = _mascheaza(cheie_const, val)
    return rezultat


def _structureaza_istoric(
    istoric: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Structurează lista de intrări istorice pentru export."""
    if not isinstance(istoric, list):
        return []
    rezultat: list[dict[str, Any]] = []
    for intrare in istoric:
        if not isinstance(intrare, dict):
            continue
        rezultat.append(
            {
                "tip": intrare.get("tip", "necunoscut"),
                "data_arhivare": intrare.get("data_arhivare"),
                "date": intrare.get("date", {}),
            }
        )
    return rezultat


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Returnează datele de diagnostic structurate pe categorii."""
    # Combinăm data + options (la fel ca în sensor.py)
    toate_datele: dict[str, Any] = {**entry.data, **entry.options}
    numar_normalizat = normalizeaza_numar(
        entry.data.get(CONF_NR_INMATRICULARE, "")
    )

    # ── Categorii structurate ──
    categorii: dict[str, Any] = {}
    for titlu, campuri in _CATEGORII_DIAGNOSTIC:
        sectiune = _extrage_categorie(toate_datele, campuri)
        if sectiune:
            categorii[titlu] = sectiune

    # ── Istoric (arhivă) ──
    istoric_raw = toate_datele.get(CONF_ISTORIC, [])
    istoric = _structureaza_istoric(istoric_raw)

    # ── Senzori activi ──
    senzori_activi = [
        entitate.entity_id
        for entitate in hass.states.async_all("sensor")
        if entitate.entity_id.startswith(
            f"sensor.vehicule_{numar_normalizat}"
        )
    ]

    return {
        "intrare": {
            "titlu": _mascheaza(
                CONF_NR_INMATRICULARE,
                entry.title,
            ),
            "versiune": entry.version,
            "domeniu": DOMAIN,
        },
        "categorii": categorii,
        "istoric": istoric,
        "stare": {
            "senzori_activi": len(senzori_activi),
            "lista_senzori": sorted(senzori_activi),
        },
    }
