"""
Funcții utilitare comune pentru integrarea Vehicule.

Conține:
- Conversie date calendaristice (format românesc ZZ.LL.AAAA ↔ ISO YYYY-MM-DD)
- Validare date calendaristice și ani
- Conversie numerică (float → int pentru afișare curată)
- Formatare valori pentru afișare în senzori
- Pregătire valori sugerate pentru formulare
"""

from __future__ import annotations

from datetime import date
from typing import Any

from .const import (
    CONF_AN_FABRICATIE,
    CONF_AN_PRIMA_INMATRICULARE,
    CONF_ANVELOPE_IARNA_DATA,
    CONF_ANVELOPE_VARA_DATA,
    CONF_BATERIE_DATA_SCHIMB,
    CONF_CASCO_DATA_EMITERE,
    CONF_CASCO_DATA_EXPIRARE,
    CONF_DISCURI_FRANA_DATA,
    CONF_DISTRIBUTIE_DATA,
    CONF_EXTINCTOR_DATA_EXPIRARE,
    CONF_IMPOZIT_SCADENTA,
    CONF_ISTORIC,
    CONF_ITP_DATA_EXPIRARE,
    CONF_LEASING_DATA_EXPIRARE,
    CONF_PLACUTE_FRANA_DATA,
    CONF_RCA_DATA_EMITERE,
    CONF_RCA_DATA_EXPIRARE,
    CONF_REVIZIE_ULEI_DATA,
    CONF_ROVINIETA_DATA_INCEPUT,
    CONF_ROVINIETA_DATA_SFARSIT,
    CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE,
    STRUCTURA_CATEGORII,
)

# ─────────────────────────────────────────────
# Constante pentru tipuri de câmpuri
# ─────────────────────────────────────────────

# Câmpuri care conțin date calendaristice (stocate ISO, afișate ZZ.LL.AAAA)
CAMPURI_DATA: frozenset[str] = frozenset(
    {
        CONF_RCA_DATA_EMITERE,
        CONF_RCA_DATA_EXPIRARE,
        CONF_CASCO_DATA_EMITERE,
        CONF_CASCO_DATA_EXPIRARE,
        CONF_ITP_DATA_EXPIRARE,
        CONF_IMPOZIT_SCADENTA,
        CONF_LEASING_DATA_EXPIRARE,
        CONF_REVIZIE_ULEI_DATA,
        CONF_DISTRIBUTIE_DATA,
        CONF_ANVELOPE_VARA_DATA,
        CONF_ANVELOPE_IARNA_DATA,
        CONF_BATERIE_DATA_SCHIMB,
        CONF_PLACUTE_FRANA_DATA,
        CONF_DISCURI_FRANA_DATA,
        CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE,
        CONF_EXTINCTOR_DATA_EXPIRARE,
        CONF_ROVINIETA_DATA_INCEPUT,
        CONF_ROVINIETA_DATA_SFARSIT,
    }
)

# Câmpuri de tip an (TextSelector, stocate ca int)
CAMPURI_AN: frozenset[str] = frozenset(
    {
        CONF_AN_FABRICATIE,
        CONF_AN_PRIMA_INMATRICULARE,
    }
)

# Formatul afișat în UI (românesc)
FORMAT_DATA_RO = "ZZ.LL.AAAA"


# ─────────────────────────────────────────────
# Conversie date calendaristice
# ─────────────────────────────────────────────


def ro_la_iso(valoare: str) -> str | None:
    """Convertește o dată din format românesc (ZZ.LL.AAAA) în ISO (AAAA-LL-ZZ).

    Acceptă separatori: . - /
    Exemplu: 18.04.2026 → 2026-04-18
    Returnează None dacă conversia eșuează sau anul e în afara 1900-2100.
    """
    if not valoare or not valoare.strip():
        return None

    text = valoare.strip()

    # Dacă e deja format ISO (YYYY-MM-DD), validăm și returnăm
    if len(text) == 10 and text[4] == "-":
        try:
            d = date.fromisoformat(text)
            if not 1900 <= d.year <= 2100:
                return None
            return text
        except ValueError:
            pass

    # Încercăm format românesc: ZZ.LL.AAAA sau ZZ-LL-AAAA sau ZZ/LL/AAAA
    for separator in (".", "-", "/"):
        parti = text.split(separator)
        if len(parti) == 3:
            try:
                zi, luna, an = int(parti[0]), int(parti[1]), int(parti[2])
                if not 1900 <= an <= 2100:
                    continue
                data_convertita = date(an, luna, zi)
                return data_convertita.isoformat()
            except (ValueError, TypeError):
                continue

    return None


def iso_la_ro(valoare: str | None) -> str:
    """Convertește o dată ISO (AAAA-LL-ZZ) în format românesc (ZZ.LL.AAAA).

    Exemplu: 2026-04-18 → 18.04.2026
    Returnează string gol dacă valoarea e None/goală.
    """
    if not valoare:
        return ""
    try:
        d = date.fromisoformat(str(valoare))
        return f"{d.day:02d}.{d.month:02d}.{d.year}"
    except (ValueError, TypeError):
        return str(valoare)


def format_data_ro(valoare: Any) -> str | None:
    """Formatează o dată ISO pentru afișare în atributele senzorilor.

    Exemplu: 2026-04-18 → 18.04.2026
    Returnează None dacă valoarea e goală (pentru filtrare atribute).
    """
    if valoare is None or valoare == "":
        return None
    try:
        d = date.fromisoformat(str(valoare))
        return f"{d.day:02d}.{d.month:02d}.{d.year}"
    except (ValueError, TypeError):
        return str(valoare)


# ─────────────────────────────────────────────
# Conversie numerică
# ─────────────────────────────────────────────


def intreg(valoare: Any) -> int | None:
    """Convertește o valoare numerică la int (elimină .0 de la float-uri).

    NumberSelector din HA returnează float-uri (ex: 2010.0, 210544.0).
    Această funcție asigură afișarea corectă: 2010, 210544.
    Returnează None dacă valoarea e goală sau neconvertibilă.
    """
    if valoare is None or valoare == "":
        return None
    try:
        return int(float(valoare))
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────────────
# Validare formulare
# ─────────────────────────────────────────────


def valideaza_campuri_data(user_input: dict[str, Any]) -> dict[str, str]:
    """Validează toate câmpurile de tip dată din input.

    Returnează un dict de erori {cheie_camp: cod_eroare}.
    Dict gol = fără erori.
    """
    erori: dict[str, str] = {}
    for cheie, valoare in user_input.items():
        if cheie in CAMPURI_DATA and valoare and str(valoare).strip():
            if ro_la_iso(str(valoare)) is None:
                erori[cheie] = "format_data_invalid"
    return erori


def valideaza_campuri_an(
    user_input: dict[str, Any],
    an_max_fabricatie: int,
    an_max_inmatriculare: int,
) -> dict[str, str]:
    """Validează câmpurile de tip an din input.

    Returnează un dict de erori {cheie_camp: cod_eroare}.
    La succes, convertește valorile la int în user_input (in-place).
    """
    erori: dict[str, str] = {}

    limite = {
        CONF_AN_FABRICATIE: an_max_fabricatie,
        CONF_AN_PRIMA_INMATRICULARE: an_max_inmatriculare,
    }

    for cheie, an_max in limite.items():
        val = user_input.get(cheie)
        if val is not None and str(val).strip():
            try:
                an = int(str(val).strip())
                if not 1900 <= an <= an_max:
                    erori[cheie] = "an_invalid"
                else:
                    user_input[cheie] = an
            except (ValueError, TypeError):
                erori[cheie] = "an_invalid"

    return erori


# ─────────────────────────────────────────────
# Conversie date pentru stocare
# ─────────────────────────────────────────────


def converteste_date_la_iso(user_input: dict[str, Any]) -> dict[str, Any]:
    """Convertește toate câmpurile de dată din format RO în ISO pentru stocare."""
    rezultat = dict(user_input)
    for cheie in CAMPURI_DATA:
        if cheie in rezultat and rezultat[cheie]:
            iso = ro_la_iso(str(rezultat[cheie]))
            if iso:
                rezultat[cheie] = iso
    return rezultat


def pregateste_valori_sugerate(optiuni: dict[str, Any]) -> dict[str, Any]:
    """Pregătește valorile stocate pentru afișare în formulare.

    - Date calendaristice: ISO → format românesc (ZZ.LL.AAAA)
    - Ani: int/float → string (TextSelector necesită string)
    """
    rezultat = dict(optiuni)

    for cheie in CAMPURI_DATA:
        if cheie in rezultat and rezultat[cheie]:
            rezultat[cheie] = iso_la_ro(str(rezultat[cheie]))

    for cheie in CAMPURI_AN:
        if cheie in rezultat and rezultat[cheie] is not None:
            try:
                rezultat[cheie] = str(int(float(rezultat[cheie])))
            except (ValueError, TypeError):
                rezultat[cheie] = str(rezultat[cheie])

    return rezultat


# ─────────────────────────────────────────────
# Funcții calcul pentru senzori
# ─────────────────────────────────────────────


def zile_ramase(data_str: str | None) -> int | None:
    """Calculează zilele rămase până la o dată ISO.

    Returnează valoare negativă dacă data a trecut (document expirat).
    """
    if not data_str:
        return None
    try:
        data_tinta = date.fromisoformat(str(data_str))
        return (data_tinta - date.today()).days
    except (ValueError, TypeError):
        return None


def km_ramasi(km_curent: Any, km_urmator: Any) -> int | None:
    """Calculează km rămași până la următoarea intervenție.

    Returnează valoare negativă dacă intervenția e depășită.
    """
    if km_curent is None or km_urmator is None:
        return None
    try:
        return int(float(km_urmator)) - int(float(km_curent))
    except (ValueError, TypeError):
        return None


def luni_de_la(data_str: str | None) -> int | None:
    """Calculează lunile trecute de la o dată ISO."""
    if not data_str:
        return None
    try:
        data_ref = date.fromisoformat(str(data_str))
        azi = date.today()
        return (azi.year - data_ref.year) * 12 + (azi.month - data_ref.month)
    except (ValueError, TypeError):
        return None


def sezon_anvelope(date_vara: str | None, date_iarna: str | None) -> str | None:
    """Determină sezonul anvelopelor montate pe baza ultimei schimbări."""
    if not date_vara and not date_iarna:
        return None
    if date_vara and not date_iarna:
        return "Vară"
    if date_iarna and not date_vara:
        return "Iarnă"
    try:
        d_vara = date.fromisoformat(str(date_vara))
        d_iarna = date.fromisoformat(str(date_iarna))
        return "Vară" if d_vara > d_iarna else "Iarnă"
    except (ValueError, TypeError):
        return None


def stare_document(data_str: str | None) -> str | None:
    """Returnează starea unui document pe baza datei de expirare (Valid/Expirat)."""
    zile = zile_ramase(data_str)
    if zile is None:
        return None
    return "Expirat" if zile < 0 else "Valid"


# ─────────────────────────────────────────────
# Structurare / aplatizare opțiuni (export/import)
# ─────────────────────────────────────────────


def _extrage_campuri(
    sursa: dict[str, Any], campuri: list[tuple[str, str]]
) -> dict[str, Any]:
    """Extrage câmpurile non-goale dintr-un dicționar sursă."""
    rezultat: dict[str, Any] = {}
    for cheie_json, cheie_conf in campuri:
        val = sursa.get(cheie_conf)
        if val is not None and val != "":
            rezultat[cheie_json] = val
    return rezultat


def structureaza_optiuni(optiuni: dict[str, Any]) -> dict[str, Any]:
    """Structurează opțiunile flat pe categorii pentru export.

    Transformă dicționarul flat din entry.options într-o structură
    ierarhică pe categorii și subcategorii.
    Istoric-ul este extras separat la nivel superior.
    """
    rezultat: dict[str, Any] = {}

    for categorie, continut in STRUCTURA_CATEGORII:
        if isinstance(continut, list):
            sectiune = _extrage_campuri(optiuni, continut)
            if sectiune:
                rezultat[categorie] = sectiune
        elif isinstance(continut, dict):
            sectiune: dict[str, Any] = {}
            for sub_categorie, campuri in continut.items():
                sub_sectiune = _extrage_campuri(optiuni, campuri)
                if sub_sectiune:
                    sectiune[sub_categorie] = sub_sectiune
            if sectiune:
                rezultat[categorie] = sectiune

    # Istoric (separat – este o listă, nu face parte din categorii)
    istoric = optiuni.get(CONF_ISTORIC)
    if istoric:
        rezultat["istoric"] = istoric

    return rezultat


def aplatizeaza_optiuni(structurat: dict[str, Any]) -> dict[str, Any]:
    """Aplatizează opțiunile structurate pe categorii într-un dict flat.

    Inversul lui structureaza_optiuni(). Folosit la import pentru
    a reconstrui dicționarul entry.options din JSON structurat.
    """
    rezultat: dict[str, Any] = {}

    for categorie, continut in STRUCTURA_CATEGORII:
        sectiune = structurat.get(categorie, {})
        if not isinstance(sectiune, dict):
            continue

        if isinstance(continut, list):
            for cheie_json, cheie_conf in continut:
                if cheie_json in sectiune:
                    rezultat[cheie_conf] = sectiune[cheie_json]
        elif isinstance(continut, dict):
            for sub_categorie, campuri in continut.items():
                sub_sectiune = sectiune.get(sub_categorie, {})
                if not isinstance(sub_sectiune, dict):
                    continue
                for cheie_json, cheie_conf in campuri:
                    if cheie_json in sub_sectiune:
                        rezultat[cheie_conf] = sub_sectiune[cheie_json]

    # Istoric
    istoric = structurat.get("istoric")
    if istoric:
        rezultat[CONF_ISTORIC] = istoric

    return rezultat
