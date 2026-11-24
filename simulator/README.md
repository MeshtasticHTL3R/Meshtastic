# Simulator

Für H-02 verwendet [start.py](start.py) den getesteten Meshtasticator-Commit
und das offizielle Firmware-Image mit festem Docker-Digest. Der Starter prüft
den Commit im Nachbar-Checkout und übergibt den Image-Digest direkt an
Meshtasticator. Das Docker-SDK lädt das Image bei Bedarf herunter.

Die [Einrichtung und der Starttest](../README.md#simulator-einrichten-und-testen)
stehen in der Haupt-README.
