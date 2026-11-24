# Simulator · H‑02

Der [Starter](start.py) prüft, ob der Meshtasticator-Checkout auf dem getesteten Commit steht. Er übergibt das Firmware-Image mit festem Docker-Digest direkt an Meshtasticator. Wenn das Image lokal fehlt, lädt Docker es beim Start nach.

## Einmalige Einrichtung

Installiere Git, Python 3.12 und Docker Desktop gemäß der [Windows-Einrichtung](../README.md#arbeitsplatz-unter-windows-einrichten). Der offizielle Meshtasticator liegt als Nachbarordner neben dem Projekt. So sieht es auf dem Schulrechner aus:

```text
C:\Schule\ITP\5CN\
├── Meshtastic\       Projekt-Repository
└── Meshtasticator\   offizieller Simulator
```

Öffne in VS Code über **Terminal → Neues Terminal** ein PowerShell-Terminal im Projektordner `Meshtastic`. Falls der Nachbarordner bereits existiert, überspringe den Klonbefehl. Wenn der Checkout und die Python-Umgebung bereits eingerichtet sind, gehe direkt zum Starttest.

```powershell
Set-Location ..
git clone https://github.com/meshtastic/Meshtasticator.git
Set-Location .\Meshtasticator
git switch --detach 17ceb8231079d87b070abc6132181e4c6b20202d
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt docker
Set-Location ..\Meshtastic
```

## Simulator starten und prüfen

1. **Docker starten.** Öffne Docker Desktop und warte, bis die Engine läuft. `docker version` zeigt dann einen Abschnitt **Server** an.
2. **Einen Knoten starten.** Führe den folgenden Befehl im PowerShell-Terminal aus dem Projektordner `Meshtastic` aus. `-X utf8` sorgt unter Windows für die korrekte Ausgabe der Knotentabelle.

   ```powershell
   ..\Meshtasticator\.venv\Scripts\python.exe -X utf8 .\simulator\start.py 1
   ```

3. **Knoten prüfen.** Im Terminal erscheinen `Docker container with name Meshtastic is started.` und danach der Prompt `(Cmd)`. Wechsle vom Fenster mit der Knotenposition zurück zum selben Terminal und gib `nodes 0` ein. In der Tabelle sollte **Node 0** mit **PORTDUINO** als Hardware stehen.
4. **Firmware prüfen.** Öffne über **+** im Terminalbereich ein zweites PowerShell-Terminal, während der Simulator läuft.

   ```powershell
   docker exec Meshtastic cat /home/out_0.log
   ```

   Das Log sollte `Running in simulated mode.` und die Firmware-Version `2.7.26.54e0d8d` enthalten.
5. **Simulator beenden.** Gib im ersten Terminal am Prompt `(Cmd)` den Befehl `exit` ein. Der Simulator meldet `Closing all nodes...` und PowerShell übernimmt wieder. Der Testcontainer wird automatisch entfernt.


## Verifizierter Starttest

Am 24. November 2026 wurde die Anleitung unter Windows mit einem frischen
Projekt-Checkout auf `aa0bb6e`, einem separaten Meshtasticator-Checkout und
einer neu eingerichteten Python-3.12-Umgebung getestet. Docker Desktop und
das Firmware-Image waren auf dem Rechner bereits vorhanden.

- `nodes 0` zeigte **Node 0** (`!00000010`) mit **PORTDUINO** an.
- Docker meldete den in `start.py` festgelegten Image-Digest.
- Das Firmware-Log enthielt `Running in simulated mode.` und die Version
  `2.7.26.54e0d8d`.
- `exit` beendete den Simulator mit Exit-Code 0. Der Testcontainer wurde
  automatisch entfernt.

Messwerte für die Raum-Nodes erzeugt der [Messwertgenerator (H‑05)](generator/README.md).