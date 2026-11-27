#!/usr/bin/env python3
"""Bereken de verwarmingsbehoefte van een woning.

Methode: som van transmissieverliezen (U x A) plus ventilatieverlies
(0,33 Wh/(m3.K) x ventilatiedebiet), vermenigvuldigd met het
temperatuurverschil binnen/buiten. Jaarverbruik via graaddagen.
"""

import argparse
import json
import sys

WARMTE_CAPACITEIT_LUCH = 0.33
GRADENDAGEN_STANDAARD = 2800
TEMP_BINNEN_STANDAARD = 20.0
TEMP_BUITEN_STANDAARD = -10.0
VENTILATIE_STANDAARD = 150.0

VOORBEELD = {
    "naam": "Voorbeeldwoning (tussenwoning)",
    "temperatuur_binnen": 20.0,
    "temperatuur_buiten_ontwerp": -10.0,
    "ventilatie_debiet": 150.0,
    "graaddagen": 2800,
    "elementen": [
        {"naam": "Gevel (spouw, geisoleerd)", "U": 0.25, "oppervlakte": 120.0},
        {"naam": "Dak (geisoleerd)", "U": 0.20, "oppervlakte": 80.0},
        {"naam": "Vloer op zand", "U": 0.25, "oppervlakte": 80.0},
        {"naam": "Ramen (HR++)", "U": 1.10, "oppervlakte": 25.0},
        {"naam": "Deuren", "U": 1.80, "oppervlakte": 4.0},
    ],
}


def vraag_getal(prompt, standaard):
    while True:
        invoer = input(f"{prompt} [{standaard}]: ").strip().replace(",", ".")
        if not invoer:
            return standaard
        try:
            return float(invoer)
        except ValueError:
            print("Voer een geldig getal in.")


def vraag_ja_nee(prompt, standaard=True):
    standaard_txt = "J/n" if standaard else "j/N"
    while True:
        invoer = input(f"{prompt} [{standaard_txt}]: ").strip().lower()
        if not invoer:
            return standaard
        if invoer in ("j", "ja", "y", "yes"):
            return True
        if invoer in ("n", "nee", "no"):
            return False
        print("Antwoord met j of n.")


def invoer_interactief():
    print("=== Verwarmingsbehoefte woning (interactief) ===")
    print("Druk op Enter om de default tussen haakjes te gebruiken.\n")
    data = {
        "naam": input("Naam van de woning: ").strip() or "Woning",
        "temperatuur_binnen": vraag_getal("Gewenste binnentemperatuur (C)", TEMP_BINNEN_STANDAARD),
        "temperatuur_buiten_ontwerp": vraag_getal("Ontwerp-buitentemperatuur (C)", TEMP_BUITEN_STANDAARD),
        "ventilatie_debiet": vraag_getal("Ventilatiedebiet (m3/h)", VENTILATIE_STANDAARD),
        "elementen": [],
    }
    print("\nVoer de bouwelementen in (leeg bij naam = stoppen):")
    teller = 1
    while True:
        naam = input(f"  Element {teller} naam: ").strip()
        if not naam:
            break
        u = vraag_getal(f"    U-waarde {naam} (W/m2K)", 1.0)
        opp = vraag_getal(f"    Oppervlakte {naam} (m2)", 0.0)
        data["elementen"].append({"naam": naam, "U": u, "oppervlakte": opp})
        teller += 1
    if vraag_ja_nee("\nOok jaarverbruik berekenen via graaddagen?", True):
        data["graaddagen"] = vraag_getal("Aantal graaddagen per jaar", GRADENDAGEN_STANDAARD)
    return data


def bereken(data):
    dt = data["temperatuur_binnen"] - data["temperatuur_buiten_ontwerp"]
    regels = []
    transmissie_totaal = 0.0
    for el in data["elementen"]:
        verlies = el["U"] * el["oppervlakte"]
        transmissie_totaal += verlies
        regels.append({
            "naam": el["naam"],
            "U": el["U"],
            "oppervlakte": el["oppervlakte"],
            "verliesfactor": verlies,
            "vermogen": verlies * dt,
        })
    ventilatie_factor = WARMTE_CAPACITEIT_LUCH * data["ventilatie_debiet"]
    verliesfactor_totaal = transmissie_totaal + ventilatie_factor
    vermogen_totaal = verliesfactor_totaal * dt
    resultaat = {
        "naam": data["naam"],
        "temperatuur_binnen": data["temperatuur_binnen"],
        "temperatuur_buiten_ontwerp": data["temperatuur_buiten_ontwerp"],
        "temperatuurverschil": dt,
        "ventilatie_debiet": data["ventilatie_debiet"],
        "elementen": regels,
        "transmissie_verliesfactor": transmissie_totaal,
        "ventilatie_verliesfactor": ventilatie_factor,
        "verliesfactor_totaal": verliesfactor_totaal,
        "ontwerp_vermogen_w": vermogen_totaal,
        "ontwerp_vermogen_kw": vermogen_totaal / 1000.0,
    }
    if data.get("graaddagen"):
        resultaat["graaddagen"] = data["graaddagen"]
        resultaat["jaarverbruik_kwh"] = verliesfactor_totaal * 24 * data["graaddagen"] / 1000.0
    return resultaat


def print_rapport(res):
    print("\n" + "=" * 60)
    print(f"Rapport: {res['naam']}")
    print("=" * 60)
    print(f"Binnentemperatuur          : {res['temperatuur_binnen']:.1f} C")
    print(f"Ontwerp-buitentemperatuur  : {res['temperatuur_buiten_ontwerp']:.1f} C")
    print(f"Temperatuurverschil        : {res['temperatuurverschil']:.1f} K")
    print(f"Ventilatiedebiet           : {res['ventilatie_debiet']:.0f} m3/h")
    print("-" * 60)
    print(f"{'Element':<28}{'U':>8}{'A (m2)':>9}{'W/K':>9}{'Watt':>10}")
    for el in res["elementen"]:
        print(f"{el['naam']:<28}{el['U']:>8.2f}{el['oppervlakte']:>9.1f}{el['verliesfactor']:>9.1f}{el['vermogen']:>10.0f}")
    print("-" * 60)
    print(f"Transmissie verliesfactor  : {res['transmissie_verliesfactor']:.1f} W/K")
    print(f"Ventilatie verliesfactor   : {res['ventilatie_verliesfactor']:.1f} W/K (0,33 x {res['ventilatie_debiet']:.0f} m3/h)")
    print(f"Totaal verliesfactor H     : {res['verliesfactor_totaal']:.1f} W/K")
    print("-" * 60)
    print(f"ONTWERP-VERMOGEN           : {res['ontwerp_vermogen_w']:.0f} W = {res['ontwerp_vermogen_kw']:.2f} kW")
    if "jaarverbruik_kwh" in res:
        print(f"JAARVERBRUIK (graaddagen {res['graaddagen']:.0f}): {res['jaarverbruik_kwh']:.0f} kWh/jaar")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Bereken de verwarmingsbehoefte van een woning.")
    parser.add_argument("--demo", action="store_true", help="Draai met voorbeeldgegevens van een tussenwoning.")
    parser.add_argument("--json", metavar="BESTAND", help="Lees invoergegevens uit een JSON-bestand.")
    parser.add_argument("--uitvoer-json", metavar="BESTAND", help="Schrijf het resultaat als JSON weg.")
    args = parser.parse_args()

    if args.demo:
        data = VOORBEELD
    elif args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = invoer_interactief()

    if not data.get("elementen"):
        print("Geen bouwelementen opgegeven; nothing to calculate.", file=sys.stderr)
        sys.exit(1)

    resultaat = bereken(data)
    print_rapport(resultaat)

    if args.uitvoer_json:
        with open(args.uitvoer_json, "w", encoding="utf-8") as f:
            json.dump(resultaat, f, indent=2, ensure_ascii=False)
        print(f"Resultaat weggeschreven naar {args.uitvoer_json}")


if __name__ == "__main__":
    main()
