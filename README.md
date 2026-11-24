# Meshtastic

Dieses Projekt simuliert ein Meshtastic-Netz für Raumluft- und Fenstermesswerte. Das Backend verarbeitet und speichert die Messdaten, das Dashboard zeigt sie an.

| Ordner | Inhalt |
| --- | --- |
| [simulator/](simulator/) | Docker- und Meshtasticator-Einrichtung für H-02 |
| [backend/](backend/) | Übernahme, Verarbeitung und Speicherung der Messdaten |
| [dashboard/](dashboard/) | Weboberfläche für Messwerte und Warnungen |

Backend und Dashboard enthalten derzeit je eine README. Der Simulator lässt sich mit der folgenden Anleitung lokal starten.

[Architektur und Schnittstellen (H-01)](docs/architektur.md) · [Projektprotokoll](docs/projektprotokoll.md)

## Arbeitsplatz unter Windows einrichten

1. Installiere [Git für Windows](https://git-scm.com/install/windows) und [VS Code](https://code.visualstudio.com/download). Dein GitHub-Konto braucht Zugriff auf das private Projekt-Repo.
2. Installiere [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) mit dem WSL-2-Backend. Falls WSL fehlt, führe `wsl --install` in PowerShell als Administrator aus und starte Windows neu. Siehe [WSL-Anleitung](https://learn.microsoft.com/de-de/windows/wsl/install).
3. Installiere [Python 3.12 für Windows](https://www.python.org/downloads/windows/) und starte Docker Desktop. Öffne danach ein neues PowerShell-Terminal und prüfe die Installation.

```powershell
git --version
py -3.12 --version
docker version
docker run --rm hello-world
```

Bei `docker version` sollten **Client** und **Server** erscheinen. Der Testcontainer gibt `Hello from Docker!` aus.

## Projekt in VS Code öffnen

Öffne PowerShell in dem Ordner, der die beiden Klone enthalten soll. Wenn du das Projekt bereits geklont hast, öffne deinen vorhandenen Projektordner in VS Code.

```powershell
git clone https://github.com/dunollie/Meshtastic.git
code .\Meshtastic
```

## Simulator einrichten und testen

Öffne in VS Code ein PowerShell-Terminal im Projektordner. Klone den offiziellen Meshtasticator einmal als Nachbarordner. Die Anleitung verwendet den getesteten Stand des [Meshtasticator](https://github.com/meshtastic/Meshtasticator/blob/17ceb8231079d87b070abc6132181e4c6b20202d/INTERACTIVE_SIM.md).

```powershell
Set-Location ..
git clone https://github.com/meshtastic/Meshtasticator.git
Set-Location .\Meshtasticator
git switch --detach 17ceb8231079d87b070abc6132181e4c6b20202d

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt docker
```

Falls der Nachbarordner und die Python-Umgebung schon eingerichtet sind, kannst du diesen Schritt überspringen. Starte den Simulator bei laufendem Docker Desktop aus dem Projektordner `Meshtastic` mit einem virtuellen Knoten.

```powershell
..\Meshtasticator\.venv\Scripts\python.exe -X utf8 .\simulator\start.py 1
```

Der [Starter](simulator/start.py) prüft den Meshtasticator-Commit und startet die Firmware über den fest hinterlegten Docker-Digest. `-X utf8` sorgt dafür, dass die Knotentabelle auch unter Windows korrekt ausgegeben wird. Gib am Simulator-Prompt `nodes 0` ein. Wenn die Tabelle **Node 0** anzeigt, war der Starttest erfolgreich. Mit `exit` beendest du den Simulator.

Das festgelegte Docker-Image enthält die getestete Firmware `2.7.26.54e0d8d`.

## Gemeinsam arbeiten

Erstelle für jede Jira-Aufgabe einen Branch vom aktuellen `main`. Die folgenden Befehle führst du im **Projektordner Meshtastic** aus. Wenn es den Branch für deine Aufgabe schon gibt, verwende den vorhandenen Branch.

```powershell
git switch main
git pull --ff-only
git switch -c mes-38-meshtasticator
```

Lege projektspezifische Simulator-Dateien in `simulator/` ab. Der offizielle Meshtasticator und seine Python-Umgebung liegen im separaten Nachbarordner. Committe deine Änderungen auf dem Aufgabenbranch, pushe ihn und öffne auf GitHub einen Pull Request nach `main`.

- [Jira-Projekt Meshtastic](https://topocheckdiplomarbeit.atlassian.net/browse/MES)
- [H-02 – Docker-Umgebung und Meshtasticator](https://topocheckdiplomarbeit.atlassian.net/browse/MES-38)
