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
from datetime import date
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    COMBUSTIBIL_OPTIONS,
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
                "itp",
                "administrativ",
                "mentenanta",
                "kilometraj",
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

        if user_input is not None:
            # Validare ani
            errors = valideaza_campuri_an(
                user_input,
                an_max_fabricatie=an_curent + 1,
                an_max_inmatriculare=an_curent,
            )

            if not errors:
                return self._salveaza_si_inchide(user_input)

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

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input)
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
    # 3. ITP
    # ─────────────────────────────────────────
    async def async_step_itp(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele ITP."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input)
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
    # 4. Date administrative / fiscale
    # ─────────────────────────────────────────
    async def async_step_administrativ(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru datele administrative și fiscale.

        Câmpul „Data expirare leasing" apare DOAR dacă tip_proprietate = leasing.
        Dacă utilizatorul schimbă din leasing în proprietate, câmpul dispare
        la următoarea deschidere (și datele de leasing sunt șterse).
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                date_convertite = converteste_date_la_iso(user_input)
                # Dacă tip_proprietate s-a schimbat din leasing în proprietate,
                # ștergem data de expirare leasing din opțiuni
                if date_convertite.get(CONF_TIP_PROPRIETATE) != "leasing":
                    date_convertite.pop(CONF_LEASING_DATA_EXPIRARE, None)
                    # Ștergem și din opțiunile existente (la salvare)
                    optiuni_curente = dict(self.config_entry.options)
                    optiuni_curente.pop(CONF_LEASING_DATA_EXPIRARE, None)
                    optiuni_curente.update(
                        {k: v for k, v in date_convertite.items() if v is not None and v != ""}
                    )
                    # Ștergem câmpurile golite explicit
                    for k, v in date_convertite.items():
                        if v is None or v == "":
                            optiuni_curente.pop(k, None)
                    return self.async_create_entry(data=optiuni_curente)
                return self._salveaza_si_inchide(date_convertite)

        # Determinăm dacă vehiculul e în leasing (din opțiunile salvate)
        este_leasing = (
            self.config_entry.options.get(CONF_TIP_PROPRIETATE) == "leasing"
        )

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

        # Câmpul leasing apare DOAR dacă vehiculul e în leasing
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
            ],
        )

    # ── 5a. Revizie ulei ──
    async def async_step_revizie_ulei(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru revizia de ulei."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input)
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
        """Formular pentru distribuție."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input)
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

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input)
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_ANVELOPE_VARA_DATA): _selector_data(),
                vol.Optional(CONF_ANVELOPE_IARNA_DATA): _selector_data(),
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

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input)
                )

        schema = vol.Schema(
            {
                vol.Optional(CONF_BATERIE_DATA_SCHIMB): _selector_data(),
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
        """Formular pentru plăcuțe și discuri de frână."""
        if user_input is not None:
            return self._salveaza_si_inchide(user_input)

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
            }
        )

        return self.async_show_form(
            step_id="frane",
            data_schema=self.add_suggested_values_to_schema(
                schema, self.config_entry.options
            ),
        )

    # ── 5f. Trusă de prim ajutor ──
    async def async_step_trusa_prim_ajutor(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru trusa de prim ajutor (obligatorie în România)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = valideaza_campuri_data(user_input)
            if not errors:
                return self._salveaza_si_inchide(
                    converteste_date_la_iso(user_input)
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

    # ─────────────────────────────────────────
    # 6. Kilometraj curent
    # ─────────────────────────────────────────
    async def async_step_kilometraj(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Formular pentru actualizarea kilometrajului curent."""
        if user_input is not None:
            return self._salveaza_si_inchide(user_input)

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
    # Utilitar: salvează și închide
    # ─────────────────────────────────────────
    def _salveaza_si_inchide(
        self, user_input: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Îmbină datele noi cu opțiunile existente și închide fluxul.

        Comportament:
        - Câmpuri cu valoare non-goală: se actualizează / adaugă
        - Câmpuri golite explicit (None sau ""): se șterg din opțiuni
        - Câmpuri nemodificate (absent din user_input): rămân neschimbate
        """
        optiuni_noi = {**self.config_entry.options}

        for cheie, valoare in user_input.items():
            if valoare is not None and valoare != "":
                optiuni_noi[cheie] = valoare
            else:
                # Utilizatorul a golit câmpul → ștergem din opțiuni
                optiuni_noi.pop(cheie, None)

        return self.async_create_entry(data=optiuni_noi)
