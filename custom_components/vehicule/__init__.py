"""
Integrarea Vehicule pentru Home Assistant.

Gestionarea vehiculelor, documentelor și notificărilor pentru expirări.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_KM_CURENT,
    CONF_NR_INMATRICULARE,
    DOMAIN,
    PLATFORMS,
    SERVICE_ACTUALIZEAZA_DATE,
)

_LOGGER = logging.getLogger(__name__)

# Schemă pentru serviciul de actualizare date
SCHEMA_ACTUALIZEAZA_DATE = vol.Schema(
    {
        vol.Required(CONF_NR_INMATRICULARE): cv.string,
        vol.Required(CONF_KM_CURENT): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=9_999_999)
        ),
    }
)


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


async def _async_inregistreaza_servicii(hass: HomeAssistant) -> None:
    """Înregistrează serviciile domeniului (o singură dată)."""
    if hass.services.has_service(DOMAIN, SERVICE_ACTUALIZEAZA_DATE):
        return

    async def _handle_actualizeaza_date(call: ServiceCall) -> None:
        """Procesează apelul de actualizare date (kilometraj)."""
        nr_inmatriculare = call.data[CONF_NR_INMATRICULARE].strip().upper()
        km_nou = call.data[CONF_KM_CURENT]

        _LOGGER.debug(
            "Actualizez datele pentru %s – km: %d",
            nr_inmatriculare,
            km_nou,
        )

        # Căutăm intrarea corespunzătoare
        gasit = False
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get(CONF_NR_INMATRICULARE) == nr_inmatriculare:
                optiuni_noi: dict[str, Any] = {**entry.options, CONF_KM_CURENT: km_nou}
                hass.config_entries.async_update_entry(entry, options=optiuni_noi)
                await hass.config_entries.async_reload(entry.entry_id)
                gasit = True
                break

        if not gasit:
            _LOGGER.warning(
                "Nu am găsit vehiculul cu nr. %s", nr_inmatriculare
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ACTUALIZEAZA_DATE,
        _handle_actualizeaza_date,
        schema=SCHEMA_ACTUALIZEAZA_DATE,
    )
    _LOGGER.debug("Serviciul %s.%s a fost înregistrat", DOMAIN, SERVICE_ACTUALIZEAZA_DATE)
