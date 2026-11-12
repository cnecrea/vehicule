"""
Flux de configurare pentru integrarea Vehicule.

ConfigFlow: adaugă un vehicul nou (cere doar nr. de înmatriculare).
OptionsFlow: meniu cu categorii pentru editarea datelor vehiculului.

Câmpurile de dată folosesc TextSelector cu format românesc ZZ.LL.AAAA
(ex: 18.04.2026). Intern, datele se stochează în format ISO (2026-04-18).

Câmpurile de an folosesc TextSelector cu validare server-side
(evită eroarea „Value X is too small" de la NumberSelector în timpul tastării).
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CATEGORII_ARHIVABILE,
    COMBUSTIBIL_OPTIONS,
    CONF_AN_FABRICATIE,
    CONF_LICENSE_KEY,
    LICENSE_DATA_KEY,
    LICENSE_PURCHASE_URL,
    CONF_AN_PRIMA_INMATRICULARE,
    CONF_ANVELOPE_COST,
    CONF_ANVELOPE_IARNA_DATA,
    CONF_ANVELOPE_VARA_DATA,
    CONF_ARHIVARE_DATE,
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
    CONF_SOFER_NUME,
    CONF_SOFER_CNP,
    CONF_SOFER_NR_PERMIS,
    CONF_SOFER_CATEGORIE_PERMIS,
    CONF_SOFER_DATA_EXPIRARE_PERMIS,
    CONF_TIP_PROPRIETATE,
    CONF_EXTINCTOR_DATA_EXPIRARE,
    CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE,
    CONF_VIN,
    DOMAIN,
    TIP_PROPRIETATE_OPTIONS,
    normalizeaza_numar,
)
from .helpers import (
    FORMAT_DATA_RO,
    converteste_date_la_iso,
    pregateste_valori_sugerate,
    valideaza_campuri_an,
    valideaza_campuri_data,
)

_LOGGER = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Selector UI local
# ─────────────────────────────────────────────


def _selector_data() -> selector.TextSelector:
    """Returnează un TextSelector pentru date în format românesc ZZ.LL.AAAA."""
    return selector.TextSelector(
        selector.TextSelectorConfig(suffix=FORMAT_DATA_RO)
    )


# ─────────────────────────────────────────────
# Licență — etichete tip
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# Config Flow
# ─────────────────────────────────────────────


class VehiculeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flux de configurare pentru adăugarea unui vehicul."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Pasul inițial: solicită numărul de înmatriculare."""
        errors: dict[str, str] = {}

        if user_input is not None:
            numar = user_input[CONF_NR_INMATRICULARE].strip().upper()

            if not numar:
                errors["base"] = "numar_gol"
            elif not re.fullmatch(r"[A-Z0-9]+", numar):
                errors["base"] = "format_numar_invalid"
            else:
                numar_normalizat = normalizeaza_numar(numar)
                await self.async_set_unique_id(numar_normalizat)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=numar,
                    data={CONF_NR_INMATRICULARE: numar},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NR_INMATRICULARE): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(
        self, import_data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Creează o intrare din import (utilizat de serviciul importa_date).

        Acest pas este apelat programatic, nu de utilizator.
        Se ocupă doar de crearea intrării cu numărul de înmatriculare.
        Opțiunile sunt setate ulterior de serviciul de import.
        """
        numar = import_data[CONF_NR_INMATRICULARE].strip().upper()
        numar_normalizat = normalizeaza_numar(numar)

        await self.async_set_unique_id(numar_normalizat)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=numar,
            data={CONF_NR_INMATRICULARE: numar},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VehiculeOptionsFlow:
        """Returnează fluxul de opțiuni pentru editarea datelor."""
        return VehiculeOptionsFlow()


# ─────────────────────────────────────────────
# Options Flow
# ─────────────────────────────────────────────


# ── Textele licenței: aceleași în toate integrările hubinteligent (standardizate pe 12.11.2026) ──

_TIP_LICENTA = {
    # Tipurile emise de WebAPI (LICENSE_DURATION)
    "perpetual": ("permanentă", "permanent"),
    "annual": ("anuală", "annual"),
    "semi_annual": ("semestrială", "semi-annual"),
    "monthly": ("lunară", "monthly"),
}


def _tip_licenta(tip: str | None, is_ro: bool) -> str:
    """Eticheta tipului de licență primit de la server."""
    if not tip:
        return "necunoscut" if is_ro else "unknown"
    ro, en = _TIP_LICENTA.get(tip, (tip, tip))
    return ro if is_ro else en


def _zile_ramase(zile: int, is_ro: bool) -> str:
    """„o zi rămasă”, „5 zile rămase”, „20 de zile rămase” — „1 day left”, „5 days left”."""
    if zile <= 0:
        return "ultima zi" if is_ro else "last day"
    if not is_ro:
        return "1 day left" if zile == 1 else f"{zile} days left"
    if zile == 1:
        return "o zi rămasă"
    return f"{zile} {'de ' if zile % 100 >= 20 or zile % 100 == 0 else ''}zile rămase"


def _status_licenta(mgr, is_ro: bool) -> str:
    """Starea licenței, afișată la pasul „Licență”, deasupra câmpului „Cheie de licență”."""
    from homeassistant.util import dt as dt_util

    def data(moment: float) -> str:
        return dt_util.as_local(dt_util.utc_from_timestamp(moment)).strftime("%d.%m.%Y")

    obtine = f"🛒 {'Obține o licență' if is_ro else 'Get a license'}: {LICENSE_PURCHASE_URL}"
    if mgr.status == "licensed":
        linii = [f"✅ {'Licență activă' if is_ro else 'Active license'} ({_tip_licenta(mgr.license_type, is_ro)})"]
        if mgr.license_key_masked:
            linii[0] += f" — {mgr.license_key_masked}"
        if mgr.activated_at:
            linii.append(f"{'Activată la' if is_ro else 'Activated on'}: {data(mgr.activated_at)}")
        if mgr.license_expires_at:
            linii.append(f"📅 {'Expiră la' if is_ro else 'Expires on'}: {data(mgr.license_expires_at)}")
        else:
            linii.append("Valabilitate: nelimitată" if is_ro else "Validity: unlimited")
        return "\n".join(linii)
    if mgr.status == "trial":
        perioada = "Perioadă de test" if is_ro else "Free trial"
        return "\n".join([f"⏳ {perioada}: {_zile_ramase(mgr.trial_days_remaining, is_ro)}", "", obtine])
    if mgr.status == "expired" and mgr.has_license:
        linii = ["❌ Licență expirată" if is_ro else "❌ License expired"]
        if mgr.license_expires_at:
            linii.append(f"{'Expirată la' if is_ro else 'Expired on'}: {data(mgr.license_expires_at)}")
        return "\n".join([*linii, "", obtine])
    if mgr.status == "expired":
        return "\n".join(["❌ Perioada de test s-a încheiat" if is_ro else "❌ The free trial has ended", "", obtine])
    stare = "❌ Fără licență: senzorii nu se actualizează." if is_ro else "❌ No license: sensors do not update."
    return "\n".join([stare, "", obtine])


class VehiculeOptionsFlow(config_entries.OptionsFlow):
    """Flux de opțiuni cu meniu pentru editarea datelor vehiculului.

    Notă: self.config_entry este disponibil automat în HA 2024+.
    """

    # ─────────────────────────────────────────
    # Meniu principal
    # ─────────────────────────────────────────
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Afișează meniul principal cu categoriile de date."""
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "identificare",
                "rca",
                "casco",
                "itp",
                "rovinieta",
                "administrativ",
                "mentenanta",
                "kilometraj",
                "soferi",
                "licenta",
            ],
        )

    # ─────────────────────────────────────────
    # 1. Date de identificare
    # ─────────────────────────────────────────
    async def async_step_identificare(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele de identificare ale vehiculului.

        Câmpurile An fabricație și An prima înmatriculare folosesc TextSelector
        pentru a evita eroarea „Value X is too small" de la NumberSelector
        în timpul tastării. Validarea se face server-side la submit.
        """
        errors: dict[str, str] = {}
        an_curent = date.today().year

        chei = {
            CONF_MARCA, CONF_MODEL, CONF_VIN, CONF_SERIE_CIV,
            CONF_AN_FABRICATIE, CONF_AN_PRIMA_INMATRICULARE,
            CONF_MOTORIZARE, CONF_COMBUSTIBIL,
            CONF_CAPACITATE_CILINDRICA, CONF_PUTERE_KW, CONF_PUTERE_CP,
        }

        if user_input is not None:
            # Validare ani
            errors = valideaza_campuri_an(
                user_input,
                an_max_fabricatie=an_curent + 1,
                an_max_inmatriculare=an_curent,
            )

            if not errors:
                return self._salveaza_si_inchide(user_input, chei)

        schema = vol.Schema(
            {
                vol.Optional(CONF_MARCA): selector.TextSelector(),
                vol.Optional(CONF_MODEL): selector.TextSelector(),
                vol.Optional(CONF_VIN): selector.TextSelector(),
                vol.Optional(CONF_SERIE_CIV): selector.TextSelector(),
                vol.Optional(CONF_AN_FABRICATIE): selector.TextSelector(
                    selector.TextSelectorConfig(
                        suffix=f"(1900–{an_curent + 1})"
                    )
                ),
                vol.Optional(CONF_AN_PRIMA_INMATRICULARE): selector.TextSelector(
                    selector.TextSelectorConfig(
                        suffix=f"(1900–{an_curent})"
                    )
                ),
                vol.Optional(CONF_MOTORIZARE): selector.TextSelector(),
                vol.Optional(CONF_COMBUSTIBIL): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=COMBUSTIBIL_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="combustibil",
                    )
                ),
                vol.Optional(CONF_CAPACITATE_CILINDRICA): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="cm³",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_PUTERE_KW): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9999, step=1,
                        unit_of_measurement="kW",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_PUTERE_CP): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9999, step=1,
                        unit_of_measurement="CP",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="identificare",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ─────────────────────────────────────────
    # 2. Asigurare RCA
    # ─────────────────────────────────────────
    async def async_step_rca(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele asigurării RCA."""
        errors: dict[str, str] = {}
        chei = {
            CONF_RCA_NUMAR_POLITA, CONF_RCA_COMPANIE,
            CONF_RCA_DATA_EMITERE, CONF_RCA_DATA_EXPIRARE, CONF_RCA_COST,
        }

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="rca",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_RCA_NUMAR_POLITA): selector.TextSelector(),
                vol.Optional(CONF_RCA_COMPANIE): selector.TextSelector(),
                vol.Optional(CONF_RCA_DATA_EMITERE): _selector_data(),
                vol.Optional(CONF_RCA_DATA_EXPIRARE): _selector_data(),
                vol.Optional(CONF_RCA_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="rca",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ─────────────────────────────────────────
    # 2b. Asigurare Casco
    # ─────────────────────────────────────────
    async def async_step_casco(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele asigurării Casco."""
        errors: dict[str, str] = {}
        chei = {
            CONF_CASCO_NUMAR_POLITA, CONF_CASCO_COMPANIE,
            CONF_CASCO_DATA_EMITERE, CONF_CASCO_DATA_EXPIRARE, CONF_CASCO_COST,
        }

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="casco",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_CASCO_NUMAR_POLITA): selector.TextSelector(),
                vol.Optional(CONF_CASCO_COMPANIE): selector.TextSelector(),
                vol.Optional(CONF_CASCO_DATA_EMITERE): _selector_data(),
                vol.Optional(CONF_CASCO_DATA_EXPIRARE): _selector_data(),
                vol.Optional(CONF_CASCO_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="casco",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ─────────────────────────────────────────
    # 3. ITP
    # ─────────────────────────────────────────
    async def async_step_itp(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele ITP.

        Necesită kilometrajul curent configurat (câmpul „Kilometraj la ITP"
        depinde de referința km a vehiculului).
        """
        errors: dict[str, str] = {}
        chei = {CONF_ITP_DATA_EXPIRARE, CONF_ITP_STATIE, CONF_ITP_KILOMETRAJ}

        if not self._verifica_km_curent():
            errors["base"] = "km_necesar"
        elif user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="itp",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_ITP_DATA_EXPIRARE): _selector_data(),
                vol.Optional(CONF_ITP_STATIE): selector.TextSelector(),
                vol.Optional(CONF_ITP_KILOMETRAJ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="itp",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ─────────────────────────────────────────
    # 3b. Rovinieta
    # ─────────────────────────────────────────
    async def async_step_rovinieta(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele rovinietei."""
        errors: dict[str, str] = {}
        chei = {
            CONF_ROVINIETA_DATA_INCEPUT,
            CONF_ROVINIETA_DATA_SFARSIT,
            CONF_ROVINIETA_CATEGORIE,
            CONF_ROVINIETA_PRET,
        }

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="rovinieta",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_ROVINIETA_DATA_INCEPUT): _selector_data(),
                vol.Optional(CONF_ROVINIETA_DATA_SFARSIT): _selector_data(),
                vol.Optional(CONF_ROVINIETA_CATEGORIE): selector.TextSelector(),
                vol.Optional(CONF_ROVINIETA_PRET): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="rovinieta",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ─────────────────────────────────────────
    # 4. Date administrative / fiscale
    # ─────────────────────────────────────────
    async def async_step_administrativ(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele administrative și fiscale.

        Câmpul „Data expirare leasing" apare DOAR dacă tip_proprietate = leasing.

        Comportament dinamic:
        - Dacă vehiculul e DEJA în leasing (salvat), câmpul apare inline.
        - Dacă utilizatorul SCHIMBĂ acum în leasing (prima dată), se salvează
          datele admin și se redirectează la pasul „leasing_data" pentru dată.
        - Dacă utilizatorul schimbă din leasing în altceva, câmpul dispare
          și datele de leasing sunt șterse automat.
        """
        errors: dict[str, str] = {}
        chei = {
            CONF_PROPRIETAR, CONF_TIP_PROPRIETATE,
            CONF_IMPOZIT_SUMA, CONF_IMPOZIT_SCADENTA, CONF_IMPOZIT_LOCALITATE,
        }

        # Determinăm dacă vehiculul e DEJA în leasing (din opțiunile salvate)
        este_leasing = (
            self.config_entry.options.get(CONF_TIP_PROPRIETATE) == "leasing"
        )

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                date_convertite = converteste_date_la_iso(user_input)
                chei.add(CONF_LEASING_DATA_EXPIRARE)

                # Dacă utilizatorul tocmai a selectat „leasing" și NU era
                # deja leasing → câmpul de dată NU era vizibil în formular.
                # Salvăm temporar datele admin și redirectăm la pasul dedicat.
                tip_selectat = user_input.get(CONF_TIP_PROPRIETATE)
                if tip_selectat == "leasing" and not este_leasing:
                    self._date_admin_temp = date_convertite
                    self._chei_admin_temp = chei
                    return await self.async_step_leasing_data()

                return self._salveaza_si_inchide(date_convertite, chei)

        # Construim schema dinamic
        campuri: dict[vol.Optional, Any] = {
            vol.Optional(CONF_PROPRIETAR): selector.TextSelector(),
            vol.Optional(CONF_TIP_PROPRIETATE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=TIP_PROPRIETATE_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="tip_proprietate",
                )
            ),
            vol.Optional(CONF_IMPOZIT_SUMA): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=999_999, step=1,
                    unit_of_measurement="RON",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_IMPOZIT_SCADENTA): _selector_data(),
            vol.Optional(CONF_IMPOZIT_LOCALITATE): selector.TextSelector(),
        }

        # Câmpul leasing apare inline DOAR dacă vehiculul e DEJA în leasing
        if este_leasing:
            campuri[vol.Optional(CONF_LEASING_DATA_EXPIRARE)] = _selector_data()

        schema = vol.Schema(campuri)

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="administrativ",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    async def async_step_leasing_data(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Pas suplimentar: data expirare leasing.

        Apare automat după ce utilizatorul selectează „Leasing" ca tip
        de proprietate (prima dată). La vizitele ulterioare, câmpul
        apare inline în formularul administrativ.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                date_convertite = converteste_date_la_iso(user_input)
                # Combinăm datele administrative cu data de leasing
                date_complete = {**self._date_admin_temp, **date_convertite}
                chei_complete = self._chei_admin_temp | {
                    CONF_LEASING_DATA_EXPIRARE
                }
                return self._salveaza_si_inchide(date_complete, chei_complete)

        schema = vol.Schema(
            {
                vol.Optional(CONF_LEASING_DATA_EXPIRARE): _selector_data(),
            }
        )

        valori = pregateste_valori_sugerate(self.config_entry.options)

        return self.async_show_form(
            step_id="leasing_data",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ─────────────────────────────────────────
    # 5. Mentenanță – Sub-meniu
    # ─────────────────────────────────────────
    async def async_step_mentenanta(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Sub-meniu pentru categoriile de mentenanță."""
        return self.async_show_menu(
            step_id="mentenanta",
            menu_options=[
                "revizie_ulei",
                "distributie",
                "anvelope",
                "baterie",
                "frane",
                "trusa_prim_ajutor",
                "extinctor",
            ],
        )

    # ── 5a. Revizie ulei ──
    async def async_step_revizie_ulei(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru revizia de ulei.

        Necesită kilometrajul curent configurat (senzorul calculează
        km rămași până la următoarea revizie).
        """
        errors: dict[str, str] = {}
        chei = {
            CONF_REVIZIE_ULEI_KM_ULTIMUL, CONF_REVIZIE_ULEI_KM_URMATOR,
            CONF_REVIZIE_ULEI_DATA, CONF_REVIZIE_ULEI_COST,
        }

        if not self._verifica_km_curent():
            errors["base"] = "km_necesar"
        elif user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="revizie_ulei",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_REVIZIE_ULEI_KM_ULTIMUL): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_REVIZIE_ULEI_KM_URMATOR): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_REVIZIE_ULEI_DATA): _selector_data(),
                vol.Optional(CONF_REVIZIE_ULEI_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="revizie_ulei",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ── 5b. Distribuție ──
    async def async_step_distributie(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru distribuție.

        Necesită kilometrajul curent configurat (senzorul calculează
        km rămași până la următoarea schimbare distribuție).
        """
        errors: dict[str, str] = {}
        chei = {
            CONF_DISTRIBUTIE_KM_ULTIMUL, CONF_DISTRIBUTIE_KM_URMATOR,
            CONF_DISTRIBUTIE_DATA, CONF_DISTRIBUTIE_COST,
        }

        if not self._verifica_km_curent():
            errors["base"] = "km_necesar"
        elif user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="distributie",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_DISTRIBUTIE_KM_ULTIMUL): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_DISTRIBUTIE_KM_URMATOR): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_DISTRIBUTIE_DATA): _selector_data(),
                vol.Optional(CONF_DISTRIBUTIE_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="distributie",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ── 5c. Anvelope ──
    async def async_step_anvelope(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru anvelope."""
        errors: dict[str, str] = {}
        chei = {CONF_ANVELOPE_VARA_DATA, CONF_ANVELOPE_IARNA_DATA, CONF_ANVELOPE_COST}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="anvelope",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_ANVELOPE_VARA_DATA): _selector_data(),
                vol.Optional(CONF_ANVELOPE_IARNA_DATA): _selector_data(),
                vol.Optional(CONF_ANVELOPE_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="anvelope",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ── 5d. Baterie ──
    async def async_step_baterie(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru baterie."""
        errors: dict[str, str] = {}
        chei = {CONF_BATERIE_DATA_SCHIMB, CONF_BATERIE_COST}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei,
                    categorie_arhivare="baterie",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_BATERIE_DATA_SCHIMB): _selector_data(),
                vol.Optional(CONF_BATERIE_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="baterie",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ── 5e. Frâne ──
    async def async_step_frane(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru plăcuțe și discuri de frână.

        Necesită kilometrajul curent configurat (senzorii calculează
        km rămași până la următoarea schimbare plăcuțe/discuri).
        """
        errors: dict[str, str] = {}
        chei = {
            CONF_PLACUTE_FRANA_KM_ULTIMUL, CONF_PLACUTE_FRANA_KM_URMATOR,
            CONF_PLACUTE_FRANA_DATA, CONF_PLACUTE_FRANA_COST,
            CONF_DISCURI_FRANA_KM_ULTIMUL, CONF_DISCURI_FRANA_KM_URMATOR,
            CONF_DISCURI_FRANA_DATA, CONF_DISCURI_FRANA_COST,
        }

        if not self._verifica_km_curent():
            errors["base"] = "km_necesar"
        elif user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input),
                    chei,
                    categorie_arhivare="frane",
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_PLACUTE_FRANA_KM_ULTIMUL): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_PLACUTE_FRANA_KM_URMATOR): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_PLACUTE_FRANA_DATA): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Optional(CONF_PLACUTE_FRANA_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_DISCURI_FRANA_KM_ULTIMUL): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_DISCURI_FRANA_KM_URMATOR): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_DISCURI_FRANA_DATA): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Optional(CONF_DISCURI_FRANA_COST): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=99999, step=1,
                        unit_of_measurement="RON",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ARHIVARE_DATE, default=False
                ): selector.BooleanSelector(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="frane",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ── 5f. Trusă de prim ajutor ──
    async def async_step_trusa_prim_ajutor(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru trusa de prim ajutor (obligatorie în România)."""
        errors: dict[str, str] = {}
        chei = {CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE): _selector_data(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="trusa_prim_ajutor",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ── 5g. Extinctor ──
    async def async_step_extinctor(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru extinctor (obligatoriu în România)."""
        errors: dict[str, str] = {}
        chei = {CONF_EXTINCTOR_DATA_EXPIRARE}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input), chei
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_EXTINCTOR_DATA_EXPIRARE): _selector_data(),
            }
        )

        valori = pregateste_valori_sugerate(
            {**self.config_entry.options, **(user_input or {})}
            if user_input
            else self.config_entry.options
        )

        return self.async_show_form(
            step_id="extinctor",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
        )

    # ─────────────────────────────────────────
    # 6. Kilometraj curent
    # ─────────────────────────────────────────
    async def async_step_kilometraj(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru actualizarea kilometrajului curent."""
        chei = {CONF_KM_CURENT}
        if user_input is not None:
            return self._salveaza_si_inchide(user_input, chei)

        schema = vol.Schema(
            {
                vol.Optional(CONF_KM_CURENT): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=9_999_999, step=1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="kilometraj",
            data_schema=self.add_suggested_values_to_schema(
                schema, self.config_entry.options
            ),
        )

    # ─────────────────────────────────────────
    # 7. Șoferi
    # ─────────────────────────────────────────

    def _get_soferi(self) -> list[dict[str, Any]]:
        """Returnează lista de șoferi din options."""
        return list(self.config_entry.options.get(CONF_SOFERI, []))

    def _save_soferi(self, soferi: list[dict[str, Any]]) -> config_entries.ConfigFlowResult:
        """Salvează lista de șoferi și închide flow-ul."""
        optiuni_noi = {**self.config_entry.options, CONF_SOFERI: soferi}
        self.hass.config_entries.async_update_entry(
            self.config_entry, options=optiuni_noi,
        )
        return self.async_create_entry(data=optiuni_noi)

    async def async_step_soferi(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Sub-meniu șoferi — analog cu mentenanță.

        Folosește async_show_menu cu dict menu_options pentru
        etichete dinamice (numele șoferilor existenți).
        """
        soferi = self._get_soferi()
        is_ro = self.hass.config.language == "ro"

        # Construiește dict de opțiuni: cheie = step_id, valoare = etichetă
        menu_opts: dict[str, str] = {
            "soferi_adauga": "Adaugă un șofer nou" if is_ro else "Add a new driver",
        }
        for i, s in enumerate(soferi):
            fallback = f"Șofer {i + 1}" if is_ro else f"Driver {i + 1}"
            nume = s.get(CONF_SOFER_NUME, fallback)
            prefix = "Editare" if is_ro else "Edit"
            menu_opts[f"soferi_editeaza_{i}"] = f"{prefix}: {nume}"

        return self.async_show_menu(
            step_id="soferi",
            menu_options=menu_opts,
        )

    async def async_step_soferi_adauga(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular adăugare șofer nou."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validare data expirare permis
            errors = valideaza_campuri_data(user_input)
            if not user_input.get(CONF_SOFER_NUME, "").strip():
                errors["base"] = "sofer_nume_gol"
            if not errors:
                sofer_nou = {
                    CONF_SOFER_NUME: user_input[CONF_SOFER_NUME].strip(),
                    CONF_SOFER_CNP: user_input.get(CONF_SOFER_CNP, "").strip(),
                    CONF_SOFER_NR_PERMIS: user_input.get(CONF_SOFER_NR_PERMIS, "").strip(),
                    CONF_SOFER_CATEGORIE_PERMIS: user_input.get(CONF_SOFER_CATEGORIE_PERMIS, "").strip(),
                    CONF_SOFER_DATA_EXPIRARE_PERMIS: converteste_date_la_iso(user_input).get(
                        CONF_SOFER_DATA_EXPIRARE_PERMIS, ""
                    ),
                }
                soferi = self._get_soferi()
                soferi.append(sofer_nou)
                return self._save_soferi(soferi)

        schema = vol.Schema(
            {
                vol.Required(CONF_SOFER_NUME): selector.TextSelector(),
                vol.Optional(CONF_SOFER_CNP): selector.TextSelector(),
                vol.Optional(CONF_SOFER_NR_PERMIS): selector.TextSelector(),
                vol.Optional(CONF_SOFER_CATEGORIE_PERMIS): selector.TextSelector(
                    selector.TextSelectorConfig(suffix="ex: B, B+E, C")
                ),
                vol.Optional(CONF_SOFER_DATA_EXPIRARE_PERMIS): _selector_data(),
            }
        )
        return self.async_show_form(
            step_id="soferi_adauga",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_soferi_editeaza(
        self, user_input: dict[str, Any] | None = None,
        *, idx: int | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Editare / ștergere șofer existent. idx setat de dispatcher."""
        if idx is None:
            idx = getattr(self, "_sofer_edit_idx", 0)
        else:
            self._sofer_edit_idx = idx

        soferi = self._get_soferi()
        if idx >= len(soferi):
            return self._save_soferi(soferi)

        sofer = soferi[idx]
        errors: dict[str, str] = {}

        if user_input is not None:
            # Butonul de ștergere
            if user_input.get("_sterge_sofer"):
                soferi.pop(idx)
                return self._save_soferi(soferi)

            errors = valideaza_campuri_data(user_input)
            if not user_input.get(CONF_SOFER_NUME, "").strip():
                errors["base"] = "sofer_nume_gol"
            if not errors:
                soferi[idx] = {
                    CONF_SOFER_NUME: user_input[CONF_SOFER_NUME].strip(),
                    CONF_SOFER_CNP: user_input.get(CONF_SOFER_CNP, "").strip(),
                    CONF_SOFER_NR_PERMIS: user_input.get(CONF_SOFER_NR_PERMIS, "").strip(),
                    CONF_SOFER_CATEGORIE_PERMIS: user_input.get(CONF_SOFER_CATEGORIE_PERMIS, "").strip(),
                    CONF_SOFER_DATA_EXPIRARE_PERMIS: converteste_date_la_iso(user_input).get(
                        CONF_SOFER_DATA_EXPIRARE_PERMIS, ""
                    ),
                }
                return self._save_soferi(soferi)

        from .helpers import format_data_ro
        schema = vol.Schema(
            {
                vol.Required(CONF_SOFER_NUME): selector.TextSelector(),
                vol.Optional(CONF_SOFER_CNP): selector.TextSelector(),
                vol.Optional(CONF_SOFER_NR_PERMIS): selector.TextSelector(),
                vol.Optional(CONF_SOFER_CATEGORIE_PERMIS): selector.TextSelector(
                    selector.TextSelectorConfig(suffix="ex: B, B+E, C")
                ),
                vol.Optional(CONF_SOFER_DATA_EXPIRARE_PERMIS): _selector_data(),
                vol.Optional("_sterge_sofer"): selector.BooleanSelector(),
            }
        )

        valori = {
            CONF_SOFER_NUME: sofer.get(CONF_SOFER_NUME, ""),
            CONF_SOFER_CNP: sofer.get(CONF_SOFER_CNP, ""),
            CONF_SOFER_NR_PERMIS: sofer.get(CONF_SOFER_NR_PERMIS, ""),
            CONF_SOFER_CATEGORIE_PERMIS: sofer.get(CONF_SOFER_CATEGORIE_PERMIS, ""),
            CONF_SOFER_DATA_EXPIRARE_PERMIS: format_data_ro(sofer.get(CONF_SOFER_DATA_EXPIRARE_PERMIS, "")),
        }

        return self.async_show_form(
            step_id="soferi_editeaza",
            data_schema=self.add_suggested_values_to_schema(schema, valori),
            errors=errors,
            description_placeholders={
                "sofer_nume": sofer.get(
                    CONF_SOFER_NUME,
                    "Șofer" if self.hass.config.language == "ro" else "Driver",
                )
            },
        )

    # Dispatcher-e dinamice: soferi_editeaza_0, soferi_editeaza_1, ...
    def __getattr__(self, name: str) -> Any:
        if name.startswith("async_step_soferi_editeaza_"):
            idx_str = name.replace("async_step_soferi_editeaza_", "")
            try:
                idx = int(idx_str)
            except ValueError:
                raise AttributeError(name)

            async def _step(user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
                return await self.async_step_soferi_editeaza(user_input, idx=idx)
            return _step
        raise AttributeError(name)

    # ─────────────────────────────────────────
    # 8. Licențiere
    # ─────────────────────────────────────────
    async def async_step_licenta(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru activarea / vizualizarea licenței Vehicule."""
        from .license import LicenseManager

        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] = {}

        # Obține LicenseManager
        mgr: LicenseManager | None = self.hass.data.get(DOMAIN, {}).get(
            LICENSE_DATA_KEY
        )
        if mgr is None:
            mgr = LicenseManager(self.hass)
            await mgr.async_load()

        description_placeholders["license_status"] = _status_licenta(mgr, is_ro)

        if user_input is not None:
            cheie = user_input.get(CONF_LICENSE_KEY, "").strip()

            if not cheie:
                errors["base"] = "license_key_empty"
            elif len(cheie) < 10:
                errors["base"] = "license_key_invalid"
            else:
                # Activare prin API
                result = await mgr.async_activate(cheie)

                if result.get("success"):
                    # Notificare de succes
                    from homeassistant.components import (
                        persistent_notification,
                    )

                    tip_label = _tip_licenta(mgr.license_type, is_ro)
                    if is_ro:
                        notif_msg = f"Licența Vehicule este activă ({tip_label})."
                        notif_title = "Licență activată"
                    else:
                        notif_msg = f"The Vehicule license is active ({tip_label})."
                        notif_title = "License activated"

                    persistent_notification.async_create(
                        self.hass,
                        notif_msg,
                        title=notif_title,
                        notification_id="vehicule_license_activated",
                    )
                    return self.async_create_entry(
                        data=self.config_entry.options
                    )

                # Mapare erori API (codurile WebAPI /activate + erorile locale)
                api_error = result.get("error", "unknown_error")
                error_map = {
                    "invalid_key": "license_key_invalid",
                    "already_used": "license_already_used",
                    "expired_key": "license_key_expired",
                    "fingerprint_mismatch": "license_fingerprint_mismatch",
                    "network_error": "license_network_error",
                    "http_503": "license_network_error",  # server temporar ocupat
                    "http_502": "license_network_error",
                    "http_504": "license_network_error",
                }
                errors["base"] = error_map.get(api_error, "license_server_error")

        schema = vol.Schema(
            {
                vol.Optional(CONF_LICENSE_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                        suffix="VULE-XXXX-XXXX-XXXX-XXXX",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="licenta",
            data_schema=schema,
            errors=errors,
            description_placeholders=description_placeholders,
        )

    # ─────────────────────────────────────────
    # Utilitar: salvează și închide
    # ─────────────────────────────────────────
    def _salveaza_si_inchide(
        self,
        user_input: dict[str, Any],
        chei_formular: set[str] | None = None,
        categorie_arhivare: str | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Îmbină datele noi cu opțiunile existente și închide fluxul.

        Comportament:
        - Câmpuri cu valoare non-goală: se actualizează / adaugă
        - Câmpuri golite explicit (None sau ""): se șterg din opțiuni
        - Câmpuri din formular absente din user_input: se șterg din opțiuni
          (HA nu trimite câmpuri vol.Optional lăsate goale de utilizator)
        - Câmpuri nemodificate (absent din user_input ȘI din chei_formular):
          rămân neschimbate

        Dacă categorie_arhivare este specificată ȘI utilizatorul a bifat
        opțiunea de arhivare, datele vechi sunt salvate în lista _istoric
        înainte de suprascrierea cu date noi.
        """
        # Extragem flag-ul de arhivare din user_input (câmp UI-only, nu se salvează)
        doreste_arhivare = user_input.pop(CONF_ARHIVARE_DATE, False)

        optiuni_noi = {**self.config_entry.options}

        # ── Arhivare datelor vechi (doar dacă utilizatorul a bifat) ──
        if (
            doreste_arhivare
            and categorie_arhivare
            and categorie_arhivare in CATEGORII_ARHIVABILE
        ):
            campuri_categorie = CATEGORII_ARHIVABILE[categorie_arhivare]
            date_vechi: dict[str, Any] = {}
            for eticheta, cheie_const in campuri_categorie.items():
                val = optiuni_noi.get(cheie_const)
                if val is not None and val != "":
                    date_vechi[eticheta] = val
            if date_vechi:
                istoric = list(optiuni_noi.get(CONF_ISTORIC, []))
                istoric.append(
                    {
                        "tip": categorie_arhivare,
                        "data_arhivare": date.today().isoformat(),
                        "date": date_vechi,
                    }
                )
                optiuni_noi[CONF_ISTORIC] = istoric

        # ── Îmbinare date noi ──
        for cheie, valoare in user_input.items():
            if valoare is not None and valoare != "":
                optiuni_noi[cheie] = valoare
            else:
                # Utilizatorul a golit câmpul → ștergem din opțiuni
                optiuni_noi.pop(cheie, None)

        # Câmpuri care erau în formular dar NU au fost trimise de HA
        # (= utilizatorul le-a golit) → le ștergem din opțiuni
        if chei_formular:
            for cheie in chei_formular:
                if cheie not in user_input:
                    optiuni_noi.pop(cheie, None)

        return self.async_create_entry(data=optiuni_noi)

    def _verifica_km_curent(self) -> bool:
        """Verifică dacă kilometrajul curent este configurat.

        Pașii ITP, Revizie ulei, Distribuție și Frâne necesită km_curent
        deoarece senzorii lor depind de kilometrajul vehiculului.
        """
        return self.config_entry.options.get(CONF_KM_CURENT) is not None
