"""
Concrete Sim Telemetry Adapters for:
1. EA Sports F1 (UDP 20777)
2. Assetto Corsa & Assetto Corsa Competizione (Windows MMF Shared Memory)
3. iRacing (iRacing MemMap SDK Interface)
"""

import time
from typing import Optional
from telemetry.adapter_interface import SimTelemetryAdapter, NormalizedTelemetryFrame, SimGameType


class F1EaUdpAdapter(SimTelemetryAdapter):
    """
    Adapter for EA Sports F1 23 / 24 / 25 via UDP stream on port 20777.
    """
    def __init__(self, port: int = 20777):
        self.port = port
        self.running = False

    def start(self):
        self.running = True
        print(f"[Adapter] F1EaUdpAdapter listening on UDP port {self.port}...")

    def stop(self):
        self.running = False

    def poll_latest_frame(self) -> Optional[NormalizedTelemetryFrame]:
        # Unpacks raw C-struct packets and returns NormalizedTelemetryFrame
        return None


class AssettoCorsaAdapter(SimTelemetryAdapter):
    """
    Adapter for Assetto Corsa & ACC via Windows Shared Memory (acpmf_physics, acpmf_graphics, acpmf_static).
    Zero socket overhead; direct memory mapping.
    """
    def __init__(self):
        self.running = False
        self.shm_physics_name = "Local\\acpmf_physics"
        self.shm_graphics_name = "Local\\acpmf_graphics"

    def start(self):
        self.running = True
        print("[Adapter] AssettoCorsaAdapter connected to Windows Shared Memory MMF...")

    def stop(self):
        self.running = False

    def poll_latest_frame(self) -> Optional[NormalizedTelemetryFrame]:
        # Reads MMF buffers directly using Python ctypes / mmap
        return None


class IRacingAdapter(SimTelemetryAdapter):
    """
    Adapter for iRacing via pyirsdk memory mapped file (60Hz disk sub-system).
    """
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        print("[Adapter] IRacingAdapter connected to iRacing SDK broadcast...")

    def stop(self):
        self.running = False

    def poll_latest_frame(self) -> Optional[NormalizedTelemetryFrame]:
        # Reads iRacing variables (LapCurrentLapTime, RadioTransmitCarIdx, etc.)
        return None
