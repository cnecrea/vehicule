# Vehicule - Întrebări Frecvente (FAQ)

## 1. Generale

### Ce este integrarea Vehicule?
Vehicule este o integrare Home Assistant personalizată care vă permite să gestionați vehiculele și documentele acestora (RCA, Casco, ITP, rovinieta, asigurări, reparații, etc.) direct în Home Assistant. Puteți urmări expirarea documentelor, kilometrajul și istoricul mentenanței pentru fiecare vehicul.

### Pentru cine este aceasta integrare?
Aceasta integrare este ideală pentru:
- Proprietarii de multiple vehicule care doresc centralizarea datelor
- Persoane care doresc automatizări pentru remindere la expirarea RCA/Casco/ITP
- Utilizatori care doresc urmărirea consumului de carburant și mentenanței
- Oricine preferă să-și gestioneze datele 100% local, fără servicii cloud externe

### Este gratuită?
Da, integrarea este complet gratuită și open-source. Codul sursă este disponibil pe GitHub: https://github.com/cnecrea/vehicule

### Are nevoie de internet?
**NU.** Integrarea funcționează 100% local, pe mașina dvs. Home Assistant. Nu trimite nicio informație către servere externe. Nu are nicio dependență de API-uri externe. Datele rămân sub controlul dvs total.

### Care este clasa IoT?
Integrarea este clasificată ca `calculated` - datele sunt prelucrate local pe baza valorilor introduse de utilizator.

---

## 2. Configurare

### Cum adaug un vehicul?
1. Accesați **Settings → Devices & Services → Integrations**
2. Căutați și instalați **Vehicule** (dacă nu este deja instalată)
3. Apăsați **+ Create Entry**
4. Introduceți **numărul de înmatriculare** (plăcuța de înmatriculare)
5. Confirmare - integrarea creează automat senzorii

Fiecare vehicul = 1 config entry, identificat unic prin numărul de înmatriculare.

### Cum editez datele unui vehicul?
1. Accesați **Settings → Devices & Services → Integrations → Vehicule**
2. Selectați vehiculul pe care doriti să-l editați
3. Apăsați pe intrare
4. Apăsați butonul **⚙️ (Options)** din colțul dreapta sus
5. Completați categoriile relevante (vezi mai jos)

### Care sunt categoriile de date?
Datele sunt organizate în meniuri categorizate:

| Categorie | Descriere |
|-----------|-----------|
| **Identificare** | Marca, model, tip combustibil, cilindree, an de fabricație, an de înmatriculare, tip proprietate (proprietate/leasing) |
| **RCA** | Număr poliță, data expirării, asigurator |
| **Casco** | Număr poliță, data expirării, asigurator |
| **ITP** | Data expirării, locul testării |
| **Rovinieta** | Data început, data sfârșit, categorie, preț |
| **Administrativ** | Proprietar, tip proprietate, impozit, leasing |
| **Mentenanță** | Revizie ulei, distribuție, anvelope, baterie, frâne, trusă de prim ajutor, extinctor |
| **Kilometraj** | Kilometrajul curent (actualizat manual sau prin automatizări) |

### Cum funcționează formatele de dată?
- **Afișare:** în interfață, datele se afișează în format **ZZ.LL.AAAA** (ex: 15.03.2026)
- **Stocare internă:** datele sunt stocate în format ISO (YYYY-MM-DD)
- **Input:** introduceți datele în format ZZ.LL.AAAA

Exemplu: pentru 15 martie 2026, scrieți `15.03.2026`

### Ce se întâmplă dacă sterg o valoare dintr-un câmp?
- Câmpurile sunt opționale
- Dacă goliți un câmp, sensorul asociat **dispare** din Home Assistant
- Datele anterioare sunt șterse
- Puteți completa din nou oricând

### Cum funcționează câmpurile de an (fabricație și înmatriculare)?
- Au validare pe server
- Acceptă ani între **1900** și anul curent + 1 pentru **fabricație**
- Acceptă ani între **1900** și anul curent pentru **înmatriculare**
- Validarea previne erori de introduceți în date

### Trebuie setat kilometrajul înainte de ITP și mentenanță?
Da. Începând cu versiunea 1.1.0, pașii **ITP**, **Revizie ulei**, **Distribuție** și **Frâne** necesită ca kilometrajul curent să fie configurat. Dacă nu este setat, formularul afișează o eroare și trebuie mai întâi să accesați **Actualizare kilometraj** din meniul principal.

---

## 3. Senzori

### Ce senzori are fiecare vehicul?
Integrarea creează până la **17 senzori** pentru fiecare vehicul:
- Informații (marcă + model)
- Kilometraj
- RCA (zile rămase)
- Casco (zile rămase)
- ITP (zile rămase)
- Rovinieta (zile rămase)
- Impozit (zile rămase)
- Leasing (zile rămase)
- Revizie ulei (km rămași)
- Distribuție (km rămași)
- Anvelope (sezon curent)
- Baterie (luni de la schimb)
- Plăcuțe frână (km rămași)
- Discuri frână (km rămași)
- Trusă prim ajutor (zile rămase)
- Extinctor (zile rămase)
- Cost total (RON — suma tuturor costurilor)

### Când apare/dispare un senzor?
- Un senzor **apare** doar când datele relevante sunt completate
- Un senzor **dispare** automat când goliți (ștergeți) datele corespunzătoare
- Integrarea auto-curață entitățile orfane

### Ce arată atributul `days_remaining`?
- **Valori pozitive (ex: 45):** zilele rămase până la expirare
- **Valori negative (ex: -10):** documentul a expirat cu 10 zile în urmă
- **0:** expira astazi

Exemplu: dacă RCA expira în 15 zile, `days_remaining = 15`. Dacă a expirat acum 3 zile, `days_remaining = -3`. Același atribut se aplică și pentru Casco.

### De ce datele se afișează în format românesc?
Formatele de dată sunt adaptate la localizarea românească:
- Afișare: `15.03.2026`
- Zile prescurtate: Lun, Mar, Mie, etc.
- Luni prescurtate: Ian, Feb, Mar, etc.

---

## 4. Mentenanță

### Cum urmăresc schimbul de ulei?
1. Completați în categoria **Mentenanță → Ulei curent** data ultimului schimb (ZZ.LL.AAAA)
2. Introduceți **Interval schimb ulei (km)** (ex: 10000)
3. Integrarea creează un senzor care arată km rămași până la schimb
4. Când `km_remaining_ulei < 0`, trebuie să efectuați schimbul

### Cum urmăresc distribuitorului?
Similar ca uleiul:
1. Completați **Mentenanță → Distribuitor data schimbului**
2. Introduceți **Interval schimb distribuitor (km)**
3. Senzorul arată km rămași

### Cum funcționează detecția anvelopelor de sezon?
- Puteți introduce date pentru **Anvelope iarnă** și **Anvelope vară**
- Integrarea creează senzori de status pentru fiecare set
- Indicați manual când ați montat setul respectiv
- Asta vă ajută să păstrați evidența tipului de anvelope și a datei schimbării

### Cum urmăresc bateria?
1. Completați **Mentenanță → Data ultimei înlocuiri a bateriei**
2. Introduceți **Interval baterie (ani)** (tipic 3-5 ani)
3. Senzorul arată dacă bateria trebuie înlocuită

### Cum urmăresc frânele?
1. Completați **Mentenanță → Frâne** cu kilometrajul la ultima și următoarea schimbare
2. Senzorul arată km rămași până la schimbare (separat pentru plăcuțe și discuri)

### Cum urmăresc trusa de prim ajutor?
Trusa de prim ajutor este **obligatorie în România**. Integrarea o gestionează astfel:
1. Accesați **Mentenanță → Trusă de prim ajutor**
2. Completați **Data expirare** (ZZ.LL.AAAA)
3. Senzorul arată zilele rămase până la expirare
4. Atributul „Stare" arată „Valid" sau „Expirat"

### Cum urmăresc extinctorul?
Extinctorul este **obligatoriu în România**. Funcționează identic cu trusa de prim ajutor:
1. Accesați **Mentenanță → Extinctor**
2. Completați **Data expirare** (ZZ.LL.AAAA)
3. Senzorul arată zilele rămase până la expirare
4. Atributul „Stare" arată „Valid" sau „Expirat"

### Cum urmăresc rovinieta?
1. Accesați meniul de configurare → **Rovinieta**
2. Completați **Data început** și **Data sfârșit** (ZZ.LL.AAAA)
3. Opțional: categorie și preț
4. Senzorul arată zilele rămase până la expirare (similar cu RCA/ITP)
5. Atributul „Stare" arată „Valid" sau „Expirat"

---

## 5. Leasing

### Când apare sensorul de leasing?
- Sensorul de leasing apare doar dacă setați **Identificare → Tip proprietate = Leasing**
- Câmpul **Data expirării leasing** devine activ doar în acest caz
- La prima selectare a opțiunii „Leasing", apare automat un pas suplimentar pentru data de expirare

### Ce se întâmplă dacă schimb din "Leasing" la "Proprietate"?
- Câmpurile de leasing dispar din interfață
- Sensorul de leasing dispare din Home Assistant
- Datele sunt șterse (nu mai sunt necesare)
- Puteți reveni oricând la "Leasing"

### Cum urmăresc expirarea contractului de leasing?
1. Setați **Tip proprietate = Leasing**
2. Completați **Data expirării leasing** (ZZ.LL.AAAA)
3. Senzorul arată zilele rămase (similar cu RCA/ITP)
4. Folosiți în automatizări pentru reminder

---

## 6. Automatizări

### Cum creez notificări pentru documente și mentenanță?

Recomandăm o singură automatizare care verifică **zilnic** toți senzorii, în loc de trigger-uri `numeric_state` separate (care se activează doar la **tranziția** valorii sub prag și pot rata notificări după restart HA).

```yaml
automation:
  - alias: "Vehicul B123ABC — Notificări zilnice"
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
                    message: "Mai ai {{ val }} {{ repeat.item.unitate }} rămase."
```

Adăugați sau eliminați senzori din lista `for_each` după necesități. Pragurile se pot ajusta liber.

### Cum creez o notificare doar pentru RCA, Casco sau ITP?
Folosiți automatizarea de mai sus, dar păstrați doar senzorul dorit în lista `for_each`.

### Cum actualizez kilometrajul automat?
Puteți utiliza serviciul **`vehicule.actualizeaza_date`** pentru a actualiza km-ul curent din automatizări.

Exemplu (automatizare care actualizează km):

```yaml
automation:
  - alias: "Actualizare km din GPS"
    triggers:
      - trigger: time_pattern
        hours: "/1"
    actions:
      - action: vehicule.actualizeaza_date
        data:
          nr_inmatriculare: "B123ABC"
          km_curent: "{{ states('sensor.obd_odometer') | int(0) }}"
```

### Care sunt cazurile de utilizare frecvente?
- Notificări push pe telefon când expira RCA/Casco/ITP
- Trimitere de email/SMS cu reminder-uri
- Logging datelor în baze de date externe (ex: InfluxDB)
- Integrare cu dashboard-uri custom în Lovelace
- Afișare în tablete/displaye montate în vehicul

---

## 7. Backup și Restore

### Cum fac backup la datele unui vehicul?
Folosiți serviciul `vehicule.exporta_date`:
1. Accesați **Developer Tools → Services**
2. Selectați `vehicule.exporta_date`
3. Introduceți numărul de înmatriculare (ex: `B123ABC`)
4. Apăsați **Call Service**

Fișierul JSON este salvat automat în `/config/vehicule_backup_b123abc.json`.

### Cum restaurez datele unui vehicul?
Folosiți serviciul `vehicule.importa_date`:
1. Copiați fișierul JSON de backup în directorul `/config/`
2. Accesați **Developer Tools → Services**
3. Selectați `vehicule.importa_date`
4. Introduceți calea completă (ex: `/config/vehicule_backup_b123abc.json`)
5. Apăsați **Call Service**

Dacă vehiculul nu există, va fi creat automat. Dacă există, opțiunile sunt actualizate.

### Ce conține fișierul de backup?
Fișierul JSON include: versiunea de backup, domeniul integrării, numărul de înmatriculare, data exportului și toate opțiunile configurate (identificare, documente, mentenanță, kilometraj).

### Pot folosi backup/restore pentru a migra între instanțe HA?
Da. Exportați pe instanța sursă, copiați fișierul JSON pe instanța destinație și importați. Vehiculul va fi creat automat dacă nu există.

---

## 8. Troubleshooting

### Un senzor arată "Unknown"
**Cauze:**
- Datele pentru acel senzor nu sunt completate
- Format de dată incorect (asigurați-vă că utilizați ZZ.LL.AAAA)
- An de fabricație/înmatriculare în afara intervalului acceptat (1900 - curent+1)

**Soluție:**
1. Verificați categoria relevantă în Options
2. Completați datele în format corect
3. Salvați

### Înțeleg: "Entity not provided by integration"
Aceasta se întâmplă dacă:
- Ați șters vehiculul din integrare, dar automația/dashboard-ul încă refera senzori orfani
- Numele senzorului s-a schimbat între versiuni

**Soluție:**
1. Actualizați referințele în automatizări/dashboard-uri
2. Ștergeți și re-adăugați vehiculul dacă sunt probleme persistente

### Cum activez debug logging?
Consultați [DEBUG.md](DEBUG.md) pentru instrucțiuni detaliate asupra activării logging-ului debug.

### Integrarea nu apare în lista de integrații
- Asigurați-vă că ați instalat-o din HACS sau manual
- Verificați că fișierele sunt în locația corectă: `custom_components/vehicule/`
- Restartați Home Assistant
- Verificați din **Settings → System → Logs** pentru erori

### Datele nu se salvează corect
- Verificați formatele de dată (ZZ.LL.AAAA)
- Asigurați-vă că anii sunt în interval valid
- Restartați integrarea din **Settings → Devices & Services → Vehicule → [meniu...]**

---

## 9. Actualizări

### Cum actualizez integrarea?
**Dacă folosiți HACS:**
1. Accesați **HACS → Integrations → Vehicule**
2. Apăsați **Update**
3. Restartați Home Assistant

**Dacă ati instalat manual:**
1. Descărcați versiunea nouă de la GitHub
2. Copiați fișierele în `custom_components/vehicule/`
3. Restartați Home Assistant

### Setările mele sunt păstrate după actualizare?
Da. Configurațiile și datele vehiculelor sunt stocate în baza de date Home Assistant și nu sunt afectate de actualizări.

### Trebuie să șterg și să re-adaug vehiculul după actualizare?
Nu, în 99% dintre cazuri. Configurația și datele sunt păstrate. Poate fi necesar doar dacă:
- Au fost schimbări majore în structura entităților (rar)
- Documentația de upgrade o recomandă explicit

În caz de îndoială, consultați [CHANGELOG.md](CHANGELOG.md).

### Ce se întâmplă cu entitățile după actualizare?
- Entitățile noi sunt adăugate automat
- Entitățile existente sunt actualizate
- Entitățile care nu mai sunt necesare sunt auto-șterse
- Nicio pierdere de date

---

## Alte Resurse

- **Cod sursă:** https://github.com/cnecrea/vehicule
- **Issues/Bug reports:** https://github.com/cnecrea/vehicule/issues
- **Debug logging:** Consultați [DEBUG.md](DEBUG.md)
- **Changelog:** Consultați [CHANGELOG.md](CHANGELOG.md)
- **Contribuții:** Pull requests sunt binevenite!

---

*Ultima actualizare: 2026-03-14*
