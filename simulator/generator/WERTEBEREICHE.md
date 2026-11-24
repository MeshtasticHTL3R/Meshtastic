# H‑05 | Wertebereiche des Messwertgenerators

Der [Generator](sensor_generator.py) erzeugt für jeden virtuellen Raum-Node Messwerte im [gemeinsamen JSON-Datenformat v1](../../docs/architektur.md#gemeinsames-json-datenformat-v1). Die Grenzen stehen zentral in `LIMITS`. Jeder Wert wird auf diese Grenzen begrenzt und vor der Ausgabe mit `validate()` geprüft, daher entstehen keine ungültigen Messwerte.

| Messgröße | Feld | Einheit | Min | Max | Startwert | Max. Änderung je Messung |
| --- | --- | --- | --- | --- | --- | --- |
| CO₂ | `co2Ppm` | ppm, Ganzzahl | 400 | 2000 | 600 | ±40 |
| Temperatur | `temperatureC` | °C, 1 Nachkommastelle | 16,0 | 30,0 | 21,0 | ±0,3 |
| Luftfeuchtigkeit | `humidityPct` | % rF, 1 Nachkommastelle | 20,0 | 80,0 | 45,0 | ±1,5 |
| Fensterzustand | `windowOpen` | Boolean | – | – | `false` | Wechsel mit 5 % Wahrscheinlichkeit |

Die Grenzen liegen innerhalb der Regeln von Format v1: `co2Ppm` ist nicht negativ, `temperatureC` endlich, `humidityPct` zwischen 0 und 100.

## Begründung

- **CO₂:** Außenluft hat rund 400 ppm, niedrigere Innenraumwerte sind nicht plausibel. 1000 ppm gilt als Richtwert für gute Raumluft (Pettenkofer-Zahl), 1000 bis 2000 ppm als hygienisch auffällig. Die Obergrenze 2000 ppm reicht, um die CO₂-Warnung aus H‑10 auszulösen.
- **Temperatur:** 16 bis 30 °C deckt einen beheizten Klassenraum ab, vom Auskühlen beim Lüften bis zum voll besetzten Raum.
- **Luftfeuchtigkeit:** 20 bis 80 % deckt trockene Heizperiode und Lüften bei feuchtem Wetter ab. Der Komfortbereich liegt bei etwa 40 bis 60 %.
- **Fenster:** Es wird zufällig geöffnet und geschlossen. So entstehen auch längere Offen-Phasen für die Warnung aus H‑11.

## Realistischer Verlauf

Neuer Wert = alter Wert + Trend + Zufallsrauschen, begrenzt auf die maximale Änderung je Messung.

| Fenster | CO₂ | Temperatur | Luftfeuchte |
| --- | --- | --- | --- |
| geschlossen | +15 ppm | +0,05 °C | +0,3 % |
| geöffnet | −30 ppm | −0,2 °C | −0,8 % |

## Weitere Felder

| Feld | Erzeugung |
| --- | --- |
| `schemaVersion` | immer `1` |
| `roomId` | aus `--rooms`, Standard `raum-1`, `raum-2`, `raum-3` |
| `nodeId` | Meshtasticator-Schema: Node 0 = `!00000010`, Node 1 = `!00000011`, … |
| `measuredAt` | aktuelle Zeit in UTC, sekundengenau, mit `Z` |
| `measurementId` | UUID v5 aus `nodeId` und `measuredAt`. Dieselbe Messung ergibt immer dieselbe ID, der Gateway-Adapter kann sie daher selbst ableiten. |

## Quellen

- [BMLUK: Richtlinie zur Bewertung der Innenraumluft](https://www.bmluk.gv.at/themen/klima-und-umwelt/luft-und-laerm/innenraum/rl_luftqualitaet.html)
- [Umweltbundesamt: Einstufung der CO₂-Konzentration](https://www.umweltbundesamt.de/node/109724)
