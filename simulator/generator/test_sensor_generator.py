"""
Tests für H-05
Ausführen: py -3.12 -m pytest simulator\\generator -v
"""

import json
import random
from datetime import datetime, timedelta, timezone

import pytest

import sensor_generator as sg

RUNS = 10_000
START = datetime(2026, 11, 24, 8, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def measurements():
    rng = random.Random(42)
    node = sg.RoomNode("raum-1", "!00000010")
    return [node.step(rng, START + timedelta(seconds=10 * i)) for i in range(RUNS)]


@pytest.mark.parametrize("key", ["co2Ppm", "temperatureC", "humidityPct"])
def test_messwerte_im_definierten_bereich(measurements, key):
    lo, hi = sg.LIMITS[key]
    values = [m[key] for m in measurements]
    assert all(lo <= v <= hi for v in values)
    # der Bereich wird auch tatsächlich ausgenutzt, nicht nur der Startwert
    assert max(values) - min(values) > (hi - lo) * 0.3


def test_fenster_offen_und_geschlossen(measurements):
    assert {m["windowOpen"] for m in measurements} == {True, False}


def test_keine_unrealistischen_spruenge(measurements):
    for a, b in zip(measurements, measurements[1:]):
        assert abs(a["co2Ppm"] - b["co2Ppm"]) <= sg.MAX_STEP["co2Ppm"] + 1
        assert abs(a["temperatureC"] - b["temperatureC"]) <= sg.MAX_STEP["temperatureC"] + 0.1
        assert abs(a["humidityPct"] - b["humidityPct"]) <= sg.MAX_STEP["humidityPct"] + 0.1


def test_offenes_fenster_senkt_co2(monkeypatch):
    monkeypatch.setattr(sg, "WINDOW_TOGGLE_PROBABILITY", 0.0)
    node = sg.RoomNode("raum-1", "!00000010", co2=1500, window_open=True)
    rng = random.Random(1)
    for i in range(20):
        node.step(rng, START + timedelta(seconds=i))
    assert node.co2 < 1500


def test_geschlossenes_fenster_erhoeht_co2(monkeypatch):
    monkeypatch.setattr(sg, "WINDOW_TOGGLE_PROBABILITY", 0.0)
    node = sg.RoomNode("raum-1", "!00000010", co2=600, window_open=False)
    rng = random.Random(1)
    for i in range(20):
        node.step(rng, START + timedelta(seconds=i))
    assert node.co2 > 600


def test_regelmaessig_neu_erzeugt():
    lines, sleeps = [], []
    clock_times = iter(START + timedelta(seconds=10 * i) for i in range(5))
    nodes = sg.create_nodes(sg.DEFAULT_ROOMS)
    sg.run(nodes, random.Random(3), interval=10, count=5,
           emit=lines.append, clock=lambda: next(clock_times), sleep=sleeps.append)
    assert len(lines) == 5 * 3  # 5 Runden x 3 Raum-Nodes
    assert sleeps == [10] * 4  # zwischen den Runden wird gewartet
    parsed = [json.loads(line) for line in lines]
    assert len({m["measurementId"] for m in parsed}) == len(parsed)
    assert len({m["measuredAt"] for m in parsed}) == 5


def test_json_format_v1(measurements):
    for m in measurements[:200]:
        line = sg.to_json(m)
        parsed = json.loads(line)
        sg.validate(parsed)
        assert list(parsed) == sg.FIELDS
        assert parsed["schemaVersion"] == 1
        assert parsed["measuredAt"].endswith("Z")


def test_beispiel_aus_architektur_ist_gueltig():
    beispiel = {
        "schemaVersion": 1,
        "measurementId": "79ed8360-6341-4b35-b1e7-aa818837d776",
        "roomId": "5cn",
        "nodeId": "!00000010",
        "measuredAt": "2026-11-24T13:30:00Z",
        "co2Ppm": 980,
        "temperatureC": 22.4,
        "humidityPct": 45.2,
        "windowOpen": False,
    }
    sg.validate(beispiel)


def test_measurement_id_stabil_und_eindeutig():
    a = sg.measurement_id("!00000010", "2026-11-24T13:30:00Z")
    assert a == sg.measurement_id("!00000010", "2026-11-24T13:30:00Z")
    assert a != sg.measurement_id("!00000011", "2026-11-24T13:30:00Z")
    assert a != sg.measurement_id("!00000010", "2026-11-24T13:30:10Z")


def test_node_ids_wie_im_meshtasticator():
    nodes = sg.create_nodes(["a", "b", "c"])
    assert [n.node_id for n in nodes] == ["!00000010", "!00000011", "!00000012"]


@pytest.mark.parametrize("feld, wert", [
    ("co2Ppm", 5000), ("co2Ppm", -1), ("co2Ppm", 800.5), ("co2Ppm", True),
    ("temperatureC", float("nan")), ("temperatureC", 45.0),
    ("humidityPct", 101.0), ("windowOpen", "false"), ("windowOpen", 0),
    ("schemaVersion", 2), ("measurementId", "abc"), ("roomId", ""),
    ("measuredAt", "2026-11-24 13:30:00"),
])
def test_ungueltige_werte_werden_erkannt(feld, wert):
    m = sg.RoomNode("raum-1", "!00000010").step(random.Random(0), START)
    m[feld] = wert
    with pytest.raises(ValueError):
        sg.validate(m)


def test_fehlendes_feld_wird_erkannt():
    m = sg.RoomNode("raum-1", "!00000010").step(random.Random(0), START)
    del m["windowOpen"]
    with pytest.raises(ValueError):
        sg.validate(m)
