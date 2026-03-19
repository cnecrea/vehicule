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
    # 7. Licențiere
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

        # Informații pentru descrierea formularului
        server_status = mgr.status  # 'licensed', 'trial', 'expired', 'unlicensed'

        if server_status == "licensed":
            from datetime import datetime

            tip = mgr.license_type or "necunoscut"
            status_lines = [f"✅ Licență activă ({tip})"]

            if mgr.license_key_masked:
                status_lines[0] += f" — {mgr.license_key_masked}"

            # Data activării
            if mgr.activated_at:
                act_date = datetime.fromtimestamp(
                    mgr.activated_at
                ).strftime("%d.%m.%Y %H:%M")
                status_lines.append(f"Activată la: {act_date}")

            # Data expirării
            if mgr.license_expires_at:
                exp_date = datetime.fromtimestamp(
                    mgr.license_expires_at
                ).strftime("%d.%m.%Y %H:%M")
                status_lines.append(f"📅 Expiră la: {exp_date}")
            elif tip == "perpetual":
                status_lines.append("Valabilitate: nelimitată (perpetuă)")

            description_placeholders["license_status"] = "\n".join(
                status_lines
            )

        elif server_status == "trial":
            description_placeholders["license_status"] = (
                f"⏳ Evaluare — {mgr.trial_days_remaining} zile rămase"
            )
        elif server_status == "expired":
            from datetime import datetime

            status_lines = ["❌ Licență expirată"]

            if mgr.activated_at:
                act_date = datetime.fromtimestamp(
                    mgr.activated_at
                ).strftime("%d.%m.%Y")
                status_lines.append(f"Activată la: {act_date}")
            if mgr.license_expires_at:
                exp_date = datetime.fromtimestamp(
                    mgr.license_expires_at
                ).strftime("%d.%m.%Y")
                status_lines.append(f"Expirată la: {exp_date}")

            description_placeholders["license_status"] = "\n".join(
                status_lines
            )
        else:
            description_placeholders["license_status"] = (
                "❌ Fără licență — funcționalitate blocată"
            )

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

                    _LICENSE_TYPE_RO = {
                        "monthly": "lunară",
                        "yearly": "anuală",
                        "perpetual": "perpetuă",
                        "trial": "evaluare",
                    }
                    tip_ro = _LICENSE_TYPE_RO.get(
                        mgr.license_type, mgr.license_type or "necunoscut"
                    )

                    persistent_notification.async_create(
                        self.hass,
                        f"Licența Vehicule a fost activată cu succes! "
                        f"Tip: {tip_ro}.",
                        title="Licență activată",
                        notification_id="vehicule_license_activated",
                    )
                    return self.async_create_entry(
                        data=self.config_entry.options
                    )

                # Mapare erori API
                api_error = result.get("error", "unknown_error")
                error_map = {
                    "invalid_key": "license_key_invalid",
                    "already_used": "license_already_used",
                    "expired_key": "license_key_expired",
                    "fingerprint_mismatch": "license_fingerprint_mismatch",
                    "invalid_signature": "license_server_error",
                    "network_error": "license_network_error",
                    "server_error": "license_server_error",
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
