# Vehicule — Integrare Home Assistant

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.11%2B-41BDF5?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/cnecrea/vehicule)](https://github.com/cnecrea/vehicule/releases)
[![GitHub Stars](https://img.shields.io/github/stars/cnecrea/vehicule?style=flat&logo=github)](https://github.com/cnecrea/vehicule/stargazers)
[![Instalări](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cnecrea/vehicule/main/statistici/shields/descarcari.json)](https://github.com/cnecrea/vehicule)
[![Ultima versiune](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cnecrea/vehicule/main/statistici/shields/ultima_release.json)](https://github.com/cnecrea/vehicule/releases/latest)


Integrare custom pentru [Home Assistant](https://www.home-assistant.io/) care permite **gestionarea vehiculelor și documentelor** acestora — asigurări, taxe, revizii, anvelope, frâne, baterie, trusă de prim ajutor și extinctor — direct din interfața HA.

Fără dependențe externe, fără API-uri, fără conexiune la internet. Totul rulează local.

---

## Ce face integrarea

- **Vehicule multiple**: adaugă un număr nelimitat de vehicule, fiecare identificat prin placa de înmatriculare
- **Documente cu termen**: RCA, Casco, ITP, rovinieta, impozit, leasing — cu calculul automat al zilelor rămase
- **Mentenanță**: revizie ulei, distribuție, anvelope, baterie, plăcuțe și discuri de frână — cu calculul km rămași
- **Echipament obligatoriu**: trusă de prim ajutor, extinctor — cu avertizare la expirare
- **Costuri mentenanță**: câmpuri de cost la toate categoriile de mentenanță
- **Istoric cu confirmare**: la reînnoirea unui document sau mentenanță, datele vechi pot fi arhivate (cu bifa explicită din formular)
- **Senzor cost total pe ani**: costul anului curent cu defalcare pe categorii și totaluri pe ani anteriori (curente + arhivate)
- **Senzori condiționați**: apar doar când au date completate (nu aglomererază dashboard-ul)
- **Curățare automată**: la schimbarea condițiilor (ex: treci de la leasing la proprietate), entitățile orfane sunt eliminate automat
- **Date în format românesc**: ZZ.LL.AAAA în interfață, ISO intern
- **Verificare km obligatoriu**: ITP, revizie ulei, distribuție și frâne necesită setarea prealabilă a kilometrajului curent
- **Leasing dinamic**: la prima selectare a tipului „Leasing", apare automat un pas suplimentar pentru data de expirare
- **Serviciu actualizare**: `vehicule.actualizeaza_date` pentru automatizarea km-ului
- **Backup / Restore**: servicii `vehicule.exporta_date` și `vehicule.importa_date` pentru export/import JSON (ideal pentru flote)
- **Traduceri complete**: Română (ro.json) + Engleză (en.json + strings.json)

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
├── Asigurare Casco
├── Inspecție tehnică (ITP)
├── Rovinieta
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

Pentru fiecare vehicul, integrarea creează până la **17 senzori**. Aceștia apar condiționat — doar dacă au date completate.

Entity ID-urile urmează formatul: `sensor.vehicule_{nr_normalizat}_{tip_senzor}`

Unde `{nr_normalizat}` este numărul de înmatriculare normalizat (litere mici). De exemplu, pentru placa `B123ABC`, entity ID-urile ar fi `sensor.vehicule_b123abc_informatii`, `sensor.vehicule_b123abc_rca`, etc.

### Tabel senzori

| Senzor | Cheie | Unitate | Vizibil când... | Valoare |
|--------|-------|---------|-----------------|---------|
| Informații | `informatii` | — | Mereu | Marcă + Model (sau nr. înmatriculare) |
| Kilometraj | `kilometraj` | km | `km_curent` completat | Km curent |
| RCA | `rca` | zile | `rca_data_expirare` completat | Zile rămase până la expirare |
| Casco | `casco` | zile | `casco_data_expirare` completat | Zile rămase până la expirare |
| ITP | `itp` | zile | `itp_data_expirare` completat | Zile rămase până la expirare |
| Rovinieta | `rovinieta` | zile | `rovinieta_data_sfarsit` completat | Zile rămase până la expirare |
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
| Cost total | `cost_total` | RON | Cel puțin un cost completat | Costul total al anului curent |

### Atribute senzori

Fiecare senzor expune atribute suplimentare. Câteva exemple:

**RCA** — atribute: Număr poliță, Companie, Data emitere, Data expirare, Cost (RON), Stare (Valid/Expirat)

**Casco** — atribute: Număr poliță, Companie, Data emitere, Data expirare, Cost (RON), Stare (Valid/Expirat)

**ITP** — atribute: Data expirare, Stație, Kilometraj la ITP, Stare (Valid/Expirat)

**Rovinieta** — atribute: Data început, Data sfârșit, Categorie, Preț (RON), Stare (Valid/Expirat)

**Impozit** — atribute: Sumă (RON), Scadență, Localitate, Proprietar, Tip proprietate

**Revizie ulei** — atribute: Km ultima revizie, Km următoarea revizie, Data ultima revizie, Cost (RON), Km curent

**Anvelope** — atribute: Data montare vară, Data montare iarnă, Cost (RON), Sezon recomandat

**Trusă prim ajutor** — atribute: Data expirare, Stare (Valid/Expirat)

**Extinctor** — atribute: Data expirare, Stare (Valid/Expirat)

**Cost total** — atribute: Asigurări {an} (RON), Taxe {an} (RON), Mentenanță {an} (RON), Total {an-1} (RON), Total {an-2} (RON), Total general (RON). Costurile sunt atribuite anului din data lor de referință. Totalurile per an includ și costurile arhivate.

> **Istoric per senzor**: Senzorii arhivabili (RCA, Casco, ITP, Rovinieta, Revizie ulei, Distribuție, Anvelope, Baterie, Plăcuțe frână, Discuri frână) afișează în atribute și detaliile ultimei reînnoiri anterioare (Reînnoiri anterioare, Ultima arhivare, câmpurile anterioare cu prefix „Anterior – ", Cost total anterior)

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
action: vehicule.actualizeaza_date
data:
  nr_inmatriculare: "B123ABC"
  km_curent: 85000
```

### vehicule.exporta_date

Exportă datele unui vehicul într-un fișier JSON în directorul `/config/`.

| Parametru | Tip | Obligatoriu | Descriere |
|-----------|-----|-------------|-----------|
| `nr_inmatriculare` | string | Da | Numărul de înmatriculare (ex: `B123ABC`) |

**Exemplu**:
```yaml
action: vehicule.exporta_date
data:
  nr_inmatriculare: "B123ABC"
```

Fișierul generat: `/config/vehicule_backup_b123abc.json`

### vehicule.importa_date

Importă datele unui vehicul dintr-un fișier JSON de backup. Dacă vehiculul nu există, va fi creat automat.

| Parametru | Tip | Obligatoriu | Descriere |
|-----------|-----|-------------|-----------|
| `cale_fisier` | string | Da | Calea completă către fișierul JSON (ex: `/config/vehicule_backup_b123abc.json`) |

**Exemplu**:
```yaml
action: vehicule.importa_date
data:
  cale_fisier: "/config/vehicule_backup_b123abc.json"
```

> **Notă**: La import, dacă vehiculul există deja, opțiunile sunt actualizate. Dacă nu există, este creat automat o nouă intrare.

---

## Exemple de automatizări

### Notificare documente și mentenanță

Automatizarea verifică zilnic (la ora 11:00) toți senzorii relevanți și trimite notificări pe telefon pentru documentele sau componentele care necesită atenție.

> **De ce nu `numeric_state`?** Trigger-ul `numeric_state` se activează doar la **tranziția** valorii sub prag — dacă HA a fost repornit sau senzorul era deja sub prag, notificarea nu se mai trimite. Varianta cu `time` + `repeat.for_each` verifică **efectiv** valorile în fiecare zi.

```yaml
automation:
  - alias: "Vehicul B123ABC — Notificări zilnice"
    description: "Verifică documente și mentenanță, trimite notificări pe telefon"
    triggers:
      - trigger: time
        at: "11:00:00"
    actions:
      - repeat:
          for_each:
            - entity: sensor.vehicule_b123abc_rca
              name: "RCA"
              prag: 30
              unitate: "zile"
            - entity: sensor.vehicule_b123abc_casco
              name: "Casco"
              prag: 30
              unitate: "zile"
            - entity: sensor.vehicule_b123abc_itp
              name: "ITP"
              prag: 30
              unitate: "zile"
            - entity: sensor.vehicule_b123abc_rovinieta
              name: "Rovinieta"
              prag: 30
              unitate: "zile"
            - entity: sensor.vehicule_b123abc_impozit
              name: "Impozit"
              prag: 30
              unitate: "zile"
            - entity: sensor.vehicule_b123abc_revizie_ulei
              name: "Revizie ulei"
              prag: 1000
              unitate: "km"
            - entity: sensor.vehicule_b123abc_distributie
              name: "Distribuție"
              prag: 5000
              unitate: "km"
            - entity: sensor.vehicule_b123abc_placute_frana
              name: "Plăcuțe frână"
              prag: 3000
              unitate: "km"
            - entity: sensor.vehicule_b123abc_discuri_frana
              name: "Discuri frână"
              prag: 5000
              unitate: "km"
            - entity: sensor.vehicule_b123abc_trusa_prim_ajutor
              name: "Trusă prim ajutor"
              prag: 30
              unitate: "zile"
            - entity: sensor.vehicule_b123abc_extinctor
              name: "Extinctor"
              prag: 30
              unitate: "zile"
          sequence:
            - variables:
                val: "{{ states(repeat.item.entity) }}"
            - if:
                - condition: template
                  value_template: >
                    {{ val not in ['unknown', 'unavailable'] and val | int(999) < repeat.item.prag }}
              then:
                - action: notify.mobile_app
                  data:
                    title: "⚠️ {{ repeat.item.name }} — B123ABC"
                    message: >
                      Mai ai {{ val }} {{ repeat.item.unitate }} rămase.
                      {% if repeat.item.unitate == 'zile' and val | int(0) < 0 %}
                      ⛔ EXPIRAT de {{ val | int(0) | abs }} zile!
                      {% endif %}
```

> **Notă**: Înlocuiește `notify.mobile_app` cu serviciul tău de notificare (ex: `notify.mobile_app_telefonul_meu`). Pragurile și lista de senzori se pot ajusta după preferințe.

### Actualizare kilometraj din senzor GPS

```yaml
automation:
  - alias: "Actualizare km din OBD/GPS"
    triggers:
      - trigger: time_pattern
        hours: "/1"
    actions:
      - action: vehicule.actualizeaza_date
        data:
          nr_inmatriculare: "B123ABC"
          km_curent: "{{ states('sensor.obd_odometer') | int(0) }}"
```

---

## Carduri Lovelace

Integrarea vine cu un design profesional de dashboard — culori condiționate (verde / portocaliu / roșu), icoane per categorie și layout responsive.

Există două metode de configurare:

### Varianta 1 — Vehicule Card (recomandat)

[**Vehicule Card**](https://github.com/cnecrea/vehicule-card) este un card custom care generează automat întregul dashboard cu o singură linie de configurare. Detectează vehiculele, afișează doar secțiunile cu date completate și ascunde automat ce nu este relevant (ex: dacă nu ai leasing, cardul de leasing nu apare).

```yaml
type: custom:vehicule-card
```

Instalare din HACS → Frontend → Custom repository: `cnecrea/vehicule-card`

Detalii complete, parametri și cerințe: [github.com/cnecrea/vehicule-card](https://github.com/cnecrea/vehicule-card)

### Varianta 2 — Configurare manuală YAML

Pentru control total asupra layout-ului, poți copia configurațiile YAML secțiune cu secțiune din [**LOVELACE.md**](LOVELACE.md). Această variantă necesită editare manuală și înlocuirea prefixului vehiculului în fiecare entity ID.

Ambele variante folosesc același set de carduri custom (button-card, stack-in-card, bubble-card, card-mod, mini-graph-card) și produc același rezultat vizual.

---

## Diagnostics

Integrarea suportă exportarea datelor de diagnostic prin mecanismul standard HA:

1. **Settings** → **Devices & Services** → click pe vehicul
2. Click pe cele 3 puncte (⋮) → **Download diagnostics**

Datele sunt structurate pe categorii (identificare, kilometraj, rca, casco, itp, rovinieta, administrativ, revizie_ulei, distributie, anvelope, baterie, frane, echipament_obligatoriu), cu secțiune separată pentru istoric și lista senzorilor activi.

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
├── strings.json         # Traduceri en (sursă)
├── hacs.json            # Configurație HACS
└── translations/
    ├── en.json          # Traduceri limba engleză
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
2. **Fără imagini vehicul** — nu există suport pentru fotografii sau avatare per vehicul

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
