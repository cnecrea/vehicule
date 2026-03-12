"""Constante pentru integrarea Vehicule."""

from typing import Final

# ─────────────────────────────────────────────
# Domeniu și platforme
# ─────────────────────────────────────────────
DOMAIN: Final = "vehicule"
PLATFORMS: Final = ["sensor"]

# ─────────────────────────────────────────────
# Date de identificare vehicul
# ─────────────────────────────────────────────
CONF_NR_INMATRICULARE: Final = "nr_inmatriculare"
CONF_SERIE_CIV: Final = "serie_civ"
CONF_VIN: Final = "vin"
CONF_MARCA: Final = "marca"
CONF_MODEL: Final = "model"
CONF_AN_FABRICATIE: Final = "an_fabricatie"
CONF_AN_PRIMA_INMATRICULARE: Final = "an_prima_inmatriculare"
CONF_MOTORIZARE: Final = "motorizare"
CONF_COMBUSTIBIL: Final = "combustibil"
CONF_CAPACITATE_CILINDRICA: Final = "capacitate_cilindrica"
CONF_PUTERE_KW: Final = "putere_kw"
CONF_PUTERE_CP: Final = "putere_cp"

# ─────────────────────────────────────────────
# Kilometraj
# ─────────────────────────────────────────────
CONF_KM_CURENT: Final = "km_curent"

# ─────────────────────────────────────────────
# RCA (Asigurare obligatorie)
# ─────────────────────────────────────────────
CONF_RCA_NUMAR_POLITA: Final = "rca_numar_polita"
CONF_RCA_COMPANIE: Final = "rca_companie"
CONF_RCA_DATA_EMITERE: Final = "rca_data_emitere"
CONF_RCA_DATA_EXPIRARE: Final = "rca_data_expirare"
CONF_RCA_COST: Final = "rca_cost"

# ─────────────────────────────────────────────
# ITP (Inspecție tehnică periodică)
# ─────────────────────────────────────────────
CONF_ITP_DATA_EXPIRARE: Final = "itp_data_expirare"
CONF_ITP_STATIE: Final = "itp_statie"
CONF_ITP_KILOMETRAJ: Final = "itp_kilometraj"

# ─────────────────────────────────────────────
# Date administrative / fiscale
# ─────────────────────────────────────────────
CONF_IMPOZIT_SUMA: Final = "impozit_suma"
CONF_IMPOZIT_SCADENTA: Final = "impozit_scadenta"
CONF_IMPOZIT_LOCALITATE: Final = "impozit_localitate"
CONF_PROPRIETAR: Final = "proprietar"
CONF_TIP_PROPRIETATE: Final = "tip_proprietate"
CONF_LEASING_DATA_EXPIRARE: Final = "leasing_data_expirare"

# ─────────────────────────────────────────────
# Mentenanță – Revizie ulei
# ─────────────────────────────────────────────
CONF_REVIZIE_ULEI_KM_ULTIMUL: Final = "revizie_ulei_km_ultimul"
CONF_REVIZIE_ULEI_KM_URMATOR: Final = "revizie_ulei_km_urmator"
CONF_REVIZIE_ULEI_DATA: Final = "revizie_ulei_data"

# ─────────────────────────────────────────────
# Mentenanță – Distribuție
# ─────────────────────────────────────────────
CONF_DISTRIBUTIE_KM_ULTIMUL: Final = "distributie_km_ultimul"
CONF_DISTRIBUTIE_KM_URMATOR: Final = "distributie_km_urmator"
CONF_DISTRIBUTIE_DATA: Final = "distributie_data"

# ─────────────────────────────────────────────
# Mentenanță – Anvelope
# ─────────────────────────────────────────────
CONF_ANVELOPE_VARA_DATA: Final = "anvelope_vara_data"
CONF_ANVELOPE_IARNA_DATA: Final = "anvelope_iarna_data"

# ─────────────────────────────────────────────
# Mentenanță – Baterie
# ─────────────────────────────────────────────
CONF_BATERIE_DATA_SCHIMB: Final = "baterie_data_schimb"

# ─────────────────────────────────────────────
# Echipament obligatoriu – Trusă de prim ajutor
# ─────────────────────────────────────────────
CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE: Final = "trusa_prim_ajutor_data_expirare"

# ─────────────────────────────────────────────
# Mentenanță – Frâne
# ─────────────────────────────────────────────
CONF_PLACUTE_FRANA_KM_ULTIMUL: Final = "placute_frana_km_ultimul"
CONF_PLACUTE_FRANA_KM_URMATOR: Final = "placute_frana_km_urmator"
CONF_DISCURI_FRANA_KM_ULTIMUL: Final = "discuri_frana_km_ultimul"
CONF_DISCURI_FRANA_KM_URMATOR: Final = "discuri_frana_km_urmator"

# ─────────────────────────────────────────────
# Opțiuni pentru selectoare
# ─────────────────────────────────────────────
COMBUSTIBIL_OPTIONS: Final = [
    "benzina",
    "diesel",
    "hybrid",
    "electric",
    "gpl",
]

TIP_PROPRIETATE_OPTIONS: Final = [
    "proprietate",
    "leasing",
]

# ─────────────────────────────────────────────
# Stări senzori
# ─────────────────────────────────────────────
STARE_NECONFIGURAT: Final = "neconfigurat"
STARE_EXPIRAT: Final = "expirat"
STARE_VALID: Final = "valid"

# ─────────────────────────────────────────────
# Servicii
# ─────────────────────────────────────────────
SERVICE_ACTUALIZEAZA_DATE: Final = "actualizeaza_date"

# ─────────────────────────────────────────────
# Atribute dispozitiv
# ─────────────────────────────────────────────
ATTR_NR_INMATRICULARE: Final = "nr_inmatriculare"
ATTR_MARCA: Final = "marca"
ATTR_MODEL: Final = "model"


def normalizeaza_numar(numar: str) -> str:
    """Normalizează numărul de înmatriculare pentru utilizare în ID-uri.

    Exemplu: 'B 123 ABC' -> 'b_123_abc'
    """
    return (
        numar.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "")
    )
