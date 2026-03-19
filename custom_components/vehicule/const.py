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
# Casco (Asigurare facultativă)
# ─────────────────────────────────────────────
CONF_CASCO_NUMAR_POLITA: Final = "casco_numar_polita"
CONF_CASCO_COMPANIE: Final = "casco_companie"
CONF_CASCO_DATA_EMITERE: Final = "casco_data_emitere"
CONF_CASCO_DATA_EXPIRARE: Final = "casco_data_expirare"
CONF_CASCO_COST: Final = "casco_cost"

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
CONF_REVIZIE_ULEI_COST: Final = "revizie_ulei_cost"

# ─────────────────────────────────────────────
# Mentenanță – Distribuție
# ─────────────────────────────────────────────
CONF_DISTRIBUTIE_KM_ULTIMUL: Final = "distributie_km_ultimul"
CONF_DISTRIBUTIE_KM_URMATOR: Final = "distributie_km_urmator"
CONF_DISTRIBUTIE_DATA: Final = "distributie_data"
CONF_DISTRIBUTIE_COST: Final = "distributie_cost"

# ─────────────────────────────────────────────
# Mentenanță – Anvelope
# ─────────────────────────────────────────────
CONF_ANVELOPE_VARA_DATA: Final = "anvelope_vara_data"
CONF_ANVELOPE_IARNA_DATA: Final = "anvelope_iarna_data"
CONF_ANVELOPE_COST: Final = "anvelope_cost"

# ─────────────────────────────────────────────
# Mentenanță – Baterie
# ─────────────────────────────────────────────
CONF_BATERIE_DATA_SCHIMB: Final = "baterie_data_schimb"
CONF_BATERIE_COST: Final = "baterie_cost"

# ─────────────────────────────────────────────
# Echipament obligatoriu – Trusă de prim ajutor
# ─────────────────────────────────────────────
CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE: Final = "trusa_prim_ajutor_data_expirare"

# ─────────────────────────────────────────────
# Echipament obligatoriu – Extinctor
# ─────────────────────────────────────────────
CONF_EXTINCTOR_DATA_EXPIRARE: Final = "extinctor_data_expirare"

# ─────────────────────────────────────────────
# Rovinieta
# ─────────────────────────────────────────────
CONF_ROVINIETA_DATA_INCEPUT: Final = "rovinieta_data_inceput"
CONF_ROVINIETA_DATA_SFARSIT: Final = "rovinieta_data_sfarsit"
CONF_ROVINIETA_CATEGORIE: Final = "rovinieta_categorie"
CONF_ROVINIETA_PRET: Final = "rovinieta_pret"

# ─────────────────────────────────────────────
# Mentenanță – Frâne
# ─────────────────────────────────────────────
CONF_PLACUTE_FRANA_KM_ULTIMUL: Final = "placute_frana_km_ultimul"
CONF_PLACUTE_FRANA_KM_URMATOR: Final = "placute_frana_km_urmator"
CONF_PLACUTE_FRANA_DATA: Final = "placute_frana_data"
CONF_PLACUTE_FRANA_COST: Final = "placute_frana_cost"
CONF_DISCURI_FRANA_KM_ULTIMUL: Final = "discuri_frana_km_ultimul"
CONF_DISCURI_FRANA_KM_URMATOR: Final = "discuri_frana_km_urmator"
CONF_DISCURI_FRANA_DATA: Final = "discuri_frana_data"
CONF_DISCURI_FRANA_COST: Final = "discuri_frana_cost"

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
SERVICE_EXPORTA_DATE: Final = "exporta_date"
SERVICE_IMPORTA_DATE: Final = "importa_date"

# ─────────────────────────────────────────────
# Backup
# ─────────────────────────────────────────────
BACKUP_VERSION: Final = 2

# ─────────────────────────────────────────────
# Istoric costuri
# ─────────────────────────────────────────────
CONF_ISTORIC: Final = "_istoric"
CONF_ARHIVARE_DATE: Final = "_arhivare_date"

# ─────────────────────────────────────────────
# Atribute dispozitiv
# ─────────────────────────────────────────────
ATTR_NR_INMATRICULARE: Final = "nr_inmatriculare"
ATTR_MARCA: Final = "marca"
ATTR_MODEL: Final = "model"


# ─────────────────────────────────────────────
# Categorii arhivabile (pentru istoric costuri)
# ─────────────────────────────────────────────
# Dicționar: categorie → {eticheta_afișare: constanta_conf}
# Folosit de _salveaza_si_inchide() pentru a arhiva datele vechi
# înainte de suprascrierea cu date noi.
CATEGORII_ARHIVABILE: Final = {
    "rca": {
        "Număr poliță": CONF_RCA_NUMAR_POLITA,
        "Companie": CONF_RCA_COMPANIE,
        "Data emitere": CONF_RCA_DATA_EMITERE,
        "Data expirare": CONF_RCA_DATA_EXPIRARE,
        "Cost (RON)": CONF_RCA_COST,
    },
    "casco": {
        "Număr poliță": CONF_CASCO_NUMAR_POLITA,
        "Companie": CONF_CASCO_COMPANIE,
        "Data emitere": CONF_CASCO_DATA_EMITERE,
        "Data expirare": CONF_CASCO_DATA_EXPIRARE,
        "Cost (RON)": CONF_CASCO_COST,
    },
    "itp": {
        "Data expirare": CONF_ITP_DATA_EXPIRARE,
        "Stație": CONF_ITP_STATIE,
        "Kilometraj": CONF_ITP_KILOMETRAJ,
    },
    "rovinieta": {
        "Data început": CONF_ROVINIETA_DATA_INCEPUT,
        "Data sfârșit": CONF_ROVINIETA_DATA_SFARSIT,
        "Categorie": CONF_ROVINIETA_CATEGORIE,
        "Preț (RON)": CONF_ROVINIETA_PRET,
    },
    "revizie_ulei": {
        "Km ultima revizie": CONF_REVIZIE_ULEI_KM_ULTIMUL,
        "Km următoarea revizie": CONF_REVIZIE_ULEI_KM_URMATOR,
        "Data": CONF_REVIZIE_ULEI_DATA,
        "Cost (RON)": CONF_REVIZIE_ULEI_COST,
    },
    "distributie": {
        "Km ultima schimbare": CONF_DISTRIBUTIE_KM_ULTIMUL,
        "Km următoarea schimbare": CONF_DISTRIBUTIE_KM_URMATOR,
        "Data": CONF_DISTRIBUTIE_DATA,
        "Cost (RON)": CONF_DISTRIBUTIE_COST,
    },
    "anvelope": {
        "Data montare vară": CONF_ANVELOPE_VARA_DATA,
        "Data montare iarnă": CONF_ANVELOPE_IARNA_DATA,
        "Cost (RON)": CONF_ANVELOPE_COST,
    },
    "baterie": {
        "Data schimb": CONF_BATERIE_DATA_SCHIMB,
        "Cost (RON)": CONF_BATERIE_COST,
    },
    "frane": {
        "Plăcuțe – Km ultima schimbare": CONF_PLACUTE_FRANA_KM_ULTIMUL,
        "Plăcuțe – Km următoarea schimbare": CONF_PLACUTE_FRANA_KM_URMATOR,
        "Plăcuțe – Data schimbare": CONF_PLACUTE_FRANA_DATA,
        "Plăcuțe – Cost (RON)": CONF_PLACUTE_FRANA_COST,
        "Discuri – Km ultima schimbare": CONF_DISCURI_FRANA_KM_ULTIMUL,
        "Discuri – Km următoarea schimbare": CONF_DISCURI_FRANA_KM_URMATOR,
        "Discuri – Data schimbare": CONF_DISCURI_FRANA_DATA,
        "Discuri – Cost (RON)": CONF_DISCURI_FRANA_COST,
    },
}


# ─────────────────────────────────────────────
# Structura categoriilor (export / diagnostics)
# ─────────────────────────────────────────────
# Două tipuri de categorii:
# - categorie plată: (nume, [(cheie_json, constanta), ...])
# - categorie cu subcategorii: (nume, {sub: [(cheie_json, constanta), ...]})
#
# Folosit de:
# - __init__.py: export/import JSON structurat
# - diagnostics.py: diagnostic structurat pe categorii
STRUCTURA_CATEGORII: Final = [
    ("identificare", [
        ("marca", CONF_MARCA),
        ("model", CONF_MODEL),
        ("vin", CONF_VIN),
        ("serie_civ", CONF_SERIE_CIV),
        ("an_fabricatie", CONF_AN_FABRICATIE),
        ("an_prima_inmatriculare", CONF_AN_PRIMA_INMATRICULARE),
        ("motorizare", CONF_MOTORIZARE),
        ("combustibil", CONF_COMBUSTIBIL),
        ("capacitate_cilindrica", CONF_CAPACITATE_CILINDRICA),
        ("putere_kw", CONF_PUTERE_KW),
        ("putere_cp", CONF_PUTERE_CP),
    ]),
    ("kilometraj", [
        ("km_curent", CONF_KM_CURENT),
    ]),
    ("asigurari", {
        "rca": [
            ("numar_polita", CONF_RCA_NUMAR_POLITA),
            ("companie", CONF_RCA_COMPANIE),
            ("data_emitere", CONF_RCA_DATA_EMITERE),
            ("data_expirare", CONF_RCA_DATA_EXPIRARE),
            ("cost", CONF_RCA_COST),
        ],
        "casco": [
            ("numar_polita", CONF_CASCO_NUMAR_POLITA),
            ("companie", CONF_CASCO_COMPANIE),
            ("data_emitere", CONF_CASCO_DATA_EMITERE),
            ("data_expirare", CONF_CASCO_DATA_EXPIRARE),
            ("cost", CONF_CASCO_COST),
        ],
    }),
    ("documente", {
        "itp": [
            ("data_expirare", CONF_ITP_DATA_EXPIRARE),
            ("statie", CONF_ITP_STATIE),
            ("kilometraj", CONF_ITP_KILOMETRAJ),
        ],
        "rovinieta": [
            ("data_inceput", CONF_ROVINIETA_DATA_INCEPUT),
            ("data_sfarsit", CONF_ROVINIETA_DATA_SFARSIT),
            ("categorie", CONF_ROVINIETA_CATEGORIE),
            ("pret", CONF_ROVINIETA_PRET),
        ],
    }),
    ("administrativ", [
        ("proprietar", CONF_PROPRIETAR),
        ("tip_proprietate", CONF_TIP_PROPRIETATE),
        ("impozit_suma", CONF_IMPOZIT_SUMA),
        ("impozit_scadenta", CONF_IMPOZIT_SCADENTA),
        ("impozit_localitate", CONF_IMPOZIT_LOCALITATE),
        ("leasing_data_expirare", CONF_LEASING_DATA_EXPIRARE),
    ]),
    ("mentenanta", {
        "revizie_ulei": [
            ("km_ultimul", CONF_REVIZIE_ULEI_KM_ULTIMUL),
            ("km_urmator", CONF_REVIZIE_ULEI_KM_URMATOR),
            ("data", CONF_REVIZIE_ULEI_DATA),
            ("cost", CONF_REVIZIE_ULEI_COST),
        ],
        "distributie": [
            ("km_ultimul", CONF_DISTRIBUTIE_KM_ULTIMUL),
            ("km_urmator", CONF_DISTRIBUTIE_KM_URMATOR),
            ("data", CONF_DISTRIBUTIE_DATA),
            ("cost", CONF_DISTRIBUTIE_COST),
        ],
        "anvelope": [
            ("data_vara", CONF_ANVELOPE_VARA_DATA),
            ("data_iarna", CONF_ANVELOPE_IARNA_DATA),
            ("cost", CONF_ANVELOPE_COST),
        ],
        "baterie": [
            ("data_schimb", CONF_BATERIE_DATA_SCHIMB),
            ("cost", CONF_BATERIE_COST),
        ],
        "frane": [
            ("placute_km_ultimul", CONF_PLACUTE_FRANA_KM_ULTIMUL),
            ("placute_km_urmator", CONF_PLACUTE_FRANA_KM_URMATOR),
            ("placute_data", CONF_PLACUTE_FRANA_DATA),
            ("placute_cost", CONF_PLACUTE_FRANA_COST),
            ("discuri_km_ultimul", CONF_DISCURI_FRANA_KM_ULTIMUL),
            ("discuri_km_urmator", CONF_DISCURI_FRANA_KM_URMATOR),
            ("discuri_data", CONF_DISCURI_FRANA_DATA),
            ("discuri_cost", CONF_DISCURI_FRANA_COST),
        ],
    }),
    ("echipament", {
        "trusa_prim_ajutor": [
            ("data_expirare", CONF_TRUSA_PRIM_AJUTOR_DATA_EXPIRARE),
        ],
        "extinctor": [
            ("data_expirare", CONF_EXTINCTOR_DATA_EXPIRARE),
        ],
    }),
]


# ─────────────────────────────────────────────
# Licențiere
# ─────────────────────────────────────────────
CONF_LICENSE_KEY: Final = "license_key"
LICENSE_DATA_KEY: Final = "vehicule_license_manager"


def normalizeaza_numar(numar: str) -> str:
    """Normalizează numărul de înmatriculare pentru utilizare în ID-uri.

    Numărul trebuie introdus fără spații, cratime sau underscore (ex: B123ABC).
    Exemplu: 'B123ABC' -> 'b123abc'
    """
    return numar.strip().lower()
