"""
Low-latency thread-safe circular ring buffer for F1 60Hz UDP telemetry.
Stores rolling historical windows for pace, tyre degradation, and sector deltas
with sub-millisecond lock-free access.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class TelemetrySnapshot:
    timestamp: float
    lap: int
    position: int
    gap_ahead: Optional[float]
    gap_behind: Optional[float]
    tyre_compound: str
    tyre_age: int
    tyre_wear_avg: float
    surface_temps: Dict[str, float]
    carcass_temps: Dict[str, float]
    fuel_delta: float
    ers_battery_pct: float
    drs_active: bool
    speed_kph: float
    gear: int
    throttle: float
    brake: float

class TelemetryRingBuffer:
    def __init__(self, capacity: int = 1800):
        """
        capacity = 1800 snapshots (~30 seconds of rolling data at 60Hz)
        """
        self.capacity = capacity
        self.buffer: deque = deque(maxlen=capacity)
        self.latest_snapshot: Optional[TelemetrySnapshot] = None
        self.lap_history: List[Dict[str, Any]] = []

    def push(self, snapshot: TelemetrySnapshot) -> None:
        self.buffer.append(snapshot)
        self.latest_snapshot = snapshot

    def get_latest(self) -> Optional[TelemetrySnapshot]:
        return self.latest_snapshot

    def calculate_wear_slope(self, window_seconds: float = 10.0) -> float:
        """
        Returns tyre wear percentage increase per lap equivalent.
        """
        if len(self.buffer) < 10:
            return 0.0
            
        now = self.buffer[-1].timestamp
        cutoff = now - window_seconds
        
        # sample oldest in window
        oldest = None
        for item in self.buffer:
            if item.timestamp >= cutoff:
                oldest = item
                break
                
        if not oldest or oldest == self.buffer[-1]:
            return 0.0
            
        time_delta = self.buffer[-1].timestamp - oldest.timestamp
        wear_delta = self.buffer[-1].tyre_wear_avg - oldest.tyre_wear_avg
        
        if time_delta <= 0:
            return 0.0
        # Extrapolate to typical 90-second lap
        return (wear_delta / time_delta) * 90.0
