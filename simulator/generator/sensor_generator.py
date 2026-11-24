"""H-05: Realistische Messwerte für die virtuellen Raum-Nodes erzeugen.

Erzeugt CO2-, Temperatur-, Luftfeuchte- und Fensterwerte im gemeinsamen JSON-Datenformat v1 (siehe docs/architektur.md).

Die Werte entstehen als Random Walk: Jeder neue Wert hängt vom vorherigen ab, und ein offenes Fenster senkt CO2, Temperatur und Luftfeuchte. Alle Werte werden
auf die Grenzen in LIMITS begrenzt, ungültige Messwerte sind dadurch ausgeschlossen.

"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

SCHEMA_VERSION = 1

# Wertebereiche, dokumentiert in WERTEBEREICHE.md
LIMITS = {
    "co2Ppm": (400, 2000),
    "temperatureC": (16.0, 30.0),
    "humidityPct": (20.0, 80.0),
}

# Startwerte: typischer Klassenraum zu Unterrichtsbeginn
START = {"co2Ppm": 600.0, "temperatureC": 21.0, "humidityPct": 45.0}

# Maximale Änderung pro Messung, verhindert unrealistische Sprünge
MAX_STEP = {"co2Ppm": 40.0, "temperatureC": 0.3, "humidityPct": 1.5}

# Trend pro Messung: (Fenster zu, Fenster offen)
TREND = {
    "co2Ppm": (15.0, -30.0),
    "temperatureC": (0.05, -0.2),
    "humidityPct": (0.3, -0.8),
}

# Wahrscheinlichkeit pro Messung, dass das Fenster umgeschaltet wird
WINDOW_TOGGLE_PROBABILITY = 0.05

# Fester Namensraum: dieselbe Node und Messzeit ergeben immer dieselbe measurementId
MEASUREMENT_NAMESPACE = uuid.UUID("3f6c1c0e-5d1a-4c8e-9b7a-6d2f4e8a1b05")

# Standard-Räume. Node-IDs entsprechen dem Meshtasticator-Schema (Node 0 = !00000010).
DEFAULT_ROOMS = ["raum-1", "raum-2", "raum-3"]


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_time(t: datetime) -> str:
    """ISO-8601 in UTC mit Z, auf Sekunden genau, z. B. 2026-11-24T13:30:00Z."""
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def meshtasticator_node_id(index: int) -> str:
    """Node-ID im Meshtasticator: Node 0 ist !00000010, Node 1 ist !00000011 usw."""
    return f"!{index + 0x10:08x}"


def measurement_id(node_id: str, measured_at: str) -> str:
    """Stabile UUID aus Node-ID und Messzeit (gleiche Eingabe = gleiche ID)."""
    return str(uuid.uuid5(MEASUREMENT_NAMESPACE, f"{node_id}/{measured_at}"))


@dataclass
class RoomNode:
    room_id: str
    node_id: str
    co2: float = START["co2Ppm"]
    temperature: float = START["temperatureC"]
    humidity: float = START["humidityPct"]
    window_open: bool = False

    def step(self, rng: random.Random, now: datetime | None = None) -> dict:
        """Erzeugt die nächste Messung als dict im JSON-Format v1."""
        if rng.random() < WINDOW_TOGGLE_PROBABILITY:
            self.window_open = not self.window_open

        self.co2 = self._next("co2Ppm", self.co2, rng)
        self.temperature = self._next("temperatureC", self.temperature, rng)
        self.humidity = self._next("humidityPct", self.humidity, rng)

        measured_at = format_time(now or utc_now())
        return {
            "schemaVersion": SCHEMA_VERSION,
            "measurementId": measurement_id(self.node_id, measured_at),
            "roomId": self.room_id,
            "nodeId": self.node_id,
            "measuredAt": measured_at,
            "co2Ppm": int(round(self.co2)),
            "temperatureC": round(self.temperature, 1),
            "humidityPct": round(self.humidity, 1),
            "windowOpen": self.window_open,
        }

    def _next(self, key: str, current: float, rng: random.Random) -> float:
        step = MAX_STEP[key]
        trend = TREND[key][1 if self.window_open else 0]
        delta = clamp(trend + rng.uniform(-step, step), -step, step)
        lo, hi = LIMITS[key]
        return clamp(current + delta, lo, hi)


def create_nodes(room_ids: list[str]) -> list[RoomNode]:
    return [RoomNode(room, meshtasticator_node_id(i)) for i, room in enumerate(room_ids)]


def to_json(measurement: dict) -> str:
    """Kompakte JSON-Zeile ohne Leerzeichen."""
    return json.dumps(measurement, separators=(",", ":"), ensure_ascii=False)


FIELDS = ["schemaVersion", "measurementId", "roomId", "nodeId", "measuredAt",
          "co2Ppm", "temperatureC", "humidityPct", "windowOpen"]


def validate(m: dict) -> None:
    """Prüft eine Messung gegen JSON-Format v1 und die Wertebereiche.

    Wirft ValueError bei fehlenden Feldern, falschen Typen oder ungültigen Werten.
    """
    missing = [f for f in FIELDS if f not in m]
    if missing:
        raise ValueError(f"Pflichtfelder fehlen: {missing}")
    extra = [f for f in m if f not in FIELDS]
    if extra:
        raise ValueError(f"Unbekannte Felder: {extra}")

    if type(m["schemaVersion"]) is not int or m["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("schemaVersion muss genau 1 sein")
    try:
        uuid.UUID(m["measurementId"])
    except (ValueError, TypeError, AttributeError):
        raise ValueError("measurementId ist keine UUID") from None
    for key in ("roomId", "nodeId"):
        if not isinstance(m[key], str) or not m[key]:
            raise ValueError(f"{key} muss eine nicht leere Zeichenkette sein")
    try:
        datetime.strptime(m["measuredAt"], "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        raise ValueError("measuredAt muss UTC im Format JJJJ-MM-TTThh:mm:ssZ sein") from None

    if type(m["co2Ppm"]) is not int:
        raise ValueError("co2Ppm muss eine Ganzzahl sein")
    for key in ("temperatureC", "humidityPct"):
        if type(m[key]) not in (int, float) or not math.isfinite(m[key]):
            raise ValueError(f"{key} muss eine endliche Zahl sein")
    if type(m["windowOpen"]) is not bool:
        raise ValueError("windowOpen muss true oder false sein")

    for key, (lo, hi) in LIMITS.items():
        if not lo <= m[key] <= hi:
            raise ValueError(f"{key}={m[key]} liegt außerhalb von {lo}..{hi}")


def run(nodes: list[RoomNode], rng: random.Random, interval: float, count: int,
        emit: Callable[[str], None] = print, clock: Callable[[], datetime] = utc_now,
        sleep: Callable[[float], None] = time.sleep) -> None:
    """Erzeugt in jeder Runde eine Messung pro Node, count=0 läuft endlos."""
    rounds = 0
    while count == 0 or rounds < count:
        now = clock()
        for node in nodes:
            m = node.step(rng, now)
            validate(m)
            emit(to_json(m))
        rounds += 1
        if count == 0 or rounds < count:
            sleep(interval)


def main() -> None:
    p = argparse.ArgumentParser(description="Messwertgenerator für virtuelle Raum-Nodes (H-05)")
    p.add_argument("--rooms", default=",".join(DEFAULT_ROOMS),
                   help="Raum-IDs, kommagetrennt (Standard: raum-1,raum-2,raum-3)")
    p.add_argument("--interval", type=float, default=10.0,
                   help="Sekunden zwischen den Messungen, mindestens 1 (Standard: 10)")
    p.add_argument("--count", type=int, default=0, help="Anzahl Runden, 0 = endlos")
    p.add_argument("--seed", type=int, default=None, help="Seed für reproduzierbare Werte")
    args = p.parse_args()

    rooms = [r.strip() for r in args.rooms.split(",") if r.strip()]
    if not rooms:
        p.error("mindestens eine Raum-ID angeben")
    if args.interval < 1:
        p.error("--interval muss mindestens 1 Sekunde sein (measuredAt ist sekundengenau)")

    try:
        run(create_nodes(rooms), random.Random(args.seed), args.interval, args.count,
            emit=lambda line: print(line, flush=True))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
