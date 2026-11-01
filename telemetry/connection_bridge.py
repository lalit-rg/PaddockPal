"""
PitwallKing Connection Manager & Hardware Bridge.
Handles multi-source ingestion:
1. PS5 / Xbox (Cross-device UDP Forwarding & Auto-IP Discovery)
2. PC Local (Windows Shared Memory MMF for ACC / iRacing)
3. Real Motorsport Pitwall Software (MoTeC i2 / McLaren ATLAS CSV Stream)
"""

import socket
from enum import Enum
from typing import Any

from telemetry.adapter_interface import SimGameType


class PlatformType(Enum):
    PC = "pc"
    PS5 = "ps5"
    XBOX = "xbox"
    PRO_MOTORSPORT = "pro_motorsport"  # MoTeC / McLaren ATLAS stream


class TelemetryConnectionConfig:
    def __init__(
        self,
        platform: PlatformType = PlatformType.PC,
        game: SimGameType = SimGameType.F1_23_24_25,
        target_ip: str = "0.0.0.0",
        port: int = 20777,
        motec_csv_path: str | None = None,
    ):
        self.platform = platform
        self.game = game
        self.target_ip = target_ip
        self.port = port
        self.motec_csv_path = motec_csv_path


class UniversalConnectionBridge:
    """
    Central connection router.
    Detects local IP for PS5/Xbox users, manages incoming sockets or memory maps,
    and feeds the canonical NormalizedTelemetryFrame pipeline.
    """

    @staticmethod
    def get_local_lan_ip() -> str:
        """
        Retrieves the PC's Wi-Fi / Ethernet LAN IP (e.g., 192.168.1.45)
        so PS5 / Xbox users know what destination IP to enter into their console.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't need to be reachable
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except OSError:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    @staticmethod
    def get_supported_entry_points() -> list[dict[str, Any]]:
        lan_ip = UniversalConnectionBridge.get_local_lan_ip()
        return [
            {
                "id": "ps5_f1",
                "title": "PlayStation 5 (PS5) / Xbox Console",
                "platform": "Console (PS5 / Xbox Series X)",
                "game": "EA Sports F1 (23/24/25)",
                "how_it_connects": "UDP Broadcast over Home Wi-Fi / LAN",
                "instructions": [
                    "Ensure your PS5/Xbox is connected to the same Wi-Fi/router as this PC.",
                    "In F1 25 on your PS5: Settings -> Telemetry Settings.",
                    "Set UDP Telemetry: ON.",
                    f"Set UDP IP Address to your PC LAN IP: {lan_ip}",
                    "Set UDP Port: 20777 | Send Rate: 60Hz.",
                    "Save and start driving on your console.",
                ],
            },
            {
                "id": "pc_f1",
                "title": "PC - EA Sports F1 (23/24/25)",
                "platform": "PC (Steam / EA App)",
                "game": "F1 25",
                "how_it_connects": "Localhost UDP Socket",
                "instructions": [
                    "In F1 25: Settings -> Telemetry Settings.",
                    "Set UDP Telemetry: ON | IP: 127.0.0.1 | Port: 20777 | Rate: 60Hz.",
                ],
            },
            {
                "id": "pc_acc",
                "title": "PC - Assetto Corsa & ACC",
                "platform": "PC",
                "game": "Assetto Corsa Competizione (GT3 / GT4)",
                "how_it_connects": "Windows Shared Memory (Zero-Lag MMF)",
                "instructions": [
                    "Zero configuration needed! ACC broadcasts natively to Windows memory.",
                    "Launch ACC and hit the track.",
                ],
            },
            {
                "id": "pc_iracing",
                "title": "PC - iRacing",
                "platform": "PC",
                "game": "iRacing Motorsport Simulation",
                "how_it_connects": "iRacing Official SDK / pyirsdk pipe",
                "instructions": [
                    "Launch iRacing session. PitwallKing connects to the telemetry pipe automatically."
                ],
            },
            {
                "id": "motec_atlas",
                "title": "Professional Motorsport (MoTeC i2 / McLaren ATLAS)",
                "platform": "Pro Pitwall Software (CSV / Live Telemetry Stream)",
                "game": "Real Trackside / Sim Log",
                "how_it_connects": "ATLAS / MoTeC CSV Export Stream",
                "instructions": [
                    "Export session telemetry to CSV format from MoTeC i2 Pro or McLaren ATLAS.",
                    "Provide file or streaming socket; PitwallKing parses channels directly.",
                ],
            },
        ]
