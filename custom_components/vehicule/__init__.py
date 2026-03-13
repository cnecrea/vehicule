"""
Integrarea Vehicule pentru Home Assistant.

Gestionarea vehiculelor, documentelor și notificărilor pentru expirări.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    BACKUP_VERSION,
    CONF_KM_CURENT,
    CONF_NR_INMATRICULARE,
    DOMAIN,
    PLATFORMS,
    SERVICE_ACTUALIZEAZA_DATE,
    SERVICE_EXPORTA_DATE,
    SERVICE_IMPORTA_DATE,
    normalizeaza_numar,
)

_LOGGER = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Scheme pentru servicii
# ─────────────────────────────────────────────

SCHEMA_ACTUALIZEAZA_DATE = vol.Schema(
    {
        vol.Required(CONF_NR_INMATRICULARE): cv.string,
        vol.Required(CONF_KM_CURENT): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=9_999_999)
        ),
    }
)

SCHEMA_EXPORTA_DATE = vol.Schema(
    {
        vol.Required(CONF_NR_INMATRICULARE): cv.string,
    }
)

SCHEMA_IMPORTA_DATE = vol.Schema(
    {
        vol.Required("cale_fisier"): cv.string,
    }
)


# ─────────────────────────────────────────────
# Setup / Unload
# ─────────────────────────────────────────────


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurează o intrare pentru un vehicul."""
    _LOGGER.debug(
        "Configurez vehiculul: %s", entry.data.get(CONF_NR_INMATRICULARE)
    )

    # Stocăm referința la intrare în hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry

    # Înregistrăm listener-ul pentru actualizarea opțiunilor
    entry.async_on_unload(entry.add_update_listener(_async_actualizare_optiuni))

    # Configurăm platformele (senzori)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Înregistrăm serviciile (doar o dată, la primul vehicul)
    await _async_inregistreaza_servicii(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descarcă o intrare (vehicul șters)."""
    _LOGGER.debug(
        "Descarc vehiculul: %s", entry.data.get(CONF_NR_INMATRICULARE)
    )

    # Descărcăm platformele
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        # Dacă nu mai există vehicule, eliminăm serviciile
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
            hass.services.async_remove(DOMAIN, SERVICE_ACTUALIZEAZA_DATE)
            hass.services.async_remove(DOMAIN, SERVICE_EXPORTA_DATE)
            hass.services.async_remove(DOMAIN, SERVICE_IMPORTA_DATE)

    return unload_ok


async def _async_actualizare_optiuni(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Reîncarcă intrarea când opțiunile se schimbă."""
    _LOGGER.debug(
        "Opțiuni actualizate pentru %s – reîncarc",
        entry.data.get(CONF_NR_INMATRICULARE),
    )
    await hass.config_entries.async_reload(entry.entry_id)


# ─────────────────────────────────────────────
# Utilitar intern: caută vehicul după nr. înmatriculare
# ─────────────────────────────────────────────


def _gaseste_vehicul(
    hass: HomeAssistant, nr_inmatriculare: str
) -> ConfigEntry | None:
    """Returnează ConfigEntry pentru vehiculul dat sau None."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_NR_INMATRICULARE) == nr_inmatriculare:
            return entry
    return None


# ─────────────────────────────────────────────
# Înregistrare servicii
# ─────────────────────────────────────────────


async def _async_inregistreaza_servicii(hass: HomeAssistant) -> None:
    """Înregistrează serviciile domeniului (o singură dată)."""
    if hass.services.has_service(DOMAIN, SERVICE_ACTUALIZEAZA_DATE):
        return

    # ── Actualizare date (kilometraj) ──

    async def _handle_actualizeaza_date(call: ServiceCall) -> None:
        """Procesează apelul de actualizare date (kilometraj)."""
        nr_inmatriculare = call.data[CONF_NR_INMATRICULARE].strip().upper()
        km_nou = call.data[CONF_KM_CURENT]

        _LOGGER.debug(
            "Actualizez datele pentru %s – km: %d",
            nr_inmatriculare,
            km_nou,
        )

        entry = _gaseste_vehicul(hass, nr_inmatriculare)

        if entry is None:
            _LOGGER.warning(
                "Nu am găsit vehiculul cu nr. %s", nr_inmatriculare
            )
            return

        optiuni_noi: dict[str, Any] = {
            **entry.options,
            CONF_KM_CURENT: km_nou,
        }
        hass.config_entries.async_update_entry(entry, options=optiuni_noi)

    # ── Export date vehicul ──

    async def _handle_exporta_date(call: ServiceCall) -> None:
        """Exportă datele unui vehicul într-un fișier JSON.

        Fișierul se salvează în directorul config al Home Assistant:
        /config/vehicule_backup_{nr_normalizat}.json
        """
        nr_inmatriculare = call.data[CONF_NR_INMATRICULARE].strip().upper()
        nr_norm = normalizeaza_numar(nr_inmatriculare)

        entry = _gaseste_vehicul(hass, nr_inmatriculare)

        if entry is None:
            _LOGGER.warning("Export: nu am găsit vehiculul %s", nr_inmatriculare)
            persistent_notification.async_create(
                hass,
                f"Nu am găsit vehiculul cu nr. {nr_inmatriculare}.",
                title="Vehicule – Export eșuat",
                notification_id=f"vehicule_export_{nr_norm}",
            )
            return

        date_export = {
            "version": BACKUP_VERSION,
            "integration": DOMAIN,
            "nr_inmatriculare": nr_inmatriculare,
            "data_export": datetime.now().isoformat(),
            "optiuni": dict(entry.options),
        }

        cale = Path(hass.config.path(f"vehicule_backup_{nr_norm}.json"))

        def _scrie() -> None:
            cale.write_text(
                json.dumps(date_export, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        await hass.async_add_executor_job(_scrie)

        _LOGGER.info("Export reușit: %s → %s", nr_inmatriculare, cale)
        persistent_notification.async_create(
            hass,
            (
                f"Datele vehiculului **{nr_inmatriculare}** au fost exportate "
                f"in:\n`{cale}`"
            ),
            title="Vehicule – Export reușit",
            notification_id=f"vehicule_export_{nr_norm}",
        )

    # ── Import date vehicul ──

    async def _handle_importa_date(call: ServiceCall) -> None:
        """Importă datele unui vehicul dintr-un fișier JSON.

        Dacă vehiculul există deja, opțiunile sunt actualizate.
        Dacă vehiculul NU există, se creează automat o intrare nouă.
        """
        cale = call.data["cale_fisier"]

        # Citire fișier (I/O blocant → executor)
        def _citeste() -> dict:
            return json.loads(Path(cale).read_text(encoding="utf-8"))

        try:
            date_import = await hass.async_add_executor_job(_citeste)
        except FileNotFoundError:
            _notifica_eroare_import(hass, f"Fișierul nu a fost găsit: {cale}")
            return
        except (json.JSONDecodeError, OSError) as err:
            _notifica_eroare_import(
                hass, f"Eroare la citirea fișierului: {err}"
            )
            return

        # Validare structură
        if (
            not isinstance(date_import, dict)
            or CONF_NR_INMATRICULARE not in date_import
            or "optiuni" not in date_import
            or not isinstance(date_import["optiuni"], dict)
        ):
            _notifica_eroare_import(
                hass,
                "Structura JSON este invalida. Fisierul trebuie sa contina "
                "campurile 'nr_inmatriculare' si 'optiuni'.",
            )
            return

        nr = date_import[CONF_NR_INMATRICULARE].strip().upper()
        optiuni = date_import["optiuni"]
        nr_norm = normalizeaza_numar(nr)

        # Căutăm vehiculul existent
        entry = _gaseste_vehicul(hass, nr)

        if entry is None:
            # Creăm vehiculul prin import flow
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data={CONF_NR_INMATRICULARE: nr},
            )
            if result.get("type") == "create_entry":
                entry = result["result"]
            else:
                motiv = result.get("reason", "necunoscut")
                _notifica_eroare_import(
                    hass,
                    f"Nu am putut crea vehiculul {nr}: {motiv}",
                )
                return

        # Actualizăm opțiunile (listener-ul va reîncărca automat)
        hass.config_entries.async_update_entry(entry, options=optiuni)

        _LOGGER.info("Import reușit pentru %s din %s", nr, cale)
        persistent_notification.async_create(
            hass,
            f"Datele vehiculului **{nr}** au fost importate cu succes.",
            title="Vehicule – Import reușit",
            notification_id=f"vehicule_import_{nr_norm}",
        )

    # ── Înregistrare efectivă ──

    hass.services.async_register(
        DOMAIN,
        SERVICE_ACTUALIZEAZA_DATE,
        _handle_actualizeaza_date,
        schema=SCHEMA_ACTUALIZEAZA_DATE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPORTA_DATE,
        _handle_exporta_date,
        schema=SCHEMA_EXPORTA_DATE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_IMPORTA_DATE,
        _handle_importa_date,
        schema=SCHEMA_IMPORTA_DATE,
    )
    _LOGGER.debug("Serviciile %s au fost înregistrate", DOMAIN)


def _notifica_eroare_import(hass: HomeAssistant, mesaj: str) -> None:
    """Creează o notificare persistentă pentru erori de import."""
    _LOGGER.error("Import: %s", mesaj)
    persistent_notification.async_create(
        hass,
        mesaj,
        title="Vehicule – Import eșuat",
        notification_id="vehicule_import_eroare",
    )
