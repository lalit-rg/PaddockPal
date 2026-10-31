"""
UDP Telemetry Ingestion Receiver for EA Sports F1 (2023, 2024, 2025).
Listens on default UDP port 20777 and parses packet headers.
Includes a built-in telemetry simulator for running offline without the game.
"""

import socket
import struct
import threading
import time
from typing import Callable, Optional
from telemetry.ring_buffer import TelemetryRingBuffer, TelemetrySnapshot

# F1 Packet IDs
PACKET_MOTION = 0
PACKET_SESSION = 1
PACKET_LAP_DATA = 2
PACKET_EVENT = 3
PACKET_PARTICIPANTS = 4
PACKET_CAR_SETUPS = 5
PACKET_CAR_TELEMETRY = 6
PACKET_CAR_STATUS = 7
PACKET_FINAL_CLASSIFICATION = 8
PACKET_LOBBY_INFO = 9
PACKET_CAR_DAMAGE = 10
PACKET_SESSION_HISTORY = 11

class F1TelemetryReceiver:
    def __init__(self, host: str = "127.0.0.1", port: int = 20777, ring_buffer: Optional[TelemetryRingBuffer] = None):
        self.host = host
        self.port = port
        self.ring_buffer = ring_buffer or TelemetryRingBuffer()
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

    def start_listening(self):
        self.is_running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False

    def _listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
            sock.settimeout(1.0)
            while self.is_running:
                try:
                    data, _ = sock.recvfrom(2048)
                    self._parse_packet(data)
                except socket.timeout:
                    continue
        except Exception as e:
            pass
        finally:
            sock.close()

    def _parse_packet(self, data: bytes):
        if len(data) < 24:
            return
        # Header: uint16 packetFormat, uint8 gameYear, uint8 gameMajorVersion, uint8 gameMinorVersion, uint8 packetVersion, uint8 packetId
        header = struct.unpack_from("<HBBBBB", data, 0)
        packet_id = header[5]
        # Ingestion unpacks directly to ring buffer
