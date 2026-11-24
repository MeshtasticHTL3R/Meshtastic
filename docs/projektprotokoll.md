# Projektprotokoll

## 24. November 2026 · H‑01 Architekturentwurf

| Entscheidung zur Freigabe | Begründung |
| --- | --- |
| Ein Repository mit Simulator, Backend und Dashboard | Die drei Entwicklungsbereiche verwenden gemeinsame Schnittstellen und können separat umgesetzt werden. |
| Meshtasticator und Docker für die virtuelle Firmware | Die Teammitglieder können den Datenfluss mit virtuellen Raum-Nodes und einem Gateway testen. |
| Gateway-Adapter als Übergang zur HTTP-API | Geräteanschluss und Funkformat bleiben im Simulatorbereich. Backend und Dashboard arbeiten mit einem stabilen Datenvertrag. |
| Versioniertes JSON und eindeutige Messungs-ID | Gemeinsame Einheiten und reproduzierbare Testdaten vereinfachen die Integration. Wiederholte Übertragungen erzeugen keine doppelten Messungen. |
| SQLite für den ersten lokalen Projektstand | Zentrale Historie mit wenig Einrichtungsaufwand. Der Zugriff erfolgt über das Backend. |
| Warnlogik im Backend, Darstellung im Dashboard | Grenzwerte und Zeitregeln werden an einer Stelle ausgewertet. |

Details und Beispiele stehen in der [Architektur und Schnittstellenbeschreibung](architektur.md).

### Teamprüfung für MES‑37

- [ ] Kilian Kroboth prüft Simulator, Raum-Nodes und Gateway.
- [ ] Ilayda E prüft Datenformat, Backend-API und Speicherung.
- [ ] Victoria Strohschneider prüft Dashboard-API und Warnungen.

Die Zustimmung wird nach der Prüfung mit Name und Datum ergänzt. Die Funkcodierung und die konkreten Warnschwellen werden in den zugehörigen Implementierungstickets festgelegt.
