# Vehicule — Integrare Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/cnecrea/vehicule)](https://github.com/cnecrea/vehicule/releases)
![Total descărcări pentru toate versiunile](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cnecrea/vehicule/main/statistici/shields/descarcari.json)
![Descărcări pentru ultima versiune](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cnecrea/vehicule/main/statistici/shields/ultima_release.json)

Integrare custom pentru [Home Assistant](https://www.home-assistant.io/) care permite **gestionarea vehiculelor și documentelor** acestora — asigurări, taxe, revizii, anvelope, frâne, baterie — direct din interfața HA.

Fără dependențe externe, fără API-uri, fără conexiune la internet. Totul rulează local.

---

## Ce face integrarea

- **Vehicule multiple**: adaugă un număr nelimitat de vehicule, fiecare identificat prin placa de înmatriculare
- **Documente cu termen**: RCA, ITP, impozit, leasing — cu calculul automat al zilelor rămase
- **Mentenanță**: revizie ulei, distribuție, anvelope, baterie, plăcuțe și discuri de frână — cu calculul km rămași
- **Echipament obligatoriu**: trusă de prim ajutor, extinctor — cu avertizare la expirare
- **Senzori condiționați**: apar doar când au date completate (nu aglomererază dashboard-ul)
- **Curățare automată**: la schimbarea condițiilor (ex: treci de la leasing la proprietate), entitățile orfane sunt eliminate automat
- **Date în format românesc**: ZZ.LL.AAAA în interfață, ISO intern
- **Serviciu actualizare**: `vehicule.actualizeaza_date` pentru automatizarea km-ului

---

## Instalare

### HACS (recomandat)

1. Deschide HACS în Home Assistant
2. Click pe cele 3 puncte (⋮) din colțul dreapta sus → **Custom repositories**
3. Adaugă URL-ul: `https://github.com/cnecrea/vehicule`
4. Categorie: **Integration**
5. Click **Add** → găsește „Vehicule" → **Install**
6. Restartează Home Assistant

### Manual

1. Copiază folderul `custom_components/vehicule/` în directorul `config/custom_components/` din Home Assistant
2. Restartează Home Assistant

---

## Configurare

### Pasul 1 — Adaugă un vehicul

1. **Settings** → **Devices & Services** → **Add Integration**
2. Caută „**Vehicule**"
3. Introdu numărul de înmatriculare, fără spații (ex: `B123ABC`)
4. Click **Submit**

Integrarea creează un device cu un singur senzor (Informații). Restul senzorilor apar pe măsură ce completezi date.

### Pasul 2 — Completează datele vehiculului

1. **Settings** → **Devices & Services** → click pe intrarea vehiculului
2. Click pe **Configure** (⚙️)
3. Alege categoria dorită din meniu:

```
Gestionare vehicul
├── Date de identificare
├── Asigurare RCA
├── Inspecție tehnică (ITP)
├── Date administrative / fiscale
├── Mentenanță
│   ├── Revizie ulei
│   ├── Distribuție
│   ├── Anvelope
│   ├── Baterie
│   ├── Frâne (plăcuțe și discuri)
│   ├── Trusă de prim ajutor
│   └── Extinctor
└── Actualizare kilometraj
```

Datele calendaristice se introduc în format **ZZ.LL.AAAA** (ex: `18.04.2026`). Câmpurile de an acceptă valori cu 4 cifre, validate server-side.

---

## Entități create

Pentru fiecare vehicul, integrarea creează până la **14 senzori**. Aceștia apar condiționat — doar dacă au date completate.

Entity ID-urile urmează formatul: `sensor.vehicule_{nr_normalizat}_{tip_senzor}`

Unde `{nr_normalizat}` este numărul de înmatriculare normalizat (litere mici). De exemplu, pentru placa `B123ABC`, entity ID-urile ar fi `sensor.vehicule_b123abc_informatii`, `sensor.vehicule_b123abc_rca`, etc.

### Tabel senzori

| Senzor | Cheie | Unitate | Vizibil când... | Valoare |
|--------|-------|---------|-----------------|---------|
| Informații | `informatii` | — | Mereu | Marcă + Model (sau nr. înmatriculare) |
| Kilometraj | `kilometraj` | km | `km_curent` completat | Km curent |
| RCA | `rca` | zile | `rca_data_expirare` completat | Zile rămase până la expirare |
| ITP | `itp` | zile | `itp_data_expirare` completat | Zile rămase până la expirare |
| Impozit | `impozit` | zile | `impozit_scadenta` completat | Zile rămase până la scadență |
| Leasing | `leasing` | zile | `tip_proprietate` = leasing | Zile rămase până la expirare |
| Revizie ulei | `revizie_ulei` | km | `revizie_ulei_km_urmator` completat | Km rămași până la revizie |
| Distribuție | `distributie` | km | `distributie_km_urmator` completat | Km rămași până la schimbare |
| Anvelope | `anvelope` | — | Cel puțin o dată de montare | Sezonul curent (Vară / Iarnă) |
| Baterie | `baterie` | luni | `baterie_data_schimb` completat | Luni de la ultimul schimb |
| Plăcuțe frână | `placute_frana` | km | `placute_frana_km_urmator` completat | Km rămași |
| Discuri frână | `discuri_frana` | km | `discuri_frana_km_urmator` completat | Km rămași |
| Trusă prim ajutor | `trusa_prim_ajutor` | zile | `trusa_prim_ajutor_data_expirare` completat | Zile rămase până la expirare |
| Extinctor | `extinctor` | zile | `extinctor_data_expirare` completat | Zile rămase până la expirare |

### Atribute senzori

Fiecare senzor expune atribute suplimentare. Câteva exemple:

**RCA** — atribute: Număr poliță, Companie, Data emitere, Data expirare, Cost (RON), Stare (Valid/Expirat)

**ITP** — atribute: Data expirare, Stație, Kilometraj la ITP, Stare (Valid/Expirat)

**Impozit** — atribute: Sumă (RON), Scadență, Localitate, Proprietar, Tip proprietate

**Revizie ulei** — atribute: Km ultima revizie, Km următoarea revizie, Data ultima revizie, Km curent

**Anvelope** — atribute: Data montare vară, Data montare iarnă, Sezon recomandat

**Trusă prim ajutor** — atribute: Data expirare, Stare (Valid/Expirat)

**Extinctor** — atribute: Data expirare, Stare (Valid/Expirat)

Datele din atribute sunt afișate în format românesc (ZZ.LL.AAAA), iar valorile numerice sunt afișate ca numere întregi (fără zecimale).

---

## Servicii

### vehicule.actualizeaza_date

Actualizează kilometrajul curent al unui vehicul.

| Parametru | Tip | Obligatoriu | Descriere |
|-----------|-----|-------------|-----------|
| `nr_inmatriculare` | string | Da | Numărul de înmatriculare (ex: `B123ABC`) |
| `km_curent` | int | Da | Kilometrajul actual (0–9.999.999) |

**Exemplu**:
```yaml
service: vehicule.actualizeaza_date
data:
  nr_inmatriculare: "B123ABC"
  km_curent: 85000
```

---

## Exemple de automatizări

### Notificare RCA la expirare

```yaml
automation:
  - alias: "RCA - Expirare apropiată"
    trigger:
      platform: numeric_state
      entity_id: sensor.vehicule_b123abc_rca
      below: 30
    action:
      service: notify.mobile_app
      data:
        message: "RCA-ul va expira în {{ states('sensor.vehicule_b123abc_rca') }} zile!"
        title: "Atenție: Asigurare RCA"
```

### Notificare revizie ulei

```yaml
automation:
  - alias: "Revizie ulei - Km apropiați"
    trigger:
      platform: numeric_state
      entity_id: sensor.vehicule_b123abc_revizie_ulei
      below: 1000
    action:
      service: notify.mobile_app
      data:
        message: "Revizia uleiului e datorată în {{ states('sensor.vehicule_b123abc_revizie_ulei') }} km"
        title: "Atenție: Revizie ulei"
```

### Card Lovelace

```yaml
type: entities
title: Vehicul B123ABC
entities:
  - entity: sensor.vehicule_b123abc_informatii
  - entity: sensor.vehicule_b123abc_kilometraj
  - entity: sensor.vehicule_b123abc_rca
  - entity: sensor.vehicule_b123abc_itp
  - entity: sensor.vehicule_b123abc_impozit
  - entity: sensor.vehicule_b123abc_revizie_ulei
```

---

## Diagnostics

Integrarea suportă exportarea datelor de diagnostic prin mecanismul standard HA:

1. **Settings** → **Devices & Services** → click pe vehicul
2. Click pe cele 3 puncte (⋮) → **Download diagnostics**

Informațiile sensibile (VIN, serie CIV, nr. înmatriculare, nr. poliță, proprietar) sunt mascate automat.

---

## Structura fișierelor

```
custom_components/vehicule/
├── __init__.py          # Setup/unload integrare, servicii
├── config_flow.py       # ConfigFlow + OptionsFlow cu meniuri categorisate
├── const.py             # Constante, liste opțiuni, normalizeaza_numar()
├── diagnostics.py       # Export diagnostics cu mascare date sensibile
├── helpers.py           # Funcții comune (conversii date, validări, calcule)
├── manifest.json        # Metadata integrare
├── sensor.py            # Senzori condiționați per vehicul
├── services.yaml        # Definiții servicii
├── strings.json         # Traduceri (sursă)
├── hacs.json            # Configurație HACS
└── translations/
    └── ro.json          # Traduceri limba română
```

---

## Cerințe

- **Home Assistant** 2025.11.0 sau mai nou
- **HACS** (opțional, pentru instalare ușoară)
- Fără dependențe externe, fără conexiune la internet

---

## Limitări cunoscute

1. **Datele sunt locale** — stocate în configurația HA, nu sunt sincronizate cu alte sisteme
2. **Fără import/export CSV** — momentan nu se pot importa sau exporta date în masă
3. **Fără istoric costuri** — costurile și datele de mentenanță nu sunt arhivate istoric
4. **Fără imagini vehicul** — nu există suport pentru fotografii sau avatare per vehicul

---

## ☕ Susține dezvoltatorul

Dacă ți-a plăcut această integrare și vrei să sprijini munca depusă, **invită-mă la o cafea**! 🫶
Nu costă nimic, iar contribuția ta ajută la dezvoltarea viitoare a proiectului. 🙌

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Susține%20dezvoltatorul-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/cnecrea)

Mulțumesc pentru sprijin și apreciez fiecare gest de susținere! 🤗

---

## 🧑‍💻 Contribuții

Contribuțiile sunt binevenite! Simte-te liber să trimiți un pull request sau să raportezi probleme [aici](https://github.com/cnecrea/vehicule/issues).

---

## 🌟 Suport
Dacă îți place această integrare, oferă-i un ⭐ pe [GitHub](https://github.com/cnecrea/vehicule/)! 😊
