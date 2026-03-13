<a name="top"></a>
# Întrebări frecvente

- [Ce este integrarea Vehicule?](#ce-este-integrarea-vehicule)
- [Are nevoie de internet?](#are-nevoie-de-internet)
- [Este gratuită?](#este-gratuită)
- [Cum adaug un vehicul?](#cum-adaug-un-vehicul)
- [Cum editez datele unui vehicul?](#cum-editez-datele-unui-vehicul)
- [Care sunt categoriile disponibile în meniu?](#care-sunt-categoriile-disponibile-în-meniu)
- [Cum funcționează formatele de dată?](#cum-funcționează-formatele-de-dată)
- [Ce se întâmplă dacă șterg o valoare dintr-un câmp?](#ce-se-întâmplă-dacă-șterg-o-valoare-dintr-un-câmp)
- [Câți senzori are fiecare vehicul?](#câți-senzori-are-fiecare-vehicul)
- [Când apare sau dispare un senzor?](#când-apare-sau-dispare-un-senzor)
- [Ce arată valoarea unui senzor de tip „zile"?](#ce-arată-valoarea-unui-senzor-de-tip-zile)
- [Trebuie setat kilometrajul înainte de ITP și mentenanță?](#trebuie-setat-kilometrajul-înainte-de-itp-și-mentenanță)
- [Cum urmăresc rovinieta?](#cum-urmăresc-rovinieta)
- [Cum urmăresc schimbul de ulei?](#cum-urmăresc-schimbul-de-ulei)
- [Cum urmăresc distribuția?](#cum-urmăresc-distribuția)
- [Cum funcționează detecția anvelopelor de sezon?](#cum-funcționează-detecția-anvelopelor-de-sezon)
- [Cum urmăresc bateria?](#cum-urmăresc-bateria)
- [Cum urmăresc frânele?](#cum-urmăresc-frânele)
- [Cum urmăresc trusa de prim ajutor și extinctorul?](#cum-urmăresc-trusa-de-prim-ajutor-și-extinctorul)
- [Când apare senzorul de leasing?](#când-apare-senzorul-de-leasing)
- [Ce se întâmplă dacă schimb din „Leasing" la „Proprietate"?](#ce-se-întâmplă-dacă-schimb-din-leasing-la-proprietate)
- [Cum creez notificări zilnice pentru documente și mentenanță?](#cum-creez-notificări-zilnice-pentru-documente-și-mentenanță)
- [Cum actualizez kilometrajul automat?](#cum-actualizez-kilometrajul-automat)
- [Cum fac backup la datele unui vehicul?](#cum-fac-backup-la-datele-unui-vehicul)
- [Cum restaurez datele unui vehicul din backup?](#cum-restaurez-datele-unui-vehicul-din-backup)
- [Pot folosi backup/restore pentru a migra între instanțe HA?](#pot-folosi-backuprestore-pentru-a-migra-între-instanțe-ha)
- [Un senzor arată „Unknown". De ce?](#un-senzor-arată-unknown-de-ce)
- [Primesc „Entity not provided by integration". Ce fac?](#primesc-entity-not-provided-by-integration-ce-fac)
- [Integrarea nu apare în lista de integrații. De ce?](#integrarea-nu-apare-în-lista-de-integrații-de-ce)
- [Cum activez debug logging?](#cum-activez-debug-logging)
- [Trebuie să șterg și să readaug vehiculul după actualizare?](#trebuie-să-șterg-și-să-readaug-vehiculul-după-actualizare)
- [Îmi place proiectul. Cum pot să-l susțin?](#îmi-place-proiectul-cum-pot-să-l-susțin)

---

## Ce este integrarea Vehicule?

[↑ Înapoi la cuprins](#top)

Vehicule este o integrare Home Assistant personalizată care permite gestionarea vehiculelor și documentelor acestora — RCA, ITP, rovinieta, impozit, leasing, mentenanță — direct din interfața HA. Poți urmări expirarea documentelor, kilometrajul și starea mentenanței pentru fiecare vehicul.

E ideală pentru proprietarii de vehicule multiple, flote sau oricine vrea centralizarea datelor 100% local.

---

## Are nevoie de internet?

[↑ Înapoi la cuprins](#top)

**Nu.** Integrarea funcționează 100% local, pe instanța ta Home Assistant. Nu trimite nicio informație către servere externe, nu are dependențe de API-uri și nu necesită conexiune la internet. Datele rămân sub controlul tău total.

Clasa IoT: `calculated` — datele sunt prelucrate local pe baza valorilor introduse de utilizator.

---

## Este gratuită?

[↑ Înapoi la cuprins](#top)

Da, complet gratuită și open-source. Codul sursă este disponibil pe GitHub: https://github.com/cnecrea/vehicule

---

## Cum adaug un vehicul?

[↑ Înapoi la cuprins](#top)

1. Mergi la **Settings** → **Devices & Services** → **Add Integration**
2. Caută „**Vehicule**"
3. Introdu numărul de înmatriculare, fără spații (ex: `B123ABC`)
4. Click **Submit**

Integrarea creează un device cu un singur senzor (Informații). Restul senzorilor apar pe măsură ce completezi date.

Fiecare vehicul = 1 config entry, identificat unic prin numărul de înmatriculare. Detalii complete în [SETUP.md](./SETUP.md).

---

## Cum editez datele unui vehicul?

[↑ Înapoi la cuprins](#top)

1. Mergi la **Settings** → **Devices & Services** → **Vehicule**
2. Click pe intrarea vehiculului dorit
3. Click pe butonul **Configure** (⚙️)
4. Alege categoria din meniu și completează câmpurile

Datele calendaristice se introduc în format **ZZ.LL.AAAA** (ex: `18.04.2026`). Câmpurile de an acceptă valori cu 4 cifre, validate server-side.

---

## Care sunt categoriile disponibile în meniu?

[↑ Înapoi la cuprins](#top)

```
Gestionare vehicul
├── Date de identificare
├── Asigurare RCA
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

**Identificare** — marcă, model, combustibil, cilindree, an fabricație, an înmatriculare, tip proprietate.
**RCA** — număr poliță, companie, date emitere/expirare, cost.
**ITP** — data expirare, stație, km la ITP.
**Rovinieta** — data început, data sfârșit, categorie, preț.
**Administrativ** — proprietar, tip proprietate, impozit, leasing.
**Mentenanță** — revizie ulei, distribuție, anvelope, baterie, frâne, trusă prim ajutor, extinctor.
**Kilometraj** — kilometrajul curent (manual sau prin automatizări).

---

## Cum funcționează formatele de dată?

[↑ Înapoi la cuprins](#top)

Datele se introduc în format **ZZ.LL.AAAA** (ex: `15.03.2026` pentru 15 martie 2026). În interfață se afișează tot în format românesc. Intern, sunt stocate în format ISO (YYYY-MM-DD).

Câmpurile de an (fabricație, înmatriculare) acceptă valori între **1900** și anul curent (+1 pentru fabricație). Validarea se face server-side.

---

## Ce se întâmplă dacă șterg o valoare dintr-un câmp?

[↑ Înapoi la cuprins](#top)

Câmpurile sunt opționale. Dacă golești un câmp și salvezi, senzorul asociat **dispare** din Home Assistant și datele anterioare sunt șterse. Poți completa din nou oricând, iar senzorul va reapărea.

---

## Câți senzori are fiecare vehicul?

[↑ Înapoi la cuprins](#top)

Până la **15 senzori**, toți condiționați — apar doar dacă au date completate:

| Senzor | Cheie | Unitate | Ce afișează |
|--------|-------|---------|-------------|
| Informații | `informatii` | — | Marcă + Model |
| Kilometraj | `kilometraj` | km | Km curent |
| RCA | `rca` | zile | Zile rămase |
| ITP | `itp` | zile | Zile rămase |
| Rovinieta | `rovinieta` | zile | Zile rămase |
| Impozit | `impozit` | zile | Zile rămase până la scadență |
| Leasing | `leasing` | zile | Zile rămase |
| Revizie ulei | `revizie_ulei` | km | Km rămași |
| Distribuție | `distributie` | km | Km rămași |
| Anvelope | `anvelope` | — | Sezon curent (Vară / Iarnă) |
| Baterie | `baterie` | luni | Luni de la schimb |
| Plăcuțe frână | `placute_frana` | km | Km rămași |
| Discuri frână | `discuri_frana` | km | Km rămași |
| Trusă prim ajutor | `trusa_prim_ajutor` | zile | Zile rămase |
| Extinctor | `extinctor` | zile | Zile rămase |

Entity ID-urile urmează formatul: `sensor.vehicule_{nr_normalizat}_{cheie}` (ex: `sensor.vehicule_b123abc_rca`).

---

## Când apare sau dispare un senzor?

[↑ Înapoi la cuprins](#top)

Un senzor **apare** când completezi datele relevante. **Dispare** automat când golești câmpurile corespunzătoare. Integrarea curăță automat entitățile orfane — nu trebuie să faci nimic manual.

---

## Ce arată valoarea unui senzor de tip „zile"?

[↑ Înapoi la cuprins](#top)

- **Valori pozitive** (ex: 45) — zilele rămase până la expirare
- **0** — expiră astăzi
- **Valori negative** (ex: -10) — documentul a expirat cu 10 zile în urmă

Exemplu: RCA expiră în 15 zile → `state = 15`. A expirat acum 3 zile → `state = -3`.

---

## Trebuie setat kilometrajul înainte de ITP și mentenanță?

[↑ Înapoi la cuprins](#top)

Da. Începând cu v1.1.0, pașii **ITP**, **Revizie ulei**, **Distribuție** și **Frâne** necesită ca kilometrajul curent să fie configurat. Dacă nu e setat, formularul afișează eroarea `km_necesar` și blochează salvarea.

Soluția: accesează mai întâi **Actualizare kilometraj** din meniul principal și setează km-ul curent.

---

## Cum urmăresc rovinieta?

[↑ Înapoi la cuprins](#top)

1. Din meniul de configurare, alege **Rovinieta**
2. Completează **Data început** și **Data sfârșit** (ZZ.LL.AAAA)
3. Opțional: categorie și preț (RON)
4. Senzorul arată zilele rămase până la expirare (identic cu RCA/ITP)

Atribute expuse: Data început, Data sfârșit, Categorie, Preț (RON), Stare (Valid/Expirat).

---

## Cum urmăresc schimbul de ulei?

[↑ Înapoi la cuprins](#top)

1. Accesează **Mentenanță → Revizie ulei**
2. Completează km-ul la ultima revizie, km-ul pentru următoarea revizie și data ultimei revizii
3. Senzorul arată **km rămași** până la următoarea revizie
4. Când valoarea scade sub 0, revzia e depășită

---

## Cum urmăresc distribuția?

[↑ Înapoi la cuprins](#top)

Funcționează identic cu revizia de ulei: completezi km-ul la ultima și următoarea schimbare a distribuției, iar senzorul afișează km rămași.

---

## Cum funcționează detecția anvelopelor de sezon?

[↑ Înapoi la cuprins](#top)

Poți introduce datele de montare pentru **anvelope vară** și **anvelope iarnă**. Senzorul afișează sezonul curent (Vară / Iarnă) și compară cu sezonul recomandat. Te ajută să ții evidența schimbărilor de anvelope.

---

## Cum urmăresc bateria?

[↑ Înapoi la cuprins](#top)

1. Accesează **Mentenanță → Baterie**
2. Completează **Data schimb** (ZZ.LL.AAAA)
3. Senzorul arată **lunile de la ultimul schimb** — util pentru a ști când trebuie înlocuită (tipic 3-5 ani)

---

## Cum urmăresc frânele?

[↑ Înapoi la cuprins](#top)

1. Accesează **Mentenanță → Frâne**
2. Completează km-ul la ultima și următoarea schimbare (separat pentru plăcuțe și discuri)
3. Senzori separați pentru plăcuțe și discuri, fiecare cu km rămași

> **Notă:** Necesită setarea prealabilă a kilometrajului curent.

---

## Cum urmăresc trusa de prim ajutor și extinctorul?

[↑ Înapoi la cuprins](#top)

Ambele sunt **obligatorii în România** și funcționează identic:

1. Accesează **Mentenanță → Trusă de prim ajutor** sau **Extinctor**
2. Completează **Data expirare** (ZZ.LL.AAAA)
3. Senzorul arată zilele rămase până la expirare
4. Atributul „Stare" indică „Valid" sau „Expirat"

---

## Când apare senzorul de leasing?

[↑ Înapoi la cuprins](#top)

Senzorul de leasing apare doar dacă setezi **Tip proprietate = Leasing** în secțiunea Date administrative. La prima selectare a opțiunii „Leasing", integrarea deschide automat un pas suplimentar pentru a introduce data de expirare a contractului de leasing.

Senzorul arată zilele rămase (similar cu RCA/ITP).

---

## Ce se întâmplă dacă schimb din „Leasing" la „Proprietate"?

[↑ Înapoi la cuprins](#top)

Câmpurile de leasing dispar din interfață, senzorul de leasing dispare din Home Assistant, iar datele de leasing sunt șterse. Poți reveni oricând la „Leasing" și completa din nou.

---

## Cum creez notificări zilnice pentru documente și mentenanță?

[↑ Înapoi la cuprins](#top)

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

Adaugă sau elimină senzori din lista `for_each` după preferințe. Pragurile se pot ajusta liber.

> **⚠️ Important:** Înlocuiește `b123abc` cu numărul normalizat al vehiculului tău și `notify.mobile_app` cu entity_id-ul serviciului tău de notificare (ex: `notify.mobile_app_telefonul_meu`).

---

## Cum actualizez kilometrajul automat?

[↑ Înapoi la cuprins](#top)

Folosește serviciul `vehicule.actualizeaza_date` dintr-o automatizare. Exemplu cu senzor OBD/GPS:

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

---

## Cum fac backup la datele unui vehicul?

[↑ Înapoi la cuprins](#top)

Folosește serviciul `vehicule.exporta_date`:

1. Mergi la **Developer Tools → Services**
2. Selectează `vehicule.exporta_date`
3. Introdu numărul de înmatriculare (ex: `B123ABC`)
4. Apasă **Call Service**

Fișierul JSON este salvat automat în `/config/vehicule_backup_b123abc.json`. Conține: versiunea de backup, domeniul integrării, numărul de înmatriculare, data exportului și toate opțiunile configurate.

---

## Cum restaurez datele unui vehicul din backup?

[↑ Înapoi la cuprins](#top)

Folosește serviciul `vehicule.importa_date`:

1. Copiază fișierul JSON de backup în directorul `/config/`
2. Mergi la **Developer Tools → Services**
3. Selectează `vehicule.importa_date`
4. Introdu calea completă (ex: `/config/vehicule_backup_b123abc.json`)
5. Apasă **Call Service**

Dacă vehiculul nu există, va fi creat automat. Dacă există, opțiunile sunt actualizate.

---

## Pot folosi backup/restore pentru a migra între instanțe HA?

[↑ Înapoi la cuprins](#top)

Da. Exportezi pe instanța sursă, copiezi fișierul JSON pe instanța destinație (în `/config/`) și importezi. Vehiculul va fi creat automat dacă nu există. Ideal și pentru gestionarea flotelor — poți exporta/importa în masă.

---

## Un senzor arată „Unknown". De ce?

[↑ Înapoi la cuprins](#top)

Cauze posibile:
- Datele pentru acel senzor nu sunt completate
- Format de dată incorect (trebuie ZZ.LL.AAAA)
- An de fabricație/înmatriculare în afara intervalului acceptat (1900 – curent+1)

Soluție: verifică categoria relevantă în Options, completează datele în format corect și salvează.

---

## Primesc „Entity not provided by integration". Ce fac?

[↑ Înapoi la cuprins](#top)

Se întâmplă dacă ai șters vehiculul din integrare, dar automatizarea/dashboard-ul încă referă senzorii vechi. Actualizează referințele din automatizări și dashboard-uri. Dacă problema persistă, șterge și re-adaugă vehiculul.

---

## Integrarea nu apare în lista de integrații. De ce?

[↑ Înapoi la cuprins](#top)

Verifică:
1. Ai instalat-o din HACS sau manual (fișierele trebuie să fie în `custom_components/vehicule/`)
2. Ai restartat Home Assistant după instalare
3. Nu sunt erori în **Settings → System → Logs** legate de `vehicule`

---

## Cum activez debug logging?

[↑ Înapoi la cuprins](#top)

Consultă [DEBUG.md](DEBUG.md) pentru instrucțiuni detaliate. Pe scurt, adaugă în `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.vehicule: debug
```

Apoi restartează Home Assistant și verifică logurile din **Settings → System → Logs**.

---

## Trebuie să șterg și să readaug vehiculul după actualizare?

[↑ Înapoi la cuprins](#top)

De regulă nu. Configurațiile și datele vehiculelor sunt stocate în baza de date HA și nu sunt afectate de actualizări. Entitățile noi sunt adăugate automat, cele existente sunt actualizate, iar cele care nu mai sunt necesare sunt auto-șterse.

Poate fi necesar doar dacă au fost schimbări majore în structura entităților (rar) sau documentația de upgrade o recomandă explicit.

---

## Îmi place proiectul. Cum pot să-l susțin?

[↑ Înapoi la cuprins](#top)

- ⭐ Oferă un **star** pe [GitHub](https://github.com/cnecrea/vehicule/)
- 🐛 **Raportează probleme** — deschide un [issue](https://github.com/cnecrea/vehicule/issues)
- 🔀 **Contribuie cu cod** — trimite un pull request
- ☕ **Donează** prin [Buy Me a Coffee](https://buymeacoffee.com/cnecrea)
- 📢 **Distribuie** proiectul prietenilor sau comunității tale
