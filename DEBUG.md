# Debugging - Integrarea Vehicule

Acest ghid te ajută să activezi și să interpretezi log-urile pentru integrarea **vehicule**.

## Activează debug logging

Pentru a vedea mesajele de debug din integrarea vehicule, adaugă următoarea configurație în `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.vehicule: debug
```

După ce salvezi și reîncarci configurația (Settings → System → Restart), logurile de debug vor fi disponibile.

---

## Unde găsești logurile

### Prin interfața Home Assistant
1. Settings → System → Logs
2. Caută mesaje care conțin `vehicule`
3. Poți copia logurile direct din panou

### Fișierul de log
Logurile sunt salvate în fișierul principal:
- `<config_dir>/home-assistant.log`

### Terminal (dacă rulezi în Docker/Supervised)
```bash
docker logs homeassistant 2>&1 | grep vehicule
# sau
tail -f <config_dir>/home-assistant.log | grep vehicule
```

---

## Mesaje normale la pornire

Când integrarea vehicule se încarcă pentru prima dată sau după o repornire, vei vedea:

```
[custom_components.vehicule] Configurez vehiculul: B123ABC
[custom_components.vehicule.sensor] Creez senzorii pentru vehiculul: B123ABC
[custom_components.vehicule.sensor] Vehicul B123ABC: 5 senzori creați (din 17 posibili)
[custom_components.vehicule] Serviciul vehicule.actualizeaza_date a fost înregistrat
[custom_components.vehicule] Serviciul vehicule.exporta_date a fost înregistrat
[custom_components.vehicule] Serviciul vehicule.importa_date a fost înregistrat
```

**Explicație:**
- `Configurez vehiculul: B123ABC` – Integrarea a inițializat vehiculul cu numărul de înmatriculare
- `Creez senzorii...` – Se procesează entitățile care vor fi create
- `5 senzori creați (din 17 posibili)` – Doar 5 senzori sunt relevanți pentru datele tale (de ex., dacă nu ai date despre rovinieta, senzorul de rovinieta nu va fi creat)
- `Serviciul vehicule.actualizeaza_date a fost înregistrat` – Serviciul pentru actualizare manuală a datelor este disponibil
- `Serviciul vehicule.exporta_date a fost înregistrat` – Serviciul pentru export backup JSON
- `Serviciul vehicule.importa_date a fost înregistrat` – Serviciul pentru import backup JSON

---

## Situații normale

### Adăugarea/modificarea datelor vehiculului
Când actualizezi datele printr-un apel de serviciu:

```
[custom_components.vehicule] Actualizez datele pentru B123ABC – km: 45320
[custom_components.vehicule.sensor] Vehicul B123ABC: 6 senzori creați (din 17 posibili)
```

Senzori noi pot apărea când completezi date (de ex., dacă adaugi prima dată consumul, senzorul de consum va fi creat).

### Ștergerea vehiculului
Când elimini o intrare din integrare:

```
[custom_components.vehicule] Descarc vehiculul: B123ABC
[custom_components.vehicule.sensor] Elimin entitatea orfană: sensor.vehicul_b_123_abc_km (unique_id: vehicule_b123abc_km)
```

**Explicație:**
- Entitățile orfane (care nu mai au referință în configurație) sunt curățate automat
- Mesajul arată `unique_id`-ul pentru identificare

### Opțiuni actualizate
Dacă modifici setările integrării (Options flow):

```
[custom_components.vehicule] Opțiuni actualizate pentru B123ABC – reîncarc
[custom_components.vehicule.sensor] Creez senzorii pentru vehiculul: B123ABC
```

---

## Situații de eroare

### Validare invalidă în formularul de configurare

**Scenariu:** Introduci un an invalid (de ex., 1800)
```
[custom_components.vehicule.config_flow] Validare: an_invalid
```

**Ce trebuie verificat:**
- Anul vehiculului trebuie să fie între 1900 și anul curent
- Controlează datele introduse în formularul de configurare

### Format de dată invalid

**Scenariu:** Introduci o dată în format greșit
```
[custom_components.vehicule] format_data_invalid
```

**Ce trebuie verificat:**
- Formatul datei trebuie să fie `YYYY-MM-DD` (de ex., `2026-03-12`)

### Vehicul nu găsit

**Scenariu:** Încearcă să actualizezi un vehicul care nu mai există în configurație
```
[custom_components.vehicule] Nu am găsit vehiculul cu nr. B123ABC
```

**Ce trebuie verificat:**
- Verifică dacă vehiculul este încă configurat
- Poți reconecta integrarea dacă este necesar

### Erori generale

Pentru orice alte erori, logurile vor conține un traceback Python complet. Cauta mesajele de tip:
```
Traceback (most recent call last):
  File "custom_components/vehicule/...", line X, in ...
```

Acest traceback te ajută să identifici exact unde s-a întâmplat eroarea.

---

## Mesaje de la pornire

Atunci când Home Assistant pornește, secvența este:

1. **Încărcarea integrării**
   ```
   [custom_components.vehicule] Configurez vehiculul: B123ABC
   ```

2. **Crearea senzorilor**
   ```
   [custom_components.vehicule.sensor] Creez senzorii pentru vehiculul: B123ABC
   [custom_components.vehicule.sensor] Vehicul B123ABC: 5 senzori creați (din 17 posibili)
   ```

3. **Înregistrarea serviciilor**
   ```
   [custom_components.vehicule] Serviciul vehicule.actualizeaza_date a fost înregistrat
   [custom_components.vehicule] Serviciul vehicule.exporta_date a fost înregistrat
   [custom_components.vehicule] Serviciul vehicule.importa_date a fost înregistrat
   ```

După aceasta, integrarea este gata de utilizare.

---

## Diagnostics

Home Assistant oferă o modalitate standard de a exporta diagnostice pentru integrări.

### Cum exporți diagnosticele

1. **Din interfață:** Settings → System → Diagnostics
2. **Cauta** integrarea vehicule în lista
3. **Click** pe butonul de download
4. Un fișier JSON va fi descărcat pe computer

### Ce conțin diagnosticele

Fișierul JSON include:
- **Versiunea integrării**
- **Configurația vehiculului** (mascat: VIN, serie CIV, nr. înmatriculare, nr. poliță RCA, proprietar)
- **Lista senzorilor** (stări și atribute)
- **Informații despre entități** (unique_id, platform, disabled state)
- **Istoricul din ultimele zile** (dacă există)

**Informații mascate pentru confidențialitate:**
- VIN-ul vehiculului
- Seria CIV
- Numărul de înmatriculare
- Numărul poliței RCA
- Datele proprietarului

### Cum raportezi un bug cu diagnostice

Atunci când raportezi o problemă:

1. **Activează debug logging** (vezi secțiunea de mai sus)
2. **Reproduc eroarea** și lasă serverul să ruleze
3. **Exportă logurile** din Settings → System → Logs
4. **Exportă diagnosticele** din Settings → System → Diagnostics
5. **Deschide o problemă** pe GitHub: [https://github.com/cnecrea/vehicule/issues](https://github.com/cnecrea/vehicule/issues)
6. **Include:**
   - Descrierea problemei
   - Pașii pentru a reproduce
   - Fragmentele relevante din log (cu debug activ)
   - Fișierul de diagnostice

---

## Cum raportezi un bug

### Pași de bază

1. **Activează debug logging** (configurare.yaml + restart)
2. **Reproduc eroarea**
3. **Colectează logurile** din Settings → System → Logs
4. **Exportă diagnosticele** din Settings → System → Diagnostics
5. **Deschide o problemă** pe GitHub

### La raportare, include:

```
**Descriere:** [Ce s-a întâmplat?]

**Pași pentru a reproduce:**
1. [Pasul 1]
2. [Pasul 2]
3. [...]

**Loguri (debug activ):**
[Copiază fragmentele relevante din log]

**Informații despre mediu:**
- Versiunea Home Assistant: [v...]
- Versiunea integrării vehicule: [vX.Y.Z]
- Tip de instalare: [Docker/Supervised/...]
```

### Link pentru raportare

→ [GitHub Issues - vehicule](https://github.com/cnecrea/vehicule/issues/new)

---

## Note importante

- **Confidențialitate:** Logurile pot conține date personale mascate în diagnostice, dar nu și în log-urile brute. Revizuiește înainte de a partaja public.
- **Performanță:** Debug logging crește volumul de log-uri. Dezactivează după ce termini debugging.
- **Reîncărcări:** Schimbări în config.yaml necesită restart complet al Home Assistant.
