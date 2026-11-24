"""Start the pinned Meshtasticator and firmware from the local project checkout."""

from pathlib import Path
import os
import runpy
import subprocess
import sys

MESHTASTICATOR_COMMIT = "17ceb8231079d87b070abc6132181e4c6b20202d"
FIRMWARE_IMAGE = (
    "meshtastic/meshtasticd@"
    "sha256:23e92b1331a3a471eaef0c63cbca4365ca40b3111a9781cfdbe5a5114e5773d4"
)


def main():
    upstream = Path(__file__).resolve().parents[2] / "Meshtasticator"
    entrypoint = upstream / "interactiveSim.py"
    if not entrypoint.is_file():
        raise SystemExit(f"Meshtasticator nicht gefunden: {upstream}")

    commit = subprocess.check_output(
        ["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != MESHTASTICATOR_COMMIT:
        raise SystemExit(
            f"Erwarteter Meshtasticator-Commit: {MESHTASTICATOR_COMMIT}. "
            f"Aktueller Commit: {commit}."
        )

    os.chdir(upstream)
    sys.path.insert(0, str(upstream))
    from lib import interactive

    interactive.DEVICE_SIM_DOCKER_IMAGE = FIRMWARE_IMAGE
    sys.argv = [str(entrypoint), *sys.argv[1:], "-d"]
    runpy.run_path(str(entrypoint), run_name="__main__")


if __name__ == "__main__":
    main()
