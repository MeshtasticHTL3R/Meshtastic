# Messwertgenerator · H‑05

Erzeugt realistische CO₂-, Temperatur-, Luftfeuchte- und Fensterwerte für die virtuellen Raum-Nodes. Jede Messung wird als eine Zeile im [JSON-Datenformat v1](../../docs/architektur.md#gemeinsames-json-datenformat-v1) ausgegeben. Wertebereiche und Begründung stehen in [WERTEBEREICHE.md](WERTEBEREICHE.md).

## Starten

Führe die Befehle im Projektordner `Meshtastic` aus. Der Generator braucht nur Python 3.12 ohne Zusatzpakete.

```powershell
py -3.12 simulator\generator\sensor_generator.py --interval 5
```

Alle 5 Sekunden erscheint pro Raum-Node eine Zeile wie diese:

```json
{"schemaVersion":1,"measurementId":"4ecdebef-b06f-59e9-a590-07ee48345706","roomId":"raum-1","nodeId":"!00000010","measuredAt":"2026-11-24T15:45:19Z","co2Ppm":640,"temperatureC":21.2,"humidityPct":44.6,"windowOpen":false}
```

Mit `Strg + C` beendest du den Generator.

| Option | Bedeutung | Standard |
| --- | --- | --- |
| `--rooms` | Raum-IDs, kommagetrennt. Die Anzahl bestimmt die Anzahl der Raum-Nodes. | `raum-1,raum-2,raum-3` |
| `--interval` | Sekunden zwischen den Messungen, mindestens 1 | `10` |
| `--count` | Anzahl der Runden, `0` läuft endlos | `0` |
| `--seed` | Fester Startwert für reproduzierbare Messreihen | zufällig |

## Testen

```powershell
py -3.12 -m pip install pytest
py -3.12 -m pytest simulator\generator -v
```

Die Tests prüfen alle vier Messgrößen über 10.000 Messungen, das JSON-Format v1, die regelmäßige Erzeugung und das Erkennen ungültiger Werte.
