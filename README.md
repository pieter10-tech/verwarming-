# Verwarmingsbehoefte woning

Python-programma om de verwarmingsbehoefte van een woning te bepalen.

## Methode

- **Transmissieverlies**: per bouwelement `U [W/m2K] x oppervlakte [m2]` = verliesfactor in W/K
- **Ventilatieverlies**: `0,33 Wh/(m3.K) x ventilatiedebiet [m3/h]` = W/K
- **Ontwerp-vermogen**: totale verliesfactor H [W/K] x (binnen - buiten temperatuur) = Watt
- **Jaarverbruik**: `H x 24 x graaddagen / 1000` = kWh/jaar (standaard 2800 graaddagen, bijv. De Bilt)

## Gebruik

```bash
# Interactief: stel vragen in via het toetsenbord
python3 verwarmingsbehoefte.py

# Met voorbeeldgegevens (tussenwoning)
python3 verwarmingsbehoefte.py --demo

# Met eigen gegevens uit een JSON-bestand (zie voorbeeld_woning.json)
python3 verwarmingsbehoefte.py --json mijn_woning.json

# Resultaat ook wegschrijven als JSON
python3 verwarmingsbehoefte.py --json mijn_woning.json --uitvoer-json resultaat.json
```

## Invoer (JSON)

```json
{
  "naam": "Mijn woning",
  "temperatuur_binnen": 20.0,
  "temperatuur_buiten_ontwerp": -10.0,
  "ventilatie_debiet": 150.0,
  "graaddagen": 2800,
  "elementen": [
    {"naam": "Gevel", "U": 0.25, "oppervlakte": 120.0},
    {"naam": "Ramen (HR++)", "U": 1.10, "oppervlakte": 25.0}
  ]
}
```

`graaddagen` is optioneel; als deze ontbreekt wordt alleen het ontwerp-vermogen berekend.

## Voorbeeld van de uitvoer (demo)

Ontwerp-vermogen ca. **4,5 kW** en jaarverbruik ca. **10.100 kWh/jaar** voor de
voorbeeld-tussenwoning bij 20 C binnen, -10 C buiten en 150 m3/h ventilatie.

## Opmerking

Dit is een vereenvoudigde schatting voor ontwerpdoeleinden. Voor een
officiele berekening (bijv. volgens NTA 8800 / ISSO-publicatie 51) zijn
aanvullende correcties nodig (koudebruggen, infiltratie, interne warmtewinsten,
zonnestraling, opstooktoeslag per vertrek).
