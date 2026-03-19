# Carduri Lovelace — Integrarea Vehicule

Dashboard profesional pentru integrarea [**Vehicule**](https://github.com/cnecrea/vehicule) — cu culori condiționate (verde / portocaliu / roșu), icoane per categorie și secțiuni care apar doar când au date completate.

---

## Vehicule Card — configurare automată (recomandat)

[**Vehicule Card**](https://github.com/cnecrea/vehicule-card) este un card custom care generează automat întregul dashboard cu o singură linie de YAML. Auto-descoperă vehiculele din integrare, afișează doar secțiunile relevante și ascunde dinamic ce nu este configurat (ex: dacă nu ai leasing, cardul de leasing nu apare; dacă nu ai completat trusa de prim ajutor, secțiunea echipament dispare).

### Instalare

1. **HACS** → **Frontend** → **+** → Repository: `cnecrea/vehicule-card`
2. Instalați **Vehicule Card** → Reporniți Home Assistant
3. Adăugați un card nou → Căutați **Vehicule Card** în lista de carduri personalizate

### Configurare minimă

```yaml
type: custom:vehicule-card
```

### Configurare completă

```yaml
type: custom:vehicule-card
vehicul: b123abc
sectiuni:
  - informatii
  - documente
  - mentenanta
  - echipament
  - grafic
```

Vehicule Card include editor vizual (dropdown vehicul + checkbox-uri secțiuni) și preview live în editorul de carduri.

Detalii complete, parametri și cerințe: [**github.com/cnecrea/vehicule-card**](https://github.com/cnecrea/vehicule-card)

---

## Configurare manuală YAML

Dacă preferați control total asupra fiecărei secțiuni sau doriți să personalizați designul, mai jos găsiți configurațiile YAML complete pentru fiecare secțiune. Copiați codul, înlocuiți prefixul vehiculului și lipiți-l în dashboard.

Această variantă folosește aceleași carduri custom ca Vehicule Card și produce același rezultat vizual.

---

## Cerințe

Următoarele componente custom trebuie instalate din [HACS](https://hacs.xyz/) înainte de utilizare:

| Componentă | Rol |
|---|---|
| [Bubble Card](https://github.com/Clooos/Bubble-Card) | Separatoare de secțiune |
| [button-card](https://github.com/custom-cards/button-card) | Carduri cu JavaScript templates |
| [stack-in-card](https://github.com/custom-cards/stack-in-card) | Grupare carduri fără margini |
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | Stilizare CSS personalizată |
| [mini-graph-card](https://github.com/kalkih/mini-graph-card) | Grafic istoric kilometraj |

---

## Cum se folosesc

1. Copiați codul YAML al secțiunii dorite
2. În Home Assistant → **Dashboard** → **Edit** → **Add Card** → **Manual**
3. Lipiți codul YAML
4. **Înlocuiți `b123abc`** cu numărul normalizat al vehiculului vostru (litere mici, fără spații)
   - Exemplu: pentru plăcuța `B123ABC` → `sensor.vehicule_b123abc_rca`

> **Notă**: Cardurile folosesc atributele exacte din integrare. Dacă un senzor nu este vizibil (nu ați completat datele respective), cardul va afișa `—` sau nu va apărea deloc.

---

## Senzori disponibili

| Senzor | Entity ID | Unitate | Ce afișează |
|---|---|---|---|
| Informații | `sensor.vehicule_b123abc_informatii` | — | Marcă + Model |
| Kilometraj | `sensor.vehicule_b123abc_kilometraj` | km | Km curent |
| RCA | `sensor.vehicule_b123abc_rca` | zile | Zile rămase |
| Casco | `sensor.vehicule_b123abc_casco` | zile | Zile rămase |
| ITP | `sensor.vehicule_b123abc_itp` | zile | Zile rămase |
| Rovinieta | `sensor.vehicule_b123abc_rovinieta` | zile | Zile rămase |
| Impozit | `sensor.vehicule_b123abc_impozit` | zile | Zile rămase |
| Leasing | `sensor.vehicule_b123abc_leasing` | zile | Zile rămase |
| Revizie ulei | `sensor.vehicule_b123abc_revizie_ulei` | km | Km rămași |
| Distribuție | `sensor.vehicule_b123abc_distributie` | km | Km rămași |
| Anvelope | `sensor.vehicule_b123abc_anvelope` | — | Vară / Iarnă |
| Baterie | `sensor.vehicule_b123abc_baterie` | luni | Luni de la schimb |
| Plăcuțe frână | `sensor.vehicule_b123abc_placute_frana` | km | Km rămași |
| Discuri frână | `sensor.vehicule_b123abc_discuri_frana` | km | Km rămași |
| Trusă prim ajutor | `sensor.vehicule_b123abc_trusa_prim_ajutor` | zile | Zile rămase |
| Extinctor | `sensor.vehicule_b123abc_extinctor` | zile | Zile rămase |
| Cost total | `sensor.vehicule_b123abc_cost_total` | RON | Suma costurilor curente |

---

## Sistem de culori

Toate cardurile folosesc același sistem de culori condiționate:

| Culoare | Condiție | Semnificație |
|---|---|---|
| 🟢 Verde (`#4CAF50`) | Valoare OK (peste prag) | Totul este în regulă |
| 🟠 Portocaliu (`#FF9800`) | Aproape de prag | Atenție — acționați curând |
| 🔴 Roșu (`#EF4F1A`) | Sub zero / expirat / depășit | Acțiune imediată necesară |

Pragurile implicite: **30 zile** pentru documente, **1.000–5.000 km** pentru mentenanță, **36/48 luni** pentru baterie.

---

## 1. Informații vehicul

Header cu marcă, model, motorizare și an de fabricație.
Grid cu 3 indicatori: kilometraj, putere (CP) și cilindree (cm³).
Footer cu VIN, Serie CIV și număr de înmatriculare.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    icon: ""
    name: VEHICUL B123ABC
    sub_button:
      main: []
      bottom: []
  - type: custom:stack-in-card
    mode: vertical
    card_mod:
      style: |
        ha-card {
          border-radius: 10px;
          overflow: hidden;
          box-shadow: none;
          border: none;
        }
    cards:
      - type: custom:button-card
        entity: sensor.vehicule_b123abc_informatii
        show_state: false
        show_name: false
        show_icon: false
        show_label: false
        tap_action:
          action: more-info
        custom_fields:
          header: |
            [[[
              const attr = entity.attributes || {};
              const marca = attr['Marcă'] || '';
              const model = attr['Model'] || '';
              const titlu = (marca + ' ' + model).trim() || entity.state || '—';
              const combustibil = attr['Combustibil'] || '';
              const an = attr['An fabricație'] || '';
              const motorizare = attr['Motorizare'] || '';
              let detail = [combustibil, motorizare, an].filter(Boolean).join(' · ');
              return `
                <div style="display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:center;">
                  <div style="width:56px;height:56px;border-radius:14px;background:rgba(33,150,243,0.15);display:flex;align-items:center;justify-content:center;">
                    <ha-icon icon="mdi:car" style="width:28px;height:28px;color:rgb(33,150,243);"></ha-icon>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:13px;color:var(--secondary-text-color);">Vehicul</div>
                    <div style="font-size:22px;font-weight:700;color:rgb(33,150,243);line-height:1.2;">${titlu}</div>
                    <div style="font-size:13px;color:var(--secondary-text-color);opacity:0.8;margin-top:2px;">${detail}</div>
                  </div>
                </div>`;
            ]]]
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
            - padding: 22px 22px 30px
          grid:
            - grid-template-areas: '"header"'
            - grid-template-columns: 1fr
          custom_fields:
            header:
              - width: 100%
      - type: grid
        square: false
        columns: 3
        cards:
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_kilometraj
            icon: mdi:speedometer
            name: Kilometraj
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: rgba(33,150,243,0.15)
            label: |
              [[[
                const v = entity.state;
                return v ? parseInt(v).toLocaleString('ro-RO') + ' km' : '—';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 24px
                - color: rgb(33,150,243)
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
              label:
                - font-size: 15px
                - font-weight: 600
                - color: rgb(33,150,243)
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_informatii
            icon: mdi:engine
            name: Putere
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: rgba(255,152,0,0.15)
            label: |
              [[[
                const cp = entity.attributes['Putere (CP)'];
                const kw = entity.attributes['Putere (kW)'];
                if (cp) return cp + ' CP';
                if (kw) return kw + ' kW';
                return '—';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 24px
                - color: rgb(255,152,0)
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
              label:
                - font-size: 15px
                - font-weight: 600
                - color: rgb(255,152,0)
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_informatii
            icon: mdi:piston
            name: Cilindree
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: rgba(158,158,158,0.15)
            label: |
              [[[
                const cc = entity.attributes['Capacitate cilindrică (cm³)'];
                return cc ? cc + ' cm³' : '—';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 24px
                - color: rgb(158,158,158)
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
              label:
                - font-size: 15px
                - font-weight: 600
                - color: rgb(158,158,158)
      - type: custom:button-card
        entity: sensor.vehicule_b123abc_informatii
        show_state: false
        show_name: false
        show_icon: false
        show_label: false
        tap_action:
          action: more-info
        custom_fields:
          info: |
            [[[
              const attr = entity.attributes || {};
              const vin = attr['VIN'] || '—';
              const civ = attr['Serie CIV'] || '—';
              const nr = attr['Nr. înmatriculare'] || '—';
              return `
                <div style="padding-top:10px;display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:20px;">
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:car-info" style="width:13px;height:13px;color:#888;"></ha-icon>VIN: ${vin}
                  </span>
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:card-account-details" style="width:13px;height:13px;color:#888;"></ha-icon>CIV: ${civ}
                  </span>
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:numeric" style="width:13px;height:13px;color:#888;"></ha-icon>${nr}
                  </span>
                </div>`;
            ]]]
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
            - padding: 0 22px 16px
          grid:
            - grid-template-areas: '"info"'
            - grid-template-columns: 1fr
          custom_fields:
            info:
              - width: 100%
```

---

## 2. Documente (RCA, Casco, ITP, Rovinieta, Impozit, Leasing)

Header cu status RCA (cel mai important document) — afișează zilele rămase, compania și numărul poliței.
Grid cu 5 indicatori: Casco, ITP, Rovinieta, Impozit, Leasing — fiecare cu culoare condiționată.
Footer cu date emitere/expirare RCA și cost.

> **Notă**: Cardul Leasing apare doar dacă **Tip proprietate = leasing** este selectat în integrare. Dacă nu aveți leasing, eliminați cardul din grid sau înlocuiți-l cu alt senzor.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    icon: ""
    name: DOCUMENTE
    sub_button:
      main: []
      bottom: []
  - type: custom:stack-in-card
    mode: vertical
    card_mod:
      style: |
        ha-card {
          border-radius: 10px;
          overflow: hidden;
          box-shadow: none;
          border: none;
        }
    cards:
      - type: custom:button-card
        entity: sensor.vehicule_b123abc_rca
        show_state: false
        show_name: false
        show_icon: false
        show_label: false
        tap_action:
          action: more-info
        custom_fields:
          header: |
            [[[
              const attr = entity.attributes || {};
              const zile = parseInt(entity.state) || 0;
              const stare = attr['Stare'] || '—';
              const companie = attr['Companie'] || '';
              const polita = attr['Număr poliță'] || '';
              const expira = attr['Data expirare'] || '—';
              const cost = attr['Cost (RON)'] || '';
              const valid = zile >= 0;
              const color = valid ? (zile < 30 ? '#FF9800' : '#4CAF50') : '#EF4F1A';
              let detail = companie;
              if (polita) detail += (detail ? ' · Poliță: ' : 'Poliță: ') + polita;
              return `
                <div style="display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:center;">
                  <div style="width:56px;height:56px;border-radius:14px;background:${valid ? (zile < 30 ? 'rgba(255,152,0,0.15)' : 'rgba(76,175,80,0.15)') : 'rgba(239,79,26,0.15)'};display:flex;align-items:center;justify-content:center;">
                    <ha-icon icon="${valid ? 'mdi:shield-car' : 'mdi:shield-alert'}" style="width:28px;height:28px;color:${color};"></ha-icon>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:13px;color:var(--secondary-text-color);">Asigurare RCA</div>
                    <div style="font-size:22px;font-weight:700;color:${color};line-height:1.2;">
                      ${valid ? zile + ' zile rămase' : 'EXPIRAT'}
                    </div>
                    <div style="font-size:13px;color:${color};opacity:0.8;margin-top:2px;">${detail}</div>
                  </div>
                </div>`;
            ]]]
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
            - padding: 22px 22px 30px
          grid:
            - grid-template-areas: '"header"'
            - grid-template-columns: 1fr
          custom_fields:
            header:
              - width: 100%
      - type: grid
        square: false
        columns: 5
        cards:
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_casco
            icon: mdi:shield-plus
            name: Casco
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const z = parseInt(entity.state) || 0;
                if (z < 0) return 'rgba(239,79,26,0.15)';
                if (z < 30) return 'rgba(255,152,0,0.15)';
                return 'rgba(76,175,80,0.15)';
              ]]]
            label: |
              [[[
                const z = parseInt(entity.state);
                if (isNaN(z)) return '—';
                return z < 0 ? 'EXPIRAT' : z + ' zile';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_itp
            icon: mdi:car-wrench
            name: ITP
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const z = parseInt(entity.state) || 0;
                if (z < 0) return 'rgba(239,79,26,0.15)';
                if (z < 30) return 'rgba(255,152,0,0.15)';
                return 'rgba(76,175,80,0.15)';
              ]]]
            label: |
              [[[
                const z = parseInt(entity.state);
                if (isNaN(z)) return '—';
                return z < 0 ? 'EXPIRAT' : z + ' zile';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_rovinieta
            icon: mdi:road-variant
            name: Rovinieta
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const z = parseInt(entity.state) || 0;
                if (z < 0) return 'rgba(239,79,26,0.15)';
                if (z < 30) return 'rgba(255,152,0,0.15)';
                return 'rgba(76,175,80,0.15)';
              ]]]
            label: |
              [[[
                const z = parseInt(entity.state);
                if (isNaN(z)) return '—';
                return z < 0 ? 'EXPIRAT' : z + ' zile';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_impozit
            icon: mdi:cash
            name: Impozit
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const z = parseInt(entity.state) || 0;
                if (z < 0) return 'rgba(239,79,26,0.15)';
                if (z < 30) return 'rgba(255,152,0,0.15)';
                return 'rgba(76,175,80,0.15)';
              ]]]
            label: |
              [[[
                const z = parseInt(entity.state);
                if (isNaN(z)) return '—';
                return z < 0 ? 'EXPIRAT' : z + ' zile';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_leasing
            icon: mdi:file-document-outline
            name: Leasing
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const z = parseInt(entity.state) || 0;
                if (z < 0) return 'rgba(239,79,26,0.15)';
                if (z < 30) return 'rgba(255,152,0,0.15)';
                return 'rgba(156,39,176,0.15)';
              ]]]
            label: |
              [[[
                const z = parseInt(entity.state);
                if (isNaN(z)) return '—';
                return z < 0 ? 'EXPIRAT' : z + ' zile';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(156,39,176)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const z = parseInt(entity.state) || 0;
                      if (z < 0) return 'rgb(239,79,26)';
                      if (z < 30) return 'rgb(255,152,0)';
                      return 'rgb(156,39,176)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
      - type: custom:button-card
        entity: sensor.vehicule_b123abc_rca
        show_state: false
        show_name: false
        show_icon: false
        show_label: false
        tap_action:
          action: more-info
        custom_fields:
          info: |
            [[[
              const attr = entity.attributes || {};
              const emitere = attr['Data emitere'] || '—';
              const expirare = attr['Data expirare'] || '—';
              const cost = attr['Cost (RON)'];
              const costText = cost ? cost + ' RON' : '—';
              return `
                <div style="padding-top:10px;display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:20px;">
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:calendar-arrow-right" style="width:13px;height:13px;color:#888;"></ha-icon>Emis: ${emitere}
                  </span>
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:calendar-alert" style="width:13px;height:13px;color:#888;"></ha-icon>Expiră: ${expirare}
                  </span>
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:currency-eur" style="width:13px;height:13px;color:#888;"></ha-icon>Cost: ${costText}
                  </span>
                </div>`;
            ]]]
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
            - padding: 0 22px 16px
          grid:
            - grid-template-areas: '"info"'
            - grid-template-columns: 1fr
          custom_fields:
            info:
              - width: 100%
```

---

## 3. Mentenanță

Header cu revizia de ulei (cea mai frecventă operație) — afișează km rămași cu stare colorată.
Grid rând 1: Distribuție, Plăcuțe frână, Discuri frână — toate cu km rămași și culori condiționate.
Grid rând 2: Baterie (luni de la schimb) și Anvelope (sezon curent vs. recomandat).
Footer cu detalii revizie ulei: data ultimei revizii, km curent și km următoarea revizie.

**Praguri mentenanță:**

| Senzor | Portocaliu (atenție) | Roșu (depășit) |
|---|---|---|
| Revizie ulei | < 1.000 km | < 0 km |
| Distribuție | < 5.000 km | < 0 km |
| Plăcuțe frână | < 3.000 km | < 0 km |
| Discuri frână | < 5.000 km | < 0 km |
| Baterie | > 36 luni | > 48 luni |
| Anvelope | Sezon diferit de recomandat | — |

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    icon: ""
    name: MENTENANȚĂ
    sub_button:
      main: []
      bottom: []
  - type: custom:stack-in-card
    mode: vertical
    card_mod:
      style: |
        ha-card {
          border-radius: 10px;
          overflow: hidden;
          box-shadow: none;
          border: none;
        }
    cards:
      - type: custom:button-card
        entity: sensor.vehicule_b123abc_revizie_ulei
        show_state: false
        show_name: false
        show_icon: false
        show_label: false
        tap_action:
          action: more-info
        custom_fields:
          header: |
            [[[
              const attr = entity.attributes || {};
              const kmRamasi = parseInt(entity.state) || 0;
              const kmUrm = attr['Km următoarea revizie'];
              const dataUltima = attr['Data ultima revizie'] || '—';
              const depasit = kmRamasi < 0;
              const aproape = kmRamasi >= 0 && kmRamasi < 1000;
              const color = depasit ? '#EF4F1A' : (aproape ? '#FF9800' : '#4CAF50');
              const bgColor = depasit ? 'rgba(239,79,26,0.15)' : (aproape ? 'rgba(255,152,0,0.15)' : 'rgba(76,175,80,0.15)');
              const stareText = depasit
                ? 'DEPĂȘIT cu ' + Math.abs(kmRamasi).toLocaleString('ro-RO') + ' km'
                : kmRamasi.toLocaleString('ro-RO') + ' km rămași';
              return `
                <div style="display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:center;">
                  <div style="width:56px;height:56px;border-radius:14px;background:${bgColor};display:flex;align-items:center;justify-content:center;">
                    <ha-icon icon="mdi:oil" style="width:28px;height:28px;color:${color};"></ha-icon>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:13px;color:var(--secondary-text-color);">Revizie ulei</div>
                    <div style="font-size:22px;font-weight:700;color:${color};line-height:1.2;">${stareText}</div>
                    <div style="font-size:13px;color:var(--secondary-text-color);opacity:0.8;margin-top:2px;">Ultima: ${dataUltima}</div>
                  </div>
                </div>`;
            ]]]
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
            - padding: 22px 22px 30px
          grid:
            - grid-template-areas: '"header"'
            - grid-template-columns: 1fr
          custom_fields:
            header:
              - width: 100%
      - type: grid
        square: false
        columns: 3
        cards:
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_distributie
            icon: mdi:engine
            name: Distribuție
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const v = parseInt(entity.state) || 0;
                if (v < 0) return 'rgba(239,79,26,0.15)';
                if (v < 5000) return 'rgba(255,152,0,0.15)';
                return 'rgba(33,150,243,0.15)';
              ]]]
            label: |
              [[[
                const v = parseInt(entity.state);
                if (isNaN(v)) return '—';
                return v < 0 ? 'DEPĂȘIT' : v.toLocaleString('ro-RO') + ' km';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v < 0) return 'rgb(239,79,26)';
                      if (v < 5000) return 'rgb(255,152,0)';
                      return 'rgb(33,150,243)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v < 0) return 'rgb(239,79,26)';
                      if (v < 5000) return 'rgb(255,152,0)';
                      return 'rgb(33,150,243)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_placute_frana
            icon: mdi:car-brake-alert
            name: Plăcuțe frână
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const v = parseInt(entity.state) || 0;
                if (v < 0) return 'rgba(239,79,26,0.15)';
                if (v < 3000) return 'rgba(255,152,0,0.15)';
                return 'rgba(33,150,243,0.15)';
              ]]]
            label: |
              [[[
                const v = parseInt(entity.state);
                if (isNaN(v)) return '—';
                return v < 0 ? 'DEPĂȘIT' : v.toLocaleString('ro-RO') + ' km';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v < 0) return 'rgb(239,79,26)';
                      if (v < 3000) return 'rgb(255,152,0)';
                      return 'rgb(33,150,243)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v < 0) return 'rgb(239,79,26)';
                      if (v < 3000) return 'rgb(255,152,0)';
                      return 'rgb(33,150,243)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_discuri_frana
            icon: mdi:disc
            name: Discuri frână
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const v = parseInt(entity.state) || 0;
                if (v < 0) return 'rgba(239,79,26,0.15)';
                if (v < 5000) return 'rgba(255,152,0,0.15)';
                return 'rgba(33,150,243,0.15)';
              ]]]
            label: |
              [[[
                const v = parseInt(entity.state);
                if (isNaN(v)) return '—';
                return v < 0 ? 'DEPĂȘIT' : v.toLocaleString('ro-RO') + ' km';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v < 0) return 'rgb(239,79,26)';
                      if (v < 5000) return 'rgb(255,152,0)';
                      return 'rgb(33,150,243)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v < 0) return 'rgb(239,79,26)';
                      if (v < 5000) return 'rgb(255,152,0)';
                      return 'rgb(33,150,243)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
      - type: grid
        square: false
        columns: 2
        cards:
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_baterie
            icon: mdi:car-battery
            name: Baterie
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const v = parseInt(entity.state) || 0;
                if (v > 48) return 'rgba(239,79,26,0.15)';
                if (v > 36) return 'rgba(255,152,0,0.15)';
                return 'rgba(76,175,80,0.15)';
              ]]]
            label: |
              [[[
                const v = parseInt(entity.state);
                if (isNaN(v)) return '—';
                return v + ' luni';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v > 48) return 'rgb(239,79,26)';
                      if (v > 36) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const v = parseInt(entity.state) || 0;
                      if (v > 48) return 'rgb(239,79,26)';
                      if (v > 36) return 'rgb(255,152,0)';
                      return 'rgb(76,175,80)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_anvelope
            icon: mdi:tire
            name: Anvelope
            show_state: false
            show_name: true
            show_label: true
            color_type: card
            color: |
              [[[
                const sezon = entity.state || '';
                const recomandat = entity.attributes['Sezon recomandat'] || '';
                const ok = sezon.toLowerCase() === recomandat.toLowerCase();
                return ok ? 'rgba(76,175,80,0.15)' : 'rgba(255,152,0,0.15)';
              ]]]
            label: |
              [[[
                const sezon = entity.state || '—';
                const recomandat = entity.attributes['Sezon recomandat'] || '';
                if (sezon.toLowerCase() === recomandat.toLowerCase()) return sezon + ' ✓';
                return sezon + ' (rec: ' + recomandat + ')';
              ]]]
            tap_action:
              action: more-info
            styles:
              card:
                - border-radius: 10px
                - padding: 20px 8px
                - box-shadow: none
                - border: none
              icon:
                - width: 34px
                - color: |
                    [[[
                      const sezon = entity.state || '';
                      const recomandat = entity.attributes['Sezon recomandat'] || '';
                      return sezon.toLowerCase() === recomandat.toLowerCase() ? 'rgb(76,175,80)' : 'rgb(255,152,0)';
                    ]]]
              label:
                - font-size: 13px
                - font-weight: 600
                - color: |
                    [[[
                      const sezon = entity.state || '';
                      const recomandat = entity.attributes['Sezon recomandat'] || '';
                      return sezon.toLowerCase() === recomandat.toLowerCase() ? 'rgb(76,175,80)' : 'rgb(255,152,0)';
                    ]]]
              name:
                - font-size: 13px
                - color: var(--secondary-text-color)
                - margin-top: 4px
      - type: custom:button-card
        entity: sensor.vehicule_b123abc_revizie_ulei
        show_state: false
        show_name: false
        show_icon: false
        show_label: false
        tap_action:
          action: more-info
        custom_fields:
          info: |
            [[[
              const attr = entity.attributes || {};
              const kmUltima = attr['Km ultima revizie'];
              const kmUrm = attr['Km următoarea revizie'];
              const kmCurent = attr['Km curent'];
              const dataUltima = attr['Data ultima revizie'] || '—';
              return `
                <div style="padding-top:10px;display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:20px;">
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:wrench-clock" style="width:13px;height:13px;color:#888;"></ha-icon>Ultima: ${dataUltima}
                  </span>
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:map-marker-distance" style="width:13px;height:13px;color:#888;"></ha-icon>Curent: ${kmCurent ? parseInt(kmCurent).toLocaleString('ro-RO') + ' km' : '—'}
                  </span>
                  <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--secondary-text-color);">
                    <ha-icon icon="mdi:flag-checkered" style="width:13px;height:13px;color:#888;"></ha-icon>Următoarea: ${kmUrm ? parseInt(kmUrm).toLocaleString('ro-RO') + ' km' : '—'}
                  </span>
                </div>`;
            ]]]
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
            - padding: 0 22px 16px
          grid:
            - grid-template-areas: '"info"'
            - grid-template-columns: 1fr
          custom_fields:
            info:
              - width: 100%
```

---

## 4. Echipament obligatoriu (Trusă + Extinctor)

Grid cu 2 coloane: Trusă de prim ajutor și Extinctor.
Fiecare afișează zilele rămase până la expirare, cu icon colorat și data de expirare.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    icon: ""
    name: ECHIPAMENT OBLIGATORIU
    sub_button:
      main: []
      bottom: []
  - type: custom:stack-in-card
    mode: vertical
    card_mod:
      style: |
        ha-card {
          border-radius: 10px;
          overflow: hidden;
          box-shadow: none;
          border: none;
        }
    cards:
      - type: grid
        square: false
        columns: 2
        cards:
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_trusa_prim_ajutor
            show_state: false
            show_name: false
            show_icon: false
            show_label: false
            tap_action:
              action: more-info
            custom_fields:
              content: |
                [[[
                  const attr = entity.attributes || {};
                  const zile = parseInt(entity.state) || 0;
                  const stare = attr['Stare'] || '—';
                  const expira = attr['Data expirare'] || '—';
                  const valid = zile >= 0;
                  const color = valid ? (zile < 30 ? '#FF9800' : '#4CAF50') : '#EF4F1A';
                  const bgColor = valid ? (zile < 30 ? 'rgba(255,152,0,0.15)' : 'rgba(76,175,80,0.15)') : 'rgba(239,79,26,0.15)';
                  return `
                    <div style="display:flex;flex-direction:column;align-items:center;gap:8px;">
                      <div style="width:48px;height:48px;border-radius:12px;background:${bgColor};display:flex;align-items:center;justify-content:center;">
                        <ha-icon icon="mdi:medical-bag" style="width:24px;height:24px;color:${color};"></ha-icon>
                      </div>
                      <div style="text-align:center;">
                        <div style="font-size:13px;color:var(--secondary-text-color);">Trusă prim ajutor</div>
                        <div style="font-size:18px;font-weight:700;color:${color};margin-top:2px;">
                          ${valid ? zile + ' zile' : 'EXPIRATĂ'}
                        </div>
                        <div style="font-size:11px;color:var(--secondary-text-color);opacity:0.7;margin-top:2px;">Exp: ${expira}</div>
                      </div>
                    </div>`;
                ]]]
            styles:
              card:
                - background: transparent
                - border: none
                - box-shadow: none
                - padding: 20px 8px
              grid:
                - grid-template-areas: '"content"'
                - grid-template-columns: 1fr
              custom_fields:
                content:
                  - width: 100%
          - type: custom:button-card
            entity: sensor.vehicule_b123abc_extinctor
            show_state: false
            show_name: false
            show_icon: false
            show_label: false
            tap_action:
              action: more-info
            custom_fields:
              content: |
                [[[
                  const attr = entity.attributes || {};
                  const zile = parseInt(entity.state) || 0;
                  const stare = attr['Stare'] || '—';
                  const expira = attr['Data expirare'] || '—';
                  const valid = zile >= 0;
                  const color = valid ? (zile < 30 ? '#FF9800' : '#4CAF50') : '#EF4F1A';
                  const bgColor = valid ? (zile < 30 ? 'rgba(255,152,0,0.15)' : 'rgba(76,175,80,0.15)') : 'rgba(239,79,26,0.15)';
                  return `
                    <div style="display:flex;flex-direction:column;align-items:center;gap:8px;">
                      <div style="width:48px;height:48px;border-radius:12px;background:${bgColor};display:flex;align-items:center;justify-content:center;">
                        <ha-icon icon="mdi:fire-extinguisher" style="width:24px;height:24px;color:${color};"></ha-icon>
                      </div>
                      <div style="text-align:center;">
                        <div style="font-size:13px;color:var(--secondary-text-color);">Extinctor</div>
                        <div style="font-size:18px;font-weight:700;color:${color};margin-top:2px;">
                          ${valid ? zile + ' zile' : 'EXPIRAT'}
                        </div>
                        <div style="font-size:11px;color:var(--secondary-text-color);opacity:0.7;margin-top:2px;">Exp: ${expira}</div>
                      </div>
                    </div>`;
                ]]]
            styles:
              card:
                - background: transparent
                - border: none
                - box-shadow: none
                - padding: 20px 8px
              grid:
                - grid-template-areas: '"content"'
                - grid-template-columns: 1fr
              custom_fields:
                content:
                  - width: 100%
```

---

## 5. Grafic kilometraj

Header cu kilometrajul curent formatat și grafic istoric pe ultimele 30 de zile folosind mini-graph-card.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    icon: ""
    name: GRAFIC KILOMETRAJ
    sub_button:
      main: []
      bottom: []
  - type: custom:stack-in-card
    mode: vertical
    card_mod:
      style: |
        ha-card {
          border-radius: 10px;
          overflow: hidden;
          box-shadow: none;
          border: none;
        }
    cards:
      - type: custom:button-card
        entity: sensor.vehicule_b123abc_kilometraj
        show_state: false
        show_name: false
        show_icon: false
        show_label: false
        tap_action:
          action: more-info
        custom_fields:
          header: |
            [[[
              const v = entity.state || '—';
              const km = parseInt(v);
              const formatted = isNaN(km) ? '—' : km.toLocaleString('ro-RO') + ' km';
              return `
                <div style="display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:center;">
                  <div style="width:56px;height:56px;border-radius:14px;background:rgba(33,150,243,0.15);display:flex;align-items:center;justify-content:center;">
                    <ha-icon icon="mdi:speedometer" style="width:28px;height:28px;color:rgb(33,150,243);"></ha-icon>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:13px;color:var(--secondary-text-color);">Kilometraj curent</div>
                    <div style="font-size:28px;font-weight:700;color:rgb(33,150,243);line-height:1.2;">${formatted}</div>
                  </div>
                </div>`;
            ]]]
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
            - padding: 22px 22px 0
          grid:
            - grid-template-areas: '"header"'
            - grid-template-columns: 1fr
          custom_fields:
            header:
              - width: 100%
      - type: custom:mini-graph-card
        entities:
          - entity: sensor.vehicule_b123abc_kilometraj
            color: rgba(33,150,243,0.8)
        hour24: true
        hours_to_show: 720
        points_per_hour: 0.04
        line_width: 3
        animate: true
        show:
          icon: false
          name: false
          state: false
          graph: line
          fill: false
          labels: false
          points: false
        card_mod:
          style: |
            ha-card {
              background: transparent;
              box-shadow: none;
              border: none;
            }
```

---

## Atribute disponibile per senzor

Referință rapidă cu toate atributele accesibile din JavaScript (`entity.attributes['...']`):

| Senzor | Atribute |
|---|---|
| `informatii` | Nr. înmatriculare, Serie CIV, VIN, Marcă, Model, Motorizare, Combustibil, An fabricație, An prima înmatriculare, Capacitate cilindrică (cm³), Putere (kW), Putere (CP) |
| `rca` | Număr poliță, Companie, Data emitere, Data expirare, Cost (RON), Stare |
| `itp` | Data expirare, Stație, Kilometraj la ITP, Stare |
| `impozit` | Sumă (RON), Scadență, Localitate, Proprietar, Tip proprietate |
| `leasing` | Data expirare, Tip proprietate, Stare |
| `revizie_ulei` | Km ultima revizie, Km următoarea revizie, Data ultima revizie, Km curent |
| `distributie` | Km ultima schimbare, Km următoarea schimbare, Data ultima schimbare, Km curent |
| `anvelope` | Data montare vară, Data montare iarnă, Sezon recomandat |
| `baterie` | Data schimb |
| `placute_frana` | Km ultima schimbare, Km următoarea schimbare, Km curent |
| `discuri_frana` | Km ultima schimbare, Km următoarea schimbare, Km curent |
| `trusa_prim_ajutor` | Data expirare, Stare |
| `extinctor` | Data expirare, Stare |

> **Tip**: Click pe orice card deschide dialogul **More Info** cu toate atributele senzorului respectiv.
