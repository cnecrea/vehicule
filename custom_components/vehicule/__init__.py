"""
Integrarea Vehicule pentru Home Assistant.

Gestionarea vehiculelor, documentelor și notificărilor pentru expirări.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    BACKUP_VERSION,
    CONF_KM_CURENT,
    CONF_NR_INMATRICULARE,
    DOMAIN,
    LICENSE_DATA_KEY,
    PLATFORMS,
    SERVICE_ACTUALIZEAZA_DATE,
    SERVICE_EXPORTA_DATE,
    SERVICE_IMPORTA_DATE,
    normalizeaza_numar,
)
from .helpers import aplatizeaza_optiuni, structureaza_optiuni
from .license import LicenseManager

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
        "[Vehicule] Setup entry_id=%s (%s)",
        entry.entry_id,
        entry.data.get(CONF_NR_INMATRICULARE),
    )

    hass.data.setdefault(DOMAIN, {})

    # ── Inițializare License Manager (o singură instanță per domeniu) ──
    if LICENSE_DATA_KEY not in hass.data.get(DOMAIN, {}):
        _LOGGER.debug("[Vehicule] Inițializez LicenseManager (prima entry)")
        license_mgr = LicenseManager(hass)
        await license_mgr.async_load()
        hass.data[DOMAIN][LICENSE_DATA_KEY] = license_mgr
        _LOGGER.debug(
            "[Vehicule] LicenseManager: status=%s, valid=%s, fingerprint=%s...",
            license_mgr.status,
            license_mgr.is_valid,
            license_mgr.fingerprint[:16],
        )

        # Heartbeat periodic — intervalul vine de la server (via valid_until)
        interval_sec = license_mgr.check_interval_seconds
        _LOGGER.debug(
            "[Vehicule] Programez heartbeat periodic la fiecare %d secunde (%d ore)",
            interval_sec,
            interval_sec // 3600,
        )

        async def _heartbeat_periodic(_now) -> None:
            """Verifică statusul la server dacă cache-ul a expirat."""
            mgr: LicenseManager | None = hass.data.get(DOMAIN, {}).get(
                LICENSE_DATA_KEY
            )
            if not mgr:
                _LOGGER.debug("[Vehicule] Heartbeat: LicenseManager nu există, skip")
                return
            if mgr.needs_heartbeat:
                _LOGGER.debug("[Vehicule] Heartbeat: cache expirat, verific la server")
                await mgr.async_heartbeat()
            else:
                _LOGGER.debug("[Vehicule] Heartbeat: cache valid, nu e nevoie de verificare")

        cancel_heartbeat = async_track_time_interval(
            hass,
            _heartbeat_periodic,
            timedelta(seconds=interval_sec),
        )
        hass.data[DOMAIN]["_cancel_heartbeat"] = cancel_heartbeat
        _LOGGER.debug("[Vehicule] Heartbeat programat și stocat în hass.data")

        # ── Notificare re-enable (dacă a fost dezactivată anterior) ──
        was_disabled = hass.data.pop(f"{DOMAIN}_was_disabled", False)
        if was_disabled:
            await license_mgr.async_notify_event("integration_enabled")

        if not license_mgr.is_valid:
            _LOGGER.warning(
                "[Vehicule] Integrarea nu are licență validă. "
                "Senzorii vor afișa 'Licență necesară'."
            )
        elif license_mgr.is_trial_valid:
            _LOGGER.info(
                "[Vehicule] Perioadă de evaluare — %d zile rămase",
                license_mgr.trial_days_remaining,
            )
        else:
            _LOGGER.info(
                "[Vehicule] Licență activă — tip: %s",
                license_mgr.license_type,
            )
    else:
        _LOGGER.debug(
            "[Vehicule] LicenseManager există deja (entry suplimentară)"
        )

    # Stocăm referința la intrare în hass.data
    hass.data[DOMAIN][entry.entry_id] = entry

    # Înregistrăm listener-ul pentru actualizarea opțiunilor
    entry.async_on_unload(entry.add_update_listener(_async_actualizare_optiuni))

    # Configurăm platformele (senzori)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Înregistrăm serviciile (doar o dată, la primul vehicul)
    await _async_inregistreaza_servicii(hass)

    _LOGGER.debug("[Vehicule] Setup complet pentru entry_id=%s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descarcă o intrare (vehicul șters)."""
    _LOGGER.info(
        "[Vehicule] ── async_unload_entry ── entry_id=%s (%s)",
        entry.entry_id,
        entry.data.get(CONF_NR_INMATRICULARE),
    )

    # Descărcăm platformele
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    _LOGGER.debug("[Vehicule] Unload platforme: %s", "OK" if unload_ok else "EȘUAT")

    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        _LOGGER.debug("[Vehicule] Entry %s eliminat din hass.data", entry.entry_id)

        # Verifică dacă mai sunt entry-uri active (ignoră cheile interne)
        chei_interne = {LICENSE_DATA_KEY, "_cancel_heartbeat"}
        entry_ids_ramase = {
            k for k in hass.data.get(DOMAIN, {})
            if k not in chei_interne
        }

        _LOGGER.debug(
            "[Vehicule] Entry-uri rămase după unload: %d (%s)",
            len(entry_ids_ramase),
            entry_ids_ramase or "niciuna",
        )

        if not entry_ids_ramase:
            _LOGGER.info("[Vehicule] Ultima entry descărcată — curăț domeniul complet")

            # ── Eliminăm serviciile ──
            hass.services.async_remove(DOMAIN, SERVICE_ACTUALIZEAZA_DATE)
            hass.services.async_remove(DOMAIN, SERVICE_EXPORTA_DATE)
            hass.services.async_remove(DOMAIN, SERVICE_IMPORTA_DATE)
            _LOGGER.debug("[Vehicule] Serviciile au fost eliminate")

            # ── Notificare lifecycle (înainte de cleanup!) ──
            mgr = hass.data[DOMAIN].get(LICENSE_DATA_KEY)
            if mgr and not hass.is_stopping:
                if entry.disabled_by:
                    await mgr.async_notify_event("integration_disabled")
                    # Flag pentru async_setup_entry: la re-enable, trimitem "enabled"
                    hass.data[f"{DOMAIN}_was_disabled"] = True
                else:
                    # Salvăm fingerprint-ul pentru async_remove_entry
                    hass.data.setdefault(f"{DOMAIN}_notify", {}).update({
                        "fingerprint": mgr.fingerprint,
                        "license_key": mgr._data.get("license_key", ""),
                    })
                    _LOGGER.debug(
                        "[Vehicule] Fingerprint salvat pentru async_remove_entry"
                    )

            # Oprește heartbeat-ul periodic
            cancel_hb = hass.data[DOMAIN].pop("_cancel_heartbeat", None)
            if cancel_hb:
                cancel_hb()
                _LOGGER.debug("[Vehicule] Heartbeat periodic oprit")

            # Elimină LicenseManager
            hass.data[DOMAIN].pop(LICENSE_DATA_KEY, None)
            _LOGGER.debug("[Vehicule] LicenseManager eliminat")

            # Elimină domeniul complet
            hass.data.pop(DOMAIN, None)
            _LOGGER.debug("[Vehicule] hass.data[%s] eliminat complet", DOMAIN)

            _LOGGER.info("[Vehicule] Cleanup complet — domeniul %s descărcat", DOMAIN)
    else:
        _LOGGER.error("[Vehicule] Unload EȘUAT pentru entry_id=%s", entry.entry_id)

    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Curăță complet la ștergerea unui vehicul.

    Elimină dispozitivul și entitățile orfane din registry,
    astfel încât o readăugare ulterioară pornește de la zero.
    Dacă e ultima entry, notifică serverul de licențe.
    """
    nr_inmatriculare = entry.data.get(CONF_NR_INMATRICULARE, "")
    numar_normalizat = normalizeaza_numar(nr_inmatriculare)

    _LOGGER.debug(
        "[Vehicule] ── async_remove_entry ── entry_id=%s (%s)",
        entry.entry_id,
        nr_inmatriculare,
    )

    # ── Eliminăm entitățile din Entity Registry ──
    registru_entitati = er.async_get(hass)
    entitati_de_sters = er.async_entries_for_config_entry(
        registru_entitati, entry.entry_id
    )
    for entitate in entitati_de_sters:
        _LOGGER.debug("[Vehicule] Elimin entitatea: %s", entitate.entity_id)
        registru_entitati.async_remove(entitate.entity_id)

    # ── Eliminăm dispozitivul din Device Registry ──
    registru_dispozitive = dr.async_get(hass)
    dispozitiv = registru_dispozitive.async_get_device(
        identifiers={(DOMAIN, numar_normalizat)}
    )
    if dispozitiv is not None:
        _LOGGER.debug(
            "[Vehicule] Elimin dispozitivul: %s (id: %s)",
            dispozitiv.name,
            dispozitiv.id,
        )
        registru_dispozitive.async_remove_device(dispozitiv.id)

    _LOGGER.info("[Vehicule] Vehiculul %s a fost complet eliminat", nr_inmatriculare)

    # ── Notificare licență (doar la ultima entry) ──
    remaining = hass.config_entries.async_entries(DOMAIN)
    if not remaining:
        notify_data = hass.data.pop(f"{DOMAIN}_notify", None)
        if notify_data and notify_data.get("fingerprint"):
            await _send_lifecycle_event(
                notify_data["fingerprint"],
                notify_data.get("license_key", ""),
                "integration_removed",
            )


async def _send_lifecycle_event(
    fingerprint: str, license_key: str, action: str
) -> None:
    """Trimite un eveniment lifecycle direct (fără LicenseManager).

    Folosit în async_remove_entry când LicenseManager nu mai există.
    """
    import hashlib
    import hmac as hmac_lib
    import json
    import time

    import aiohttp

    from .license import INTEGRATION, LICENSE_API_URL

    timestamp = int(time.time())
    payload = {
        "fingerprint": fingerprint,
        "timestamp": timestamp,
        "action": action,
        "license_key": license_key,
        "integration": INTEGRATION,
    }
    data = {k: v for k, v in payload.items() if k != "hmac"}
    msg = json.dumps(data, sort_keys=True).encode()
    payload["hmac"] = hmac_lib.new(
        fingerprint.encode(), msg, hashlib.sha256
    ).hexdigest()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{LICENSE_API_URL}/notify",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Vehicule-HA-Integration/3.0",
                },
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if not result.get("success"):
                        _LOGGER.warning(
                            "[Vehicule] Server a refuzat '%s': %s",
                            action, result.get("error"),
                        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("[Vehicule] Nu s-a putut raporta '%s': %s", action, err)


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
            **structureaza_optiuni(dict(entry.options)),
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

        # Validare structură de bază
        if (
            not isinstance(date_import, dict)
            or CONF_NR_INMATRICULARE not in date_import
        ):
            _notifica_eroare_import(
                hass,
                "Structura JSON este invalida. Fisierul trebuie sa contina "
                "campul 'nr_inmatriculare'.",
            )
            return

        nr = date_import[CONF_NR_INMATRICULARE].strip().upper()
        nr_norm = normalizeaza_numar(nr)

        # Detectăm formatul: v1 (flat cu „optiuni") sau v2 (structurat)
        versiune = date_import.get("version", 1)
        if versiune >= 2:
            # Format nou: categorii structurate → aplatizăm
            optiuni = aplatizeaza_optiuni(date_import)
        elif "optiuni" in date_import and isinstance(
            date_import["optiuni"], dict
        ):
            # Format vechi: opțiuni flat
            optiuni = date_import["optiuni"]
        else:
            _notifica_eroare_import(
                hass,
                "Structura JSON este invalida. Fisierul v1 trebuie sa "
                "contina campul 'optiuni'.",
            )
            return

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
