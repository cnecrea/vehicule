"""
Platforma de senzori pentru integrarea Vehicule.

Senzorii sunt CONDIȚIONAȚI – apar DOAR când au date completate.
La prima configurare (doar nr. de înmatriculare), apare doar senzorul Informații.
Pe măsură ce utilizatorul completează date, apar senzorii corespunzători.

Senzori posibili per vehicul:
- Informații generale (marcă, model, etc.) – mereu vizibil
- Kilometraj curent – vizibil când km_curent este setat
- RCA (zile rămase) – vizibil când rca_data_expirare este setat
- ITP (zile rămase) – vizibil când itp_data_expirare este setat
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
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
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
    CONF_ANVELOPE_IARNA_DATA,
    CONF_ANVELOPE_VARA_DATA,
    CONF_BATERIE_DATA_SCHIMB,
    CONF_CAPACITATE_CILINDRICA,
    CONF_COMBUSTIBIL,
    CONF_DISCURI_FRANA_KM_ULTIMUL,
    CONF_DISCURI_FRANA_KM_URMATOR,
    CONF_DISTRIBUTIE_DATA,
    CONF_DISTRIBUTIE_KM_ULTIMUL,
    CONF_DISTRIBUTIE_KM_URMATOR,
    CONF_IMPOZIT_LOCALITATE,
    CONF_IMPOZIT_SCADENTA,
    CONF_IMPOZIT_SUMA,
    CONF_ITP_DATA_EXPIRARE,
    CONF_ITP_KILOMETRAJ,
    CONF_ITP_STATIE,
    CONF_KM_CURENT,
    CONF_LEASING_DATA_EXPIRARE,
    CONF_MARCA,
    CONF_MODEL,
    CONF_MOTORIZARE,
    CONF_NR_INMATRICULARE,
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
    CONF_REVIZIE_ULEI_DATA,
    CONF_REVIZIE_ULEI_KM_ULTIMUL,
    CONF_REVIZIE_ULEI_KM_URMATOR,
    CONF_SERIE_CIV,
    CONF_TIP_PROPRIETATE,
    CONF_EXTINCTOR_DATA_EXPIRARE,
    CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE,
    CONF_VIN,
    DOMAIN,
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Număr poliță": d.get(CONF_RCA_NUMAR_POLITA),
                "Companie": d.get(CONF_RCA_COMPANIE),
                "Data emitere": format_data_ro(d.get(CONF_RCA_DATA_EMITERE)),
                "Data expirare": format_data_ro(d.get(CONF_RCA_DATA_EXPIRARE)),
                "Cost (RON)": intreg(d.get(CONF_RCA_COST)),
                "Stare": stare_document(d.get(CONF_RCA_DATA_EXPIRARE)),
            }
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Data expirare": format_data_ro(d.get(CONF_ITP_DATA_EXPIRARE)),
                "Stație": d.get(CONF_ITP_STATIE),
                "Kilometraj la ITP": intreg(d.get(CONF_ITP_KILOMETRAJ)),
                "Stare": stare_document(d.get(CONF_ITP_DATA_EXPIRARE)),
            }
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Km ultima revizie": intreg(d.get(CONF_REVIZIE_ULEI_KM_ULTIMUL)),
                "Km următoarea revizie": intreg(d.get(CONF_REVIZIE_ULEI_KM_URMATOR)),
                "Data ultima revizie": format_data_ro(d.get(CONF_REVIZIE_ULEI_DATA)),
                "Km curent": intreg(d.get(CONF_KM_CURENT)),
            }
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Km ultima schimbare": intreg(d.get(CONF_DISTRIBUTIE_KM_ULTIMUL)),
                "Km următoarea schimbare": intreg(d.get(CONF_DISTRIBUTIE_KM_URMATOR)),
                "Data ultima schimbare": format_data_ro(d.get(CONF_DISTRIBUTIE_DATA)),
                "Km curent": intreg(d.get(CONF_KM_CURENT)),
            }
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Data montare vară": format_data_ro(d.get(CONF_ANVELOPE_VARA_DATA)),
                "Data montare iarnă": format_data_ro(d.get(CONF_ANVELOPE_IARNA_DATA)),
                "Sezon recomandat": (
                    "Iarnă"
                    if date.today().month in (11, 12, 1, 2, 3)
                    else "Vară"
                ),
            }
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Data schimb": format_data_ro(d.get(CONF_BATERIE_DATA_SCHIMB)),
            }
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Km ultima schimbare": intreg(d.get(CONF_PLACUTE_FRANA_KM_ULTIMUL)),
                "Km următoarea schimbare": intreg(d.get(CONF_PLACUTE_FRANA_KM_URMATOR)),
                "Km curent": intreg(d.get(CONF_KM_CURENT)),
            }
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
        attributes_fn=lambda d: _filtrare_atribute(
            {
                "Km ultima schimbare": intreg(d.get(CONF_DISCURI_FRANA_KM_ULTIMUL)),
                "Km următoarea schimbare": intreg(d.get(CONF_DISCURI_FRANA_KM_URMATOR)),
                "Km curent": intreg(d.get(CONF_KM_CURENT)),
            }
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurează senzorii pentru un vehicul."""
    nr_inmatriculare = entry.data[CONF_NR_INMATRICULARE]
    numar_normalizat = normalizeaza_numar(nr_inmatriculare)

    _LOGGER.debug("Creez senzorii pentru vehiculul: %s", nr_inmatriculare)

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

    _LOGGER.debug(
        "Vehicul %s: %d senzori creați (din %d posibili)",
        nr_inmatriculare,
        len(entitati),
        len(SENSOR_DESCRIPTIONS),
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

    @property
    def device_info(self) -> DeviceInfo:
        """Informații despre dispozitiv (vehiculul)."""
        marca = self._date_vehicul.get(CONF_MARCA, "")
        model = self._date_vehicul.get(CONF_MODEL, "")
        #an = intreg(self._date_vehicul.get(CONF_AN_FABRICATIE))

        return DeviceInfo(
            identifiers={(DOMAIN, self._numar_normalizat)},
            name=f"Vehicule {self._nr_inmatriculare}",
            manufacturer=marca or None,
            model=model or None,
            entry_type=None,
        )

    @property
    def native_value(self) -> Any:
        """Returnează starea senzorului."""
        if self.entity_description.value_fn is None:
            return None
        return self.entity_description.value_fn(self._date_vehicul)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Returnează atributele suplimentare ale senzorului."""
        if self.entity_description.attributes_fn is None:
            return {}
        return self.entity_description.attributes_fn(self._date_vehicul)
