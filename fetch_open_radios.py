"""
Fetches open-source / publicly broadcasted official F1 team radio clips
directly via the free OpenF1 public REST API (zero auth required).
Saves audio clips locally into audio_samples/ for voice modeling and reference.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any

OPENF1_API = "https://api.openf1.org/v1/team_radio"

# Selected drivers mapped to our personas
TARGET_DRIVERS = {
    1: {
        "name": "Max Verstappen",
        "engineer": "Gianpiero Lambiase (GP)",
        "persona": "gp_direct",
    },
    44: {
        "name": "Lewis Hamilton",
        "engineer": "Peter Bonnington (Bono)",
        "persona": "bono_calm",
    },
    14: {
        "name": "Fernando Alonso",
        "engineer": "Aston Martin Pitwall",
        "persona": "alonso_tactician",
    },
    55: {
        "name": "Carlos Sainz",
        "engineer": "Ferrari Pitwall (Riccardo Adami)",
        "persona": "vettel_analyst",
    },
}


def fetch_sample_radios(session_key: int = 9158, limit_per_driver: int = 2):
    os.makedirs("audio_samples", exist_ok=True)
    print("=" * 70)
    print(" OPENF1 PUBLIC TEAM RADIO AUDIO EXTRACTOR")
    print(f" Querying Session Key: {session_key} (Free OpenF1 endpoint)")
    print("=" * 70)

    for driver_num, info in TARGET_DRIVERS.items():
        print(
            f"\n>> Fetching clips for Driver #{driver_num}: {info['name']} & {info['engineer']}..."
        )
        url = f"{OPENF1_API}?session_key={session_key}&driver_number={driver_num}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                clips: list[dict[str, Any]] = json.loads(resp.read().decode("utf-8"))

                if not clips:
                    print(f"   No clips found in session {session_key}.")
                    continue

                downloaded = 0
                for clip in clips[:limit_per_driver]:
                    rec_url = clip.get("recording_url")
                    filename = f"audio_samples/driver_{driver_num}_{info['persona']}_{downloaded + 1}.mp3"

                    if rec_url:
                        print(f"   Downloading: {rec_url}")
                        urllib.request.urlretrieve(rec_url, filename)
                        print(f"   Saved -> {filename}")
                        downloaded += 1

        except (OSError, urllib.error.URLError, KeyError) as e:
            print(f"   Error querying OpenF1 for driver {driver_num}: {e}")


if __name__ == "__main__":
    fetch_sample_radios()
