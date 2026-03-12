# Vehicule - Integrare Home Assistant Personalizată

Integrare Home Assistant pentru gestionarea și urmărirea vehiculelor personale. Stochează date despre identificarea vehiculului, asigurări, inspecții și informații de întreținere direct în Home Assistant.

**Depozitul oficial:** https://github.com/cnecrea/vehicule

## Cerințe preliminare

- Home Assistant versiune **2025.11.0 sau mai nouă**
- **Nu este necesară conexiunea la internet** - integrarea funcționează 100% local
- **HACS** (opțional, pentru instalare simplificată)
- Acces administrative în Home Assistant

## Instalare

### Metoda 1: Prin HACS (Recomandată)

1. Deschideți **HACS** în interfața Home Assistant
2. Accesați **Integrări personalizate** (Custom Repositories)
3. Adăugați un nou depozit custom:
   - **URL:** `https://github.com/cnecrea/vehicule`
   - **Categorie:** Integration
   - **Apăsați "Creare"**
4. După adăugare, căutați **"Vehicule"** în HACS
5. Accesați integrarea și apăsați **"Descărcare"**
6. Selectați versiunea dorită și apăsați **"Descărcare"**
7. **Reporniți Home Assistant:**
   - **Setări** → **Sistem** → **Repornire** (în dreapta sus)
   - Sau: **Developeri** → **Servicii** → `homeassistant.restart`

### Metoda 2: Manual

1. Descărcați cel mai recent release de la: https://github.com/cnecrea/vehicule/releases
2. Extrageți fișierul descărcat
3. Copiați dosarul `vehicule` din `custom_components/` în directorul `config/custom_components/` al Home Assistant
   - Calea finală: `<HA_CONFIG_DIR>/custom_components/vehicule/`
4. **Reporniți Home Assistant** (apasă Repornire din Setări → Sistem)

## Configurare inițială

După instalare și repornire:

1. Accesați **Setări** → **Dispozitive și servicii**
2. În dreapta sus, apăsați **Crea integrare**
3. Căutați și selectați **"Vehicule"**
4. În fereastra de dialog:
   - Introduceți **placa de înmatriculare** a vehiculului (ex: `AB 123 CD`)
   - Apăsați **Creare**
5. Integrarea este acum adăugată și gata pentru configurare

## Editarea datelor vehiculului

Toate datele sunt stocate și gestionate prin intermediul meniului de opțiuni:

1. Accesați **Setări** → **Dispozitive și servicii**
2. Sub **Integrări**, localizați intrarea **"Vehicule"**
3. Apăsați pe intrare pentru a deschide detaliile dispozitivului
4. Apăsați butonul **"Configurare"** (pictograma cu roată dințată)

### Meniuri disponibile

#### 1. Identificare
Informații de bază despre vehicul:
- **Marcă și model:** Marca și modelul vehiculului (ex: Dacia Duster)
- **Anul fabricației:** An pe 4 cifre (ex: 2018)
- **Număr VIN:** Identificatorul unic al vehiculului
- **Km inițiali:** Kilometrajul la momentul adăugării vehiculului

#### 2. RCA
Informații despre asigurarea de răspundere civilă:
- **Data expirării:** Data până la care asigurarea este valabilă
- **Agent asigurare:** Numele agentului sau companiei de asigurări
- **Număr poliță:** Numărul unic al poliței de asigurare

#### 3. ITP
Informații despre inspecția tehnică periodică:
- **Data expirării:** Data până la care ITP este valabil
- **Stație ITP:** Locul unde a fost efectuată inspectia

#### 4. Administrativ
Alte informații administrative:
- **Certificat de înregistrare:** Data certificatului
- **Taxa locală:** Valoarea și date ale taxei locale
- **Alte documente:** Orice alte documente relevante și datele lor

#### 5. Mentenanță
Urmărirea lucrărilor de mentenanță și reparații:
- **Submeniu:** Selectați tipul de mentenanță din listă
  - Schimbare ulei
  - Schimbare filtru aer
  - Schimbare anvelope
  - Curățare radiator
  - Alte lucrări
- Pentru fiecare tip:
  - **Data ultimei mentenanțe:** Când a fost efectuată ultima dată
  - **Prețul:** Costul lucrării
  - **Observații:** Notări suplimentare

#### 6. Kilometraj
Informații actualizate privind kilometrajul:
- **Kilometrajul curent:** Km actuali ai vehiculului

### Format date

Toate datele de tip dată se introduc în format **ZZ.LL.AAAA**, unde:
- **ZZ** = ziua (01-31)
- **LL** = luna (01-12)
- **AAAA** = anul (4 cifre)

**Exemplu:** 18.04.2026 (18 aprilie 2026)

### Validare și păstrare

- Toate câmpurile cu an sunt validate pe server-side pentru a asigura corectitudinea
- **Golirea unui câmp:** Ștergerea conținutului unui câmp și salvarea înlătură acea informație din storage
- Modificările sunt salvate imediat după apăsarea butonului **"Salvare"**

## Senzori creați

Pentru fiecare vehicul adăugat, integrarea creează până la 12 senzori potențiali:

### Senzori de dată

| Senzor | Descriere | Entitate | Condiție vizibilitate |
|--------|-----------|----------|----------------------|
| **RCA Expirare** | Data expirării asigurării RCA | `sensor.<id>_rca_expirare` | Dacă data RCA este setată |
| **ITP Expirare** | Data expirării ITP | `sensor.<id>_itp_expirare` | Dacă data ITP este setată |
| **Certificat Înregistrare** | Data certificatului de înregistrare | `sensor.<id>_cert_inreg` | Dacă data este setată |
| **Taxa Locală** | Data taxei locale | `sensor.<id>_taxa_locala` | Dacă data este setată |
| **Mentenanță** | Data ultimei mentenanțe (pe fiecare tip) | `sensor.<id>_maint_<tip>` | Dacă data este setată |

### Senzori de valoare

| Senzor | Descriere | Entitate | Condiție vizibilitate |
|--------|-----------|----------|----------------------|
| **Kilometraj** | Kilometrajul curent | `sensor.<id>_km` | Întotdeauna vizibil |
| **Cost Mentenanță** | Costul ultimei mentenanțe (per tip) | `sensor.<id>_maint_cost_<tip>` | Dacă costul este setat |

Senzori care nu au valori setate nu apar în interfață.

## Serviciul vehicule.actualizeaza_date

Puteți actualiza datele vehiculului prin apelarea serviciului `vehicule.actualizeaza_date`:

### Utilizare

```yaml
service: vehicule.actualizeaza_date
data:
  placa_inmatriculare: "AB 123 CD"
  kilometraj: 50000
  data_rca: "18.04.2026"
  data_itp: "15.06.2027"
```

### Parametri disponibili

| Parametru | Tip | Descriere | Exemplu |
|-----------|-----|-----------|---------|
| `placa_inmatriculare` | string | **Obligatoriu** - Placa vehiculului | `AB 123 CD` |
| `kilometraj` | integer | Kilometrajul curent | `50000` |
| `data_rca` | string | Data expirării RCA (ZZ.LL.AAAA) | `18.04.2026` |
| `data_itp` | string | Data expirării ITP (ZZ.LL.AAAA) | `15.06.2027` |
| `data_cert_inreg` | string | Data certificatului (ZZ.LL.AAAA) | `10.01.2020` |
| `data_taxa_locala` | string | Data taxei locale (ZZ.LL.AAAA) | `15.12.2026` |
| `maint_<tip>` | string | Data mentenanței (ZZ.LL.AAAA) | `18.03.2026` |
| `maint_cost_<tip>` | float | Cost mentenanță | `150.50` |

### Exemplu - Automație

```yaml
automation:
  - alias: "Actualizare kilometraj lunar"
    trigger:
      platform: time
      at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: vehicule.actualizeaza_date
        data:
          placa_inmatriculare: "AB 123 CD"
          kilometraj: 51000
```

## Carduri Lovelace

### Card simplu cu entități

```yaml
type: entities
title: Vehicul - Status
entities:
  - sensor.ab_123_cd_km
  - sensor.ab_123_cd_rca_expirare
  - sensor.ab_123_cd_itp_expirare
  - sensor.ab_123_cd_taxa_locala
```

### Card cu informații detaliate

```yaml
type: custom:auto-entities
filter:
  include:
    - entity_id: "sensor.ab_123_cd*"
title: Vehicul - Toate informațiile
```

### Card cu avertismente

```yaml
type: conditional
conditions:
  - entity: sensor.ab_123_cd_rca_expirare
    state_not: "unavailable"
card:
  type: entities
  title: "⚠️ Documente care expiră în curând"
  entities:
    - sensor.ab_123_cd_rca_expirare
    - sensor.ab_123_cd_itp_expirare
```

## Verificare după instalare

După instalare și configurare inițială, efectuați aceste verificări:

### 1. Verificare dispozitiv

1. Accesați **Setări** → **Dispozitive și servicii** → **Dispozitive**
2. Căutați dispozitivul cu placa vehiculului
3. Verificați că sunt listate corect

### 2. Verificare senzori

1. Accesați **Setări** → **Dispozitive și servicii** → **Entități**
2. Filtrați după `sensor.` și placa vehiculului
3. Verificați că apar senzori pentru datele completate

### 3. Verificare jurnale

1. Accesați **Setări** → **Sistemul** → **Jurnale**
2. Filtrați după `vehicule`
3. Verificați că nu sunt erori sau avertismente

### 4. Test serviciu

1. Accesați **Setări** → **Sisteme** → **Servicii**
2. Selectați domeniu: `vehicule`
3. Selectați serviciu: `actualizeaza_date`
4. Completați parametrul `placa_inmatriculare` și apăsați **Execută**
5. Verificați în jurnale că serviciul s-a executat cu succes

## Dezinstalare

### Prin HACS

1. Deschideți **HACS** → **Integrări personalizate**
2. Localizați **"Vehicule"**
3. Apăsați pe ea și selectați **"Dezinstalare"**
4. Confirmați
5. **Reporniți Home Assistant**

### Manual

1. Ștergeți dosarul `vehicule` din `config/custom_components/`
2. **Reporniți Home Assistant**
3. În **Setări** → **Dispozitive și servicii**, ștergeți integrarea Vehicule dacă apare

## Suport și raportare erori

Pentru probleme, sugestii sau raportare de bug-uri, vizitați:

**GitHub:** https://github.com/cnecrea/vehicule

---

**Versiune:** 1.0.0
**Compatibilitate:** Home Assistant 2025.11.0+
**Licență:** RO (România)
