"""
Platforma de senzori pentru integrarea Vehicule.

Senzorii sunt CONDIȚIONAȚI – apar DOAR când au date completate.
La prima configurare (doar nr. de înmatriculare), apare doar senzorul Informații.
Pe măsură ce utilizatorul completează date, apar senzorii corespunzători.

Senzori posibili per vehicul:
- Informații generale (marcă, model, etc.) – mereu vizibil
- Kilometraj curent – vizibil când km_curent este setat
- RCA (zile rămase) – vizibil când rca_data_expirare este setat
- Casco (zile rămase) – vizibil când casco_data_expirare este setat
- ITP (zile rămase) – vizibil când itp_data_expirare este setat
- Rovinieta (zile rămase) – vizibil când rovinieta_data_sfarsit este setat
- Impozit (zile rămase) – vizibil când impozit_scadenta este setat
- Leasing (zile rămase) – vizibil DOAR dacă tip_proprietate = leasing
- Revizie ulei (km rămași) – vizibil când revizie_ulei_km_urmator este setat
- Distribuție (km rămași) – vizibil când distributie_km_urmator este setat
- Anvelope (sezon) – vizibil când cel puțin o dată de montare este setată
- Baterie (luni de la schimb) – vizibil când baterie_data_schimb este setat
- Plăcuțe frână (km rămași) – vizibil când placute_frana_km_urmator este setat
- Discuri frână (km rămași) – vizibil când discuri_frana_km_urmator este setat
- Trusă prim ajutor (zile rămase) – vizibil când trusa_prim_ajutor_data_expirare este setat
- Extinctor (zile rămase) – vizibil când extinctor_data_expirare este setat
- Cost total (RON) – vizibil când cel puțin un cost este completat
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    CONF_SOFERI,
    CONF_SOFER_CATEGORIE_PERMIS,
    CONF_SOFER_DATA_EXPIRARE_PERMIS,
    CONF_SOFER_NUME,
    CONF_SOFER_CNP,
    CONF_SOFER_NR_PERMIS,
    CONF_TIP_PROPRIETATE,
    CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE,
    CONF_VIN,
    DOMAIN,
    LICENSE_DATA_KEY,
    normalizeaza_numar,
)
from .helpers import (
    format_data_ro,
    intreg,
    km_ramasi,
    luni_de_la,
    sezon_anvelope,
    stare_document,
    zile_ramase,
)

_LOGGER = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Funcții utilitare locale (specifice senzorilor)
# ─────────────────────────────────────────────


def _are_valoare(data: dict[str, Any], *chei: str) -> bool:
    """Verifică dacă cel puțin una din chei are o valoare non-goală în date."""
    return any(data.get(k) not in (None, "") for k in chei)


# ─────────────────────────────────────────────
# Traducere atribute (RO → EN)
# ─────────────────────────────────────────────

# Chei de atribute: RO → EN
_TRAD_CHEI_EN: dict[str, str] = {
    # Informații
    "Nr. înmatriculare": "License plate",
    "Serie CIV": "CIV serial",
    "VIN": "VIN",
    "Marcă": "Make",
    "Model": "Model",
    "Motorizare": "Engine type",
    "Combustibil": "Fuel type",
    "An fabricație": "Year of manufacture",
    "An prima înmatriculare": "First registration year",
    "Capacitate cilindrică (cm³)": "Engine displacement (cm³)",
    "Putere (kW)": "Power (kW)",
    "Putere (CP)": "Power (HP)",
    # Asigurări / documente
    "Număr poliță": "Policy number",
    "Companie": "Company",
    "Data emitere": "Issue date",
    "Data expirare": "Expiry date",
    "Data început": "Start date",
    "Data sfârșit": "End date",
    "Cost (RON)": "Cost (RON)",
    "Preț (RON)": "Price (RON)",
    "Stare": "Status",
    "Categorie": "Category",
    "Stație": "Station",
    "Kilometraj la ITP": "Mileage at ITP",
    # Administrativ
    "Sumă (RON)": "Amount (RON)",
    "Scadență": "Due date",
    "Localitate": "Locality",
    "Primărie / localitate": "City hall / locality",
    "Proprietar": "Owner",
    "Tip proprietate": "Ownership type",
    # Mentenanță
    "Km ultima revizie": "Km at last service",
    "Km următoarea revizie": "Km at next service",
    "Data ultima revizie": "Last service date",
    "Km ultima schimbare": "Km at last replacement",
    "Km următoarea schimbare": "Km at next replacement",
    "Data ultima schimbare": "Last replacement date",
    "Data schimbare": "Replacement date",
    "Data schimb": "Replacement date",
    "Km curent": "Current mileage",
    "Data montare vară": "Summer tires fitting date",
    "Data montare iarnă": "Winter tires fitting date",
    "Sezon recomandat": "Recommended season",
    # Cost total
    "Total general (RON)": "Grand total (RON)",
    # Istoric
    "Reînnoiri anterioare": "Previous renewals",
    "Ultima arhivare": "Last archival",
    "Cost total anterior (RON)": "Previous total cost (RON)",
    # Șoferi
    "Nume": "Name",
    "CNP": "Personal ID (CNP)",
    "Nr. permis": "License number",
    "Data expirare permis": "License expiry date",
    "Stare permis": "License status",
    # Licență necesară
    "licență": "license",
    "status_licență": "license_status",
    "zile_trial_rămase": "trial_days_remaining",
    "informații": "information",
    "nr_inmatriculare": "license_plate",
}

# Valori fixe: RO → EN
_TRAD_VALORI_EN: dict[str, str] = {
    "Expirat": "Expired",
    "Valid": "Valid",
    "Vară": "Summer",
    "Iarnă": "Winter",
    "necesară": "required",
    "Licență necesară": "License required",
    "Licență expirată": "License expired",
    "Perioadă de test încheiată": "Free trial ended",
    "Introdu cheia de licență în Configurare → Licență.": "Enter the license key in Configure → License.",
    "Fără dată expirare": "No expiry date",
    "Activează licența ca să vezi senzorii vehiculului.": "Activate the license to see the vehicle sensors.",
}

# Prefixe dinamice pentru chei de tip „Anterior – X" și „Cost {an}"
_TRAD_PREFIXE_EN: dict[str, str] = {
    "Anterior – ": "Previous – ",
    "Asigurări ": "Insurance ",
    "Taxe ": "Taxes ",
    "Mentenanță ": "Maintenance ",
}

# Unități de măsură: RO → EN
_TRAD_UOM_EN: dict[str, str] = {
    "zile": "days",
    "luni": "months",
}


def _traduce_cheie(cheie: str) -> str:
    """Traduce o cheie de atribut din RO în EN."""
    # Cheie exactă
    if cheie in _TRAD_CHEI_EN:
        return _TRAD_CHEI_EN[cheie]
    # Prefixe dinamice (ex: "Anterior – Companie" → "Previous – Company")
    for prefix_ro, prefix_en in _TRAD_PREFIXE_EN.items():
        if cheie.startswith(prefix_ro):
            rest = cheie[len(prefix_ro):]
            rest_tradus = _TRAD_CHEI_EN.get(rest, rest)
            return f"{prefix_en}{rest_tradus}"
    return cheie


def _traduce_valoare(valoare: Any) -> Any:
    """Traduce o valoare fixă (string) din RO în EN."""
    if isinstance(valoare, str) and valoare in _TRAD_VALORI_EN:
        return _TRAD_VALORI_EN[valoare]
    return valoare


def _traduce_atribute(
    hass: HomeAssistant, atribute: dict[str, Any]
) -> dict[str, Any]:
    """Traduce cheile și valorile fixe ale atributelor pe baza limbii HA.

    Dacă limba UI este română, returnează atributele neschimbate.
    Pentru orice altă limbă, se aplică traducerea RO → EN.
    """
    if hass.config.language == "ro":
        return atribute
    return {
        _traduce_cheie(k): _traduce_valoare(v)
        for k, v in atribute.items()
    }


def _traduce_val(hass: HomeAssistant, text: str) -> str:
    """Traduce o valoare string individuală (native_value, etc.)."""
    if hass.config.language == "ro":
        return text
    return _TRAD_VALORI_EN.get(text, text)


def _traduce_uom(hass: HomeAssistant, uom: str | None) -> str | None:
    """Traduce unitatea de măsură."""
    if uom is None or hass.config.language == "ro":
        return uom
    return _TRAD_UOM_EN.get(uom, uom)


# ─────────────────────────────────────────────
# Descrieri senzori
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class VehiculeSensorDescription(SensorEntityDescription):
    """Descriere extinsă pentru senzorii vehiculului."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None
    attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    # Funcție de vizibilitate: returnează True dacă senzorul trebuie creat.
    # Dacă este None, senzorul este mereu vizibil.
    vizibil_fn: Callable[[dict[str, Any]], bool] | None = None


def _informatii_value(data: dict[str, Any]) -> str | None:
    """Starea senzorului de informații: Marcă Model sau nr. înmatriculare."""
    marca = data.get(CONF_MARCA, "")
    model = data.get(CONF_MODEL, "")
    text = f"{marca} {model}".strip()
    if text:
        return text
    # Fallback: returnăm nr. de înmatriculare (mereu disponibil)
    return data.get(CONF_NR_INMATRICULARE)


def _informatii_attr(data: dict[str, Any]) -> dict[str, Any]:
    """Atributele senzorului de informații."""
    atribute: dict[str, Any] = {}

    # Câmpuri text – se adaugă direct
    campuri_text = {
        "Nr. înmatriculare": CONF_NR_INMATRICULARE,
        "Serie CIV": CONF_SERIE_CIV,
        "VIN": CONF_VIN,
        "Marcă": CONF_MARCA,
        "Model": CONF_MODEL,
        "Motorizare": CONF_MOTORIZARE,
        "Combustibil": CONF_COMBUSTIBIL,
    }
    for eticheta, cheie in campuri_text.items():
        val = data.get(cheie)
        if val is not None and val != "":
            atribute[eticheta] = val

    # Câmpuri numerice – convertim float → int
    campuri_numerice = {
        "An fabricație": CONF_AN_FABRICATIE,
        "An prima înmatriculare": CONF_AN_PRIMA_INMATRICULARE,
        "Capacitate cilindrică (cm³)": CONF_CAPACITATE_CILINDRICA,
        "Putere (kW)": CONF_PUTERE_KW,
        "Putere (CP)": CONF_PUTERE_CP,
    }
    for eticheta, cheie in campuri_numerice.items():
        val = intreg(data.get(cheie))
        if val is not None:
            atribute[eticheta] = val

    return atribute


def _filtrare_atribute(perechi: dict[str, Any]) -> dict[str, Any]:
    """Filtrează atributele: elimină valorile None și stringurile goale."""
    return {k: v for k, v in perechi.items() if v is not None and v != ""}


# ─────────────────────────────────────────────
# Funcții pentru istoric (per categorie)
# ─────────────────────────────────────────────


def _cu_istoric(
    atribute: dict[str, Any], data: dict[str, Any], categorie: str
) -> dict[str, Any]:
    """Adaugă atribute de istoric la un dicționar de atribute existent.

    Afișează:
    - Reînnoiri anterioare: N
    - Ultima arhivare: DD.MM.YYYY
    - Detaliile ultimei intrări arhivate (cu prefix „Anterior – ")
    - Cost total anterior (RON) agregat (dacă > 1 intrare și > 0)
    """
    istoric = data.get(CONF_ISTORIC, [])
    if not isinstance(istoric, list):
        return atribute

    intrari = [
        i for i in istoric
        if isinstance(i, dict) and i.get("tip") == categorie
    ]
    if not intrari:
        return atribute

    # Număr total de reînnoiri
    atribute["Reînnoiri anterioare"] = len(intrari)

    # Ultima intrare arhivată — detalii
    ultima = intrari[-1]
    data_arhivare = ultima.get("data_arhivare")
    if data_arhivare:
        atribute["Ultima arhivare"] = format_data_ro(data_arhivare)

    # Câmpurile din ultima intrare, cu prefix „Anterior – "
    date_vechi = ultima.get("date", {})
    for eticheta, val in date_vechi.items():
        if val is None or val == "":
            continue
        # Încercăm conversie: dată RO > întreg > text brut
        val_afisat: Any = val
        val_data = format_data_ro(val)
        if val_data is not None:
            val_afisat = val_data
        else:
            v_int = intreg(val)
            if v_int is not None:
                val_afisat = v_int
        atribute[f"Anterior – {eticheta}"] = val_afisat

    # Cost total agregat din TOATE intrările (util dacă > 1 reînnoire)
    if len(intrari) > 1:
        total_cost = 0
        for intrare_ist in intrari:
            date_intrare = intrare_ist.get("date", {})
            for cheie_et, v in date_intrare.items():
                if "cost" in cheie_et.lower() or "preț" in cheie_et.lower():
                    vi = intreg(v)
                    if vi is not None:
                        total_cost += vi
        if total_cost > 0:
            atribute["Cost total anterior (RON)"] = total_cost

    return atribute


# ─────────────────────────────────────────────
# Funcții pentru senzorul Cost Total
# ─────────────────────────────────────────────

# ── Mapping cost → data de referință (pentru determinarea anului) ──
# Fiecare cheie de cost are o dată asociată din care extragem anul.
_COST_DATA_REFERINTA: dict[str, str] = {
    CONF_RCA_COST: CONF_RCA_DATA_EMITERE,
    CONF_CASCO_COST: CONF_CASCO_DATA_EMITERE,
    CONF_ROVINIETA_PRET: CONF_ROVINIETA_DATA_INCEPUT,
    CONF_IMPOZIT_SUMA: CONF_IMPOZIT_SCADENTA,
    CONF_REVIZIE_ULEI_COST: CONF_REVIZIE_ULEI_DATA,
    CONF_DISTRIBUTIE_COST: CONF_DISTRIBUTIE_DATA,
    CONF_ANVELOPE_COST: CONF_ANVELOPE_VARA_DATA,
    CONF_BATERIE_COST: CONF_BATERIE_DATA_SCHIMB,
    CONF_PLACUTE_FRANA_COST: CONF_PLACUTE_FRANA_DATA,
    CONF_DISCURI_FRANA_COST: CONF_DISCURI_FRANA_DATA,
}

# Costurile grupate pe categorii (pentru defalcare în atribute)
_COSTURI_ASIGURARI: dict[str, str] = {
    "RCA": CONF_RCA_COST,
    "Casco": CONF_CASCO_COST,
}
_COSTURI_TAXE: dict[str, str] = {
    "Rovinieta": CONF_ROVINIETA_PRET,
    "Impozit auto": CONF_IMPOZIT_SUMA,
}
_COSTURI_MENTENANTA: dict[str, str] = {
    "Revizie ulei": CONF_REVIZIE_ULEI_COST,
    "Distribuție": CONF_DISTRIBUTIE_COST,
    "Anvelope": CONF_ANVELOPE_COST,
    "Baterie": CONF_BATERIE_COST,
    "Plăcuțe frână": CONF_PLACUTE_FRANA_COST,
    "Discuri frână": CONF_DISCURI_FRANA_COST,
}


def _an_din_data(data_iso: Any) -> int | None:
    """Extrage anul dintr-o dată ISO. Returnează None dacă nu e validă."""
    if not data_iso or data_iso == "":
        return None
    try:
        return date.fromisoformat(str(data_iso)).year
    except (ValueError, TypeError):
        return None


def _costuri_pe_ani(data: dict[str, Any]) -> dict[int, int]:
    """Construiește un dicționar {an: total_cost} din costurile curente.

    Folosește _COST_DATA_REFERINTA pentru a determina anul fiecărui cost.
    Costurile fără dată asociată se atribuie anului curent (fallback).
    """
    costuri: dict[int, int] = {}
    an_curent = date.today().year

    for cheie_cost, cheie_data in _COST_DATA_REFERINTA.items():
        val = intreg(data.get(cheie_cost))
        if val is None or val == 0:
            continue
        an = _an_din_data(data.get(cheie_data)) or an_curent
        costuri[an] = costuri.get(an, 0) + val

    return costuri


def _costuri_istorice_pe_ani(data: dict[str, Any]) -> dict[int, int]:
    """Construiește un dicționar {an: total_cost} din intrările arhivate.

    Scanează _istoric și extrage costurile + anul din datele arhivate.
    Folosește data_arhivare ca fallback dacă nu există date calendaristice.
    """
    istoric = data.get(CONF_ISTORIC, [])
    if not isinstance(istoric, list):
        return {}

    costuri: dict[int, int] = {}

    for intrare in istoric:
        if not isinstance(intrare, dict):
            continue
        date_vechi = intrare.get("date", {})
        # Determinăm anul: căutăm prima dată validă în datele arhivate
        an_intrare: int | None = None
        for _eticheta, val in date_vechi.items():
            an_intrare = _an_din_data(val)
            if an_intrare is not None:
                break
        # Fallback: anul din data_arhivare
        if an_intrare is None:
            an_intrare = _an_din_data(intrare.get("data_arhivare"))
        if an_intrare is None:
            continue

        # Extragem costurile
        for eticheta, val in date_vechi.items():
            if "cost" in eticheta.lower() or "preț" in eticheta.lower():
                v = intreg(val)
                if v is not None and v > 0:
                    costuri[an_intrare] = costuri.get(an_intrare, 0) + v

    return costuri


def _suma_categorie_an(
    data: dict[str, Any], campuri: dict[str, str], an: int,
) -> int:
    """Calculează suma costurilor unei categorii pentru un an specific."""
    total = 0
    for _eticheta, cheie_cost in campuri.items():
        val = intreg(data.get(cheie_cost))
        if val is None or val == 0:
            continue
        cheie_data = _COST_DATA_REFERINTA.get(cheie_cost)
        an_cost = (
            _an_din_data(data.get(cheie_data)) if cheie_data else None
        ) or date.today().year
        if an_cost == an:
            total += val
    return total


def _are_costuri(data: dict[str, Any]) -> bool:
    """Verifică dacă există cel puțin un cost completat (curent sau arhivat)."""
    # Costuri curente
    for cheie_cost in _COST_DATA_REFERINTA:
        val = intreg(data.get(cheie_cost))
        if val is not None and val > 0:
            return True
    # Costuri arhivate
    istoric = data.get(CONF_ISTORIC, [])
    if isinstance(istoric, list):
        for intrare in istoric:
            if not isinstance(intrare, dict):
                continue
            for et, v in intrare.get("date", {}).items():
                if "cost" in et.lower() or "preț" in et.lower():
                    vi = intreg(v)
                    if vi is not None and vi > 0:
                        return True
    return False


def _cost_total_value(data: dict[str, Any]) -> int | None:
    """Returnează costul total al anului curent.

    Suma tuturor costurilor curente care au data de referință în anul curent.
    Returnează None dacă nu există niciun cost (senzorul nu se creează).
    Returnează 0 dacă există costuri dar niciunul nu e din anul curent.
    """
    if not _are_costuri(data):
        return None
    costuri_curente = _costuri_pe_ani(data)
    an_curent = date.today().year
    return costuri_curente.get(an_curent, 0)


def _cost_total_attr(data: dict[str, Any]) -> dict[str, Any]:
    """Atributele senzorului Cost Total: defalcare pe an și categorie.

    Afișează:
    - An curent: defalcare pe categorii (Asigurări / Taxe / Mentenanță)
    - Ani anteriori: total per an (din costuri curente + arhivate)
    """
    atribute: dict[str, Any] = {}
    an_curent = date.today().year

    # ── Defalcare an curent pe categorii ──
    s_asig = _suma_categorie_an(data, _COSTURI_ASIGURARI, an_curent)
    if s_asig > 0:
        atribute[f"Asigurări {an_curent} (RON)"] = s_asig

    s_taxe = _suma_categorie_an(data, _COSTURI_TAXE, an_curent)
    if s_taxe > 0:
        atribute[f"Taxe {an_curent} (RON)"] = s_taxe

    s_ment = _suma_categorie_an(data, _COSTURI_MENTENANTA, an_curent)
    if s_ment > 0:
        atribute[f"Mentenanță {an_curent} (RON)"] = s_ment

    # ── Costuri din ani anteriori (curente care nu sunt anul curent) ──
    costuri_curente = _costuri_pe_ani(data)

    # ── Costuri din istoric (arhivate) ──
    costuri_arhivate = _costuri_istorice_pe_ani(data)

    # Combinăm toate costurile pe ani
    toti_anii: dict[int, int] = {}
    for an, total in costuri_curente.items():
        toti_anii[an] = toti_anii.get(an, 0) + total
    for an, total in costuri_arhivate.items():
        toti_anii[an] = toti_anii.get(an, 0) + total

    # Afișăm totaluri per an (descrescător, fără anul curent – deja defalcat)
    for an in sorted(toti_anii.keys(), reverse=True):
        if an == an_curent:
            continue
        atribute[f"Total {an} (RON)"] = toti_anii[an]

    # Total general (toți anii)
    total_general = sum(toti_anii.values())
    if total_general > 0 and len(toti_anii) > 1:
        atribute["Total general (RON)"] = total_general

    return atribute


SENSOR_DESCRIPTIONS: list[VehiculeSensorDescription] = [
    # ── Informații vehicul (mereu vizibil – nr. înmatriculare există întotdeauna) ──
    VehiculeSensorDescription(
        key="informatii",
        translation_key="informatii",
        icon="mdi:car-info",
        # vizibil_fn=None → mereu vizibil
        value_fn=_informatii_value,
        attributes_fn=_informatii_attr,
    ),
    # ── Kilometraj ──
    VehiculeSensorDescription(
        key="kilometraj",
        translation_key="kilometraj",
        icon="mdi:counter",
        native_unit_of_measurement="km",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        vizibil_fn=lambda d: _are_valoare(d, CONF_KM_CURENT),
        value_fn=lambda d: intreg(d.get(CONF_KM_CURENT)),
        attributes_fn=lambda d: {},
    ),
    # ── RCA ──
    VehiculeSensorDescription(
        key="rca",
        translation_key="rca",
        icon="mdi:shield-car",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: _are_valoare(d, CONF_RCA_DATA_EXPIRARE),
        value_fn=lambda d: zile_ramase(d.get(CONF_RCA_DATA_EXPIRARE)),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Număr poliță": d.get(CONF_RCA_NUMAR_POLITA),
                    "Companie": d.get(CONF_RCA_COMPANIE),
                    "Data emitere": format_data_ro(d.get(CONF_RCA_DATA_EMITERE)),
                    "Data expirare": format_data_ro(d.get(CONF_RCA_DATA_EXPIRARE)),
                    "Cost (RON)": intreg(d.get(CONF_RCA_COST)),
                    "Stare": stare_document(d.get(CONF_RCA_DATA_EXPIRARE)),
                }
            ),
            d, "rca",
        ),
    ),
    # ── Casco ──
    VehiculeSensorDescription(
        key="casco",
        translation_key="casco",
        icon="mdi:shield-plus",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: _are_valoare(d, CONF_CASCO_DATA_EXPIRARE),
        value_fn=lambda d: zile_ramase(d.get(CONF_CASCO_DATA_EXPIRARE)),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Număr poliță": d.get(CONF_CASCO_NUMAR_POLITA),
                    "Companie": d.get(CONF_CASCO_COMPANIE),
                    "Data emitere": format_data_ro(d.get(CONF_CASCO_DATA_EMITERE)),
                    "Data expirare": format_data_ro(d.get(CONF_CASCO_DATA_EXPIRARE)),
                    "Cost (RON)": intreg(d.get(CONF_CASCO_COST)),
                    "Stare": stare_document(d.get(CONF_CASCO_DATA_EXPIRARE)),
                }
            ),
            d, "casco",
        ),
    ),
    # ── ITP ──
    VehiculeSensorDescription(
        key="itp",
        translation_key="itp",
        icon="mdi:car-wrench",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: _are_valoare(d, CONF_ITP_DATA_EXPIRARE),
        value_fn=lambda d: zile_ramase(d.get(CONF_ITP_DATA_EXPIRARE)),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Data expirare": format_data_ro(d.get(CONF_ITP_DATA_EXPIRARE)),
                    "Stație": d.get(CONF_ITP_STATIE),
                    "Kilometraj la ITP": intreg(d.get(CONF_ITP_KILOMETRAJ)),
                    "Stare": stare_document(d.get(CONF_ITP_DATA_EXPIRARE)),
                }
            ),
            d, "itp",
        ),
    ),
    # ── Rovinieta ──
    VehiculeSensorDescription(
        key="rovinieta",
        translation_key="rovinieta",
        icon="mdi:road-variant",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: _are_valoare(d, CONF_ROVINIETA_DATA_SFARSIT),
        value_fn=lambda d: zile_ramase(d.get(CONF_ROVINIETA_DATA_SFARSIT)),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Data început": format_data_ro(d.get(CONF_ROVINIETA_DATA_INCEPUT)),
                    "Data sfârșit": format_data_ro(d.get(CONF_ROVINIETA_DATA_SFARSIT)),
                    "Categorie": d.get(CONF_ROVINIETA_CATEGORIE),
                    "Preț (RON)": intreg(d.get(CONF_ROVINIETA_PRET)),
                    "Stare": stare_document(d.get(CONF_ROVINIETA_DATA_SFARSIT)),
                }
            ),
            d, "rovinieta",
        ),
    ),
    # ── Impozit ──
    VehiculeSensorDescription(
        key="impozit",
        translation_key="impozit",
        icon="mdi:cash",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: _are_valoare(d, CONF_IMPOZIT_SCADENTA),
        value_fn=lambda d: zile_ramase(d.get(CONF_IMPOZIT_SCADENTA)),
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Sumă (RON)": intreg(d.get(CONF_IMPOZIT_SUMA)),
                "Scadență": format_data_ro(d.get(CONF_IMPOZIT_SCADENTA)),
                "Localitate": d.get(CONF_IMPOZIT_LOCALITATE),
                "Proprietar": d.get(CONF_PROPRIETAR),
                "Tip proprietate": d.get(CONF_TIP_PROPRIETATE),
            }
        ),
    ),
    # ── Leasing (apare DOAR dacă tip_proprietate = leasing) ──
    VehiculeSensorDescription(
        key="leasing",
        translation_key="leasing",
        icon="mdi:file-document-outline",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: d.get(CONF_TIP_PROPRIETATE) == "leasing",
        value_fn=lambda d: zile_ramase(d.get(CONF_LEASING_DATA_EXPIRARE)),
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Data expirare": format_data_ro(d.get(CONF_LEASING_DATA_EXPIRARE)),
                "Tip proprietate": d.get(CONF_TIP_PROPRIETATE),
                "Stare": stare_document(d.get(CONF_LEASING_DATA_EXPIRARE)),
            }
        ),
    ),
    # ── Revizie ulei ──
    VehiculeSensorDescription(
        key="revizie_ulei",
        translation_key="revizie_ulei",
        icon="mdi:oil",
        native_unit_of_measurement="km",
        vizibil_fn=lambda d: _are_valoare(d, CONF_REVIZIE_ULEI_KM_URMATOR),
        value_fn=lambda d: km_ramasi(
            d.get(CONF_KM_CURENT), d.get(CONF_REVIZIE_ULEI_KM_URMATOR)
        ),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Km ultima revizie": intreg(d.get(CONF_REVIZIE_ULEI_KM_ULTIMUL)),
                    "Km următoarea revizie": intreg(d.get(CONF_REVIZIE_ULEI_KM_URMATOR)),
                    "Data ultima revizie": format_data_ro(d.get(CONF_REVIZIE_ULEI_DATA)),
                    "Cost (RON)": intreg(d.get(CONF_REVIZIE_ULEI_COST)),
                    "Km curent": intreg(d.get(CONF_KM_CURENT)),
                }
            ),
            d, "revizie_ulei",
        ),
    ),
    # ── Distribuție ──
    VehiculeSensorDescription(
        key="distributie",
        translation_key="distributie",
        icon="mdi:engine",
        native_unit_of_measurement="km",
        vizibil_fn=lambda d: _are_valoare(d, CONF_DISTRIBUTIE_KM_URMATOR),
        value_fn=lambda d: km_ramasi(
            d.get(CONF_KM_CURENT), d.get(CONF_DISTRIBUTIE_KM_URMATOR)
        ),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Km ultima schimbare": intreg(d.get(CONF_DISTRIBUTIE_KM_ULTIMUL)),
                    "Km următoarea schimbare": intreg(d.get(CONF_DISTRIBUTIE_KM_URMATOR)),
                    "Data ultima schimbare": format_data_ro(d.get(CONF_DISTRIBUTIE_DATA)),
                    "Cost (RON)": intreg(d.get(CONF_DISTRIBUTIE_COST)),
                    "Km curent": intreg(d.get(CONF_KM_CURENT)),
                }
            ),
            d, "distributie",
        ),
    ),
    # ── Anvelope ──
    VehiculeSensorDescription(
        key="anvelope",
        translation_key="anvelope",
        icon="mdi:tire",
        vizibil_fn=lambda d: _are_valoare(
            d, CONF_ANVELOPE_VARA_DATA, CONF_ANVELOPE_IARNA_DATA
        ),
        value_fn=lambda d: sezon_anvelope(
            d.get(CONF_ANVELOPE_VARA_DATA), d.get(CONF_ANVELOPE_IARNA_DATA)
        ),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Data montare vară": format_data_ro(d.get(CONF_ANVELOPE_VARA_DATA)),
                    "Data montare iarnă": format_data_ro(d.get(CONF_ANVELOPE_IARNA_DATA)),
                    "Cost (RON)": intreg(d.get(CONF_ANVELOPE_COST)),
                    "Sezon recomandat": (
                        "Iarnă"
                        if date.today().month in (11, 12, 1, 2, 3)
                        else "Vară"
                    ),
                }
            ),
            d, "anvelope",
        ),
    ),
    # ── Baterie ──
    VehiculeSensorDescription(
        key="baterie",
        translation_key="baterie",
        icon="mdi:car-battery",
        native_unit_of_measurement="luni",
        vizibil_fn=lambda d: _are_valoare(d, CONF_BATERIE_DATA_SCHIMB),
        value_fn=lambda d: luni_de_la(d.get(CONF_BATERIE_DATA_SCHIMB)),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Data schimb": format_data_ro(d.get(CONF_BATERIE_DATA_SCHIMB)),
                    "Cost (RON)": intreg(d.get(CONF_BATERIE_COST)),
                }
            ),
            d, "baterie",
        ),
    ),
    # ── Plăcuțe frână ──
    VehiculeSensorDescription(
        key="placute_frana",
        translation_key="placute_frana",
        icon="mdi:car-brake-alert",
        native_unit_of_measurement="km",
        vizibil_fn=lambda d: _are_valoare(d, CONF_PLACUTE_FRANA_KM_URMATOR),
        value_fn=lambda d: km_ramasi(
            d.get(CONF_KM_CURENT), d.get(CONF_PLACUTE_FRANA_KM_URMATOR)
        ),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Km ultima schimbare": intreg(d.get(CONF_PLACUTE_FRANA_KM_ULTIMUL)),
                    "Km următoarea schimbare": intreg(d.get(CONF_PLACUTE_FRANA_KM_URMATOR)),
                    "Data schimbare": format_data_ro(d.get(CONF_PLACUTE_FRANA_DATA)),
                    "Cost (RON)": intreg(d.get(CONF_PLACUTE_FRANA_COST)),
                    "Km curent": intreg(d.get(CONF_KM_CURENT)),
                }
            ),
            d, "frane",
        ),
    ),
    # ── Discuri frână ──
    VehiculeSensorDescription(
        key="discuri_frana",
        translation_key="discuri_frana",
        icon="mdi:disc",
        native_unit_of_measurement="km",
        vizibil_fn=lambda d: _are_valoare(d, CONF_DISCURI_FRANA_KM_URMATOR),
        value_fn=lambda d: km_ramasi(
            d.get(CONF_KM_CURENT), d.get(CONF_DISCURI_FRANA_KM_URMATOR)
        ),
        attributes_fn=lambda d: _cu_istoric(
            _filtrare_atribute(
                {
                    "Km ultima schimbare": intreg(d.get(CONF_DISCURI_FRANA_KM_ULTIMUL)),
                    "Km următoarea schimbare": intreg(d.get(CONF_DISCURI_FRANA_KM_URMATOR)),
                    "Data schimbare": format_data_ro(d.get(CONF_DISCURI_FRANA_DATA)),
                    "Cost (RON)": intreg(d.get(CONF_DISCURI_FRANA_COST)),
                    "Km curent": intreg(d.get(CONF_KM_CURENT)),
                }
            ),
            d, "frane",
        ),
    ),
    # ── Trusă de prim ajutor (obligatorie în România) ──
    VehiculeSensorDescription(
        key="trusa_prim_ajutor",
        translation_key="trusa_prim_ajutor",
        icon="mdi:medical-bag",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: _are_valoare(d, CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE),
        value_fn=lambda d: zile_ramase(d.get(CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE)),
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Data expirare": format_data_ro(d.get(CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE)),
                "Stare": stare_document(d.get(CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE)),
            }
        ),
    ),
    # ── Extinctor (obligatoriu în România) ──
    VehiculeSensorDescription(
        key="extinctor",
        translation_key="extinctor",
        icon="mdi:fire-extinguisher",
        native_unit_of_measurement="zile",
        vizibil_fn=lambda d: _are_valoare(d, CONF_EXTINCTOR_DATA_EXPIRARE),
        value_fn=lambda d: zile_ramase(d.get(CONF_EXTINCTOR_DATA_EXPIRARE)),
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Data expirare": format_data_ro(d.get(CONF_EXTINCTOR_DATA_EXPIRARE)),
                "Stare": stare_document(d.get(CONF_EXTINCTOR_DATA_EXPIRARE)),
            }
        ),
    ),
    # ── Cost Total ──
    VehiculeSensorDescription(
        key="cost_total",
        translation_key="cost_total",
        icon="mdi:cash-multiple",
        native_unit_of_measurement="RON",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        vizibil_fn=lambda d: _are_costuri(d),
        value_fn=_cost_total_value,
        attributes_fn=_cost_total_attr,
    ),
]


# ─────────────────────────────────────────────
# Configurare platformă
# ─────────────────────────────────────────────


def _senzor_vizibil(desc: VehiculeSensorDescription, date_vehicul: dict[str, Any]) -> bool:
    """Verifică dacă un senzor trebuie creat pe baza datelor disponibile.

    Senzorii fără vizibil_fn sunt mereu vizibili (ex: Informații).
    Ceilalți apar doar când au date completate.
    """
    if desc.vizibil_fn is None:
        return True
    return desc.vizibil_fn(date_vehicul)


def _is_license_valid(hass: HomeAssistant) -> bool:
    """Verifică dacă licența este validă (real-time)."""
    mgr = hass.data.get(DOMAIN, {}).get(LICENSE_DATA_KEY)
    if mgr is None:
        return False
    return mgr.is_valid


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurează senzorii pentru un vehicul."""
    nr_inmatriculare = entry.data[CONF_NR_INMATRICULARE]
    numar_normalizat = normalizeaza_numar(nr_inmatriculare)

    _LOGGER.debug("Creez senzorii pentru vehiculul: %s", nr_inmatriculare)

    license_valid = _is_license_valid(hass)
    licenta_uid = f"vehicule_licenta_{numar_normalizat}"

    # ── Licență invalidă → doar LicentaNecesaraSensor ──
    if not license_valid:
        _LOGGER.info(
            "Licență invalidă: se creează doar LicentaNecesaraSensor (%s).",
            nr_inmatriculare,
        )
        # Curăță senzorii normali orfani din Entity Registry
        registru = er.async_get(hass)
        for entry_reg in er.async_entries_for_config_entry(
            registru, entry.entry_id
        ):
            if (
                entry_reg.domain == "sensor"
                and entry_reg.unique_id != licenta_uid
            ):
                registru.async_remove(entry_reg.entity_id)
                _LOGGER.debug(
                    "[Vehicule] Senzor orfan eliminat (licență expirată): %s",
                    entry_reg.entity_id,
                )
        async_add_entities(
            [LicentaNecesaraSensor(entry, nr_inmatriculare, numar_normalizat)],
            update_before_add=True,
        )
        return

    # ── Licență validă → curăță LicentaNecesaraSensor orfan ──
    registru = er.async_get(hass)
    entitate_licenta = registru.async_get_entity_id(
        "sensor", DOMAIN, licenta_uid
    )
    if entitate_licenta is not None:
        registru.async_remove(entitate_licenta)
        _LOGGER.debug(
            "[Vehicule] Entitate LicentaNecesaraSensor orfană eliminată: %s",
            entitate_licenta,
        )

    # Combinăm data + options într-un singur dicționar
    date_vehicul: dict[str, Any] = {**entry.data, **entry.options}

    # Determinăm care senzori sunt activi și care nu
    chei_active: set[str] = set()
    chei_inactive: set[str] = set()
    for desc in SENSOR_DESCRIPTIONS:
        if _senzor_vizibil(desc, date_vehicul):
            chei_active.add(desc.key)
        else:
            chei_inactive.add(desc.key)

    # Curățăm entitățile orfane din Entity Registry
    # (ex: senzorul Leasing când se trece de la leasing la proprietate,
    #  sau orice senzor ale cărui date au fost golite)
    if chei_inactive:
        _curata_entitati_orfane(hass, entry, numar_normalizat, chei_inactive)

    entitati = [
        VehiculeSensor(
            entry=entry,
            description=desc,
            nr_inmatriculare=nr_inmatriculare,
            numar_normalizat=numar_normalizat,
            date_vehicul=date_vehicul,
        )
        for desc in SENSOR_DESCRIPTIONS
        if desc.key in chei_active
    ]

    # ── Senzori pentru șoferi ──
    soferi: list[dict[str, Any]] = date_vehicul.get(CONF_SOFERI, [])
    for i, sofer in enumerate(soferi):
        if sofer.get(CONF_SOFER_NUME):
            entitati.append(
                SoferSensor(
                    entry=entry,
                    nr_inmatriculare=nr_inmatriculare,
                    numar_normalizat=numar_normalizat,
                    sofer=sofer,
                    index=i,
                )
            )

    # Curățăm senzorii de șoferi orfani (șoferi eliminați)
    _curata_soferi_orfani(hass, entry, numar_normalizat, soferi)

    _LOGGER.debug(
        "Vehicul %s: %d senzori creați (din %d posibili) + %d șoferi",
        nr_inmatriculare,
        len(entitati) - len([s for s in soferi if s.get(CONF_SOFER_NUME)]),
        len(SENSOR_DESCRIPTIONS),
        len([s for s in soferi if s.get(CONF_SOFER_NUME)]),
    )

    async_add_entities(entitati, update_before_add=True)


def _curata_entitati_orfane(
    hass: HomeAssistant,
    entry: ConfigEntry,
    numar_normalizat: str,
    chei_inactive: set[str],
) -> None:
    """Elimină din Entity Registry entitățile care nu mai sunt necesare.

    Aceasta rezolvă problema „entitate nu mai este furnizată de integrare"
    când se schimbă condițiile de vizibilitate ale unui senzor.
    """
    registru = er.async_get(hass)

    for cheie in chei_inactive:
        unique_id = f"vehicule_{numar_normalizat}_{cheie}"

        entitate = registru.async_get_entity_id("sensor", DOMAIN, unique_id)
        if entitate is not None:
            _LOGGER.debug(
                "Elimin entitatea orfană: %s (unique_id: %s)",
                entitate,
                unique_id,
            )
            registru.async_remove(entitate)


def _curata_soferi_orfani(
    hass: HomeAssistant,
    entry: ConfigEntry,
    numar_normalizat: str,
    soferi: list[dict[str, Any]],
) -> None:
    """Elimină din Entity Registry senzorii de șoferi care nu mai există.

    Generează slug-urile active din lista curentă de șoferi și elimină
    orice entitate `vehicule_{numar}_sofer_*` care nu se regăsește.
    """
    registru = er.async_get(hass)

    # Construim setul de unique_id-uri valide
    sluguri_active: set[str] = set()
    for i, sofer in enumerate(soferi):
        nume = sofer.get(CONF_SOFER_NUME, "")
        if not nume:
            continue
        slug = re.sub(r"[^a-z0-9]", "_", nume.lower()).strip("_") or f"sofer_{i}"
        sluguri_active.add(f"vehicule_{numar_normalizat}_sofer_{slug}")

    prefix = f"vehicule_{numar_normalizat}_sofer_"
    for entitate in er.async_entries_for_config_entry(registru, entry.entry_id):
        if entitate.unique_id and entitate.unique_id.startswith(prefix):
            if entitate.unique_id not in sluguri_active:
                _LOGGER.debug(
                    "Elimin senzor șofer orfan: %s (unique_id: %s)",
                    entitate.entity_id,
                    entitate.unique_id,
                )
                registru.async_remove(entitate.entity_id)


# ─────────────────────────────────────────────
# Entitate senzor
# ─────────────────────────────────────────────


class VehiculeSensor(SensorEntity):
    """Senzor pentru un aspect al vehiculului."""

    entity_description: VehiculeSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        description: VehiculeSensorDescription,
        nr_inmatriculare: str,
        numar_normalizat: str,
        date_vehicul: dict[str, Any],
    ) -> None:
        """Inițializează senzorul."""
        self.entity_description = description
        self._entry = entry
        self._nr_inmatriculare = nr_inmatriculare
        self._numar_normalizat = numar_normalizat
        self._date_vehicul = date_vehicul

        # ID unic: vehicule_{numar_normalizat}_{tip_senzor}
        self._attr_unique_id = f"vehicule_{numar_normalizat}_{description.key}"

        # Forțăm entity_id cu prefix "vehicule_" indiferent de numele
        # dispozitivului (previne pierderea prefixului dacă userul
        # redenumește device-ul din UI-ul Home Assistant)
        self.entity_id = (
            f"sensor.vehicule_{numar_normalizat}_{description.key}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Informații despre dispozitiv (vehiculul)."""
        marca = self._date_vehicul.get(CONF_MARCA, "")
        model = self._date_vehicul.get(CONF_MODEL, "")
        return DeviceInfo(
            identifiers={(DOMAIN, self._numar_normalizat)},
            name=f"Vehicule {self._nr_inmatriculare}",
            manufacturer=marca or None,
            model=model or None,
            entry_type=None,
        )

    @property
    def _license_valid(self) -> bool:
        """Verificare real-time a licenței (nu boolean static)."""
        mgr = self.hass.data.get(DOMAIN, {}).get(LICENSE_DATA_KEY)
        if mgr is None:
            return False
        return mgr.is_valid

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Unitatea de măsură, tradusă pe baza limbii HA."""
        uom = self.entity_description.native_unit_of_measurement
        return _traduce_uom(self.hass, uom)

    @property
    def native_value(self) -> Any:
        """Returnează starea senzorului."""
        if not self._license_valid:
            return None
        if self.entity_description.value_fn is None:
            return None
        val = self.entity_description.value_fn(self._date_vehicul)
        if isinstance(val, str):
            return _traduce_val(self.hass, val)
        return val

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Returnează atributele suplimentare ale senzorului, traduse."""
        if not self._license_valid:
            return {}
        if self.entity_description.attributes_fn is None:
            return {}
        return _traduce_atribute(
            self.hass, self.entity_description.attributes_fn(self._date_vehicul)
        )


class LicentaNecesaraSensor(SensorEntity):
    """Senzor afișat DOAR când licența nu este validă.

    Oferă informații de diagnostic utile: status curent, zile trial
    rămase (dacă există), și instrucțiuni de activare.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        nr_inmatriculare: str,
        numar_normalizat: str,
    ) -> None:
        self._entry = entry
        self._nr_inmatriculare = nr_inmatriculare
        self._numar_normalizat = numar_normalizat
        self._attr_unique_id = f"vehicule_licenta_{numar_normalizat}"
        self._attr_name = "Licență necesară"
        self._attr_icon = "mdi:license"
        self.entity_id = f"sensor.vehicule_licenta_{numar_normalizat}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._numar_normalizat)},
            name=f"Vehicule {self._nr_inmatriculare}",
            entry_type=None,
        )

    @property
    def native_value(self) -> str:
        mgr = self.hass.data.get(DOMAIN, {}).get(LICENSE_DATA_KEY)
        if mgr is not None:
            status = mgr.status
            if status == "expired":
                return _traduce_val(
                    self.hass, "Licență expirată" if mgr.has_license else "Perioadă de test încheiată"
                )
        return _traduce_val(self.hass, "Licență necesară")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            "nr_inmatriculare": self._nr_inmatriculare,
        }
        mgr = self.hass.data.get(DOMAIN, {}).get(LICENSE_DATA_KEY)
        if mgr is not None:
            attrs["status_licență"] = mgr.status
            if mgr.status == "trial":
                attrs["zile_trial_rămase"] = mgr.trial_days_remaining
            attrs["informații"] = "Introdu cheia de licență în Configurare → Licență."
        else:
            attrs["informații"] = (
                "Managerul de licențe nu este disponibil."
            )
        return _traduce_atribute(self.hass, attrs)


class SoferSensor(SensorEntity):
    """Senzor dedicat pentru un șofer asociat vehiculului.

    Afișează zilele rămase până la expirarea permisului.
    Atribute: nume, CNP (mascat), nr. permis, categorie, data expirare, stare.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        nr_inmatriculare: str,
        numar_normalizat: str,
        sofer: dict[str, Any],
        index: int,
    ) -> None:
        self._entry = entry
        self._nr_inmatriculare = nr_inmatriculare
        self._numar_normalizat = numar_normalizat
        self._sofer = sofer
        self._index = index

        # Generăm un slug stabil din numele șoferului
        slug = re.sub(r"[^a-z0-9]", "_", sofer.get(CONF_SOFER_NUME, "").lower()).strip("_") or f"sofer_{index}"
        self._attr_unique_id = f"vehicule_{numar_normalizat}_sofer_{slug}"
        self._attr_name = f"Șofer — {sofer.get(CONF_SOFER_NUME, 'Necunoscut')}"
        self._attr_icon = "mdi:card-account-details"
        self.entity_id = f"sensor.vehicule_{numar_normalizat}_sofer_{slug}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._numar_normalizat)},
            name=f"Vehicule {self._nr_inmatriculare}",
            entry_type=None,
        )

    @property
    def _license_valid(self) -> bool:
        mgr = self.hass.data.get(DOMAIN, {}).get(LICENSE_DATA_KEY)
        if mgr is None:
            return False
        return mgr.is_valid

    @property
    def native_value(self) -> Any:
        if not self._license_valid:
            return None
        data_exp = self._sofer.get(CONF_SOFER_DATA_EXPIRARE_PERMIS)
        if not data_exp:
            return _traduce_val(self.hass, "Fără dată expirare")
        zile = zile_ramase(data_exp)
        if zile is None:
            return _traduce_val(self.hass, "Fără dată expirare")
        return zile

    @property
    def native_unit_of_measurement(self) -> str | None:
        if not self._license_valid:
            return None
        data_exp = self._sofer.get(CONF_SOFER_DATA_EXPIRARE_PERMIS)
        if data_exp and zile_ramase(data_exp) is not None:
            return _traduce_uom(self.hass, "zile")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self._license_valid:
            return {}

        s = self._sofer
        cnp = s.get(CONF_SOFER_CNP, "")
        cnp_mascat = f"{cnp[:1]}{'*' * (len(cnp) - 2)}{cnp[-1:]}" if len(cnp) > 2 else cnp

        attrs: dict[str, Any] = {}
        if s.get(CONF_SOFER_NUME):
            attrs["Nume"] = s[CONF_SOFER_NUME]
        if cnp:
            attrs["CNP"] = cnp_mascat
        if s.get(CONF_SOFER_NR_PERMIS):
            attrs["Nr. permis"] = s[CONF_SOFER_NR_PERMIS]
        if s.get(CONF_SOFER_CATEGORIE_PERMIS):
            attrs["Categorie"] = s[CONF_SOFER_CATEGORIE_PERMIS]
        data_exp = s.get(CONF_SOFER_DATA_EXPIRARE_PERMIS)
        if data_exp:
            attrs["Data expirare permis"] = format_data_ro(data_exp)
            attrs["Stare permis"] = stare_document(data_exp)

        return _traduce_atribute(self.hass, attrs)
