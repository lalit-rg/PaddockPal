"""
Multi-Sim Telemetry Standardization Layer.
Defines the canonical NormalizedTelemetryFrame and abstract SimTelemetryAdapter.
Decouples the Racecraft & Inference Engines from game-specific packet structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List


class SimGameType(Enum):
    F1_23_24_25 = "f1_ea"
    IRACING = "iracing"
    ASSETTO_CORSA = "ac_acc"
    LE_MANS_ULTIMATE = "lmu_rf2"
    GENERIC = "generic_sim"


@dataclass
class NormalizedTelemetryFrame:
    """
    Unified canonical schema across all sim racing games.
    Any game adapter must map raw memory/UDP packets into this standard frame.
    """
    timestamp: float
    game: SimGameType
    track_name: str
    session_type: str            # "PRACTICE", "QUALIFYING", "RACE"
    current_lap: int
    total_laps: int
    position: int
    
    # Timing & Gaps
    last_lap_time_s: float
    best_lap_time_s: float
    gap_ahead_s: Optional[float]
    gap_behind_s: Optional[float]
    gap_to_leader_s: float
    ahead_driver: Optional[str] = None
    behind_driver: Optional[str] = None

    # Dynamics & Inputs (Vehicle Physics)
    speed_kph: float = 0.0
    rpm: int = 0
    gear: int = 0
    throttle_pct: float = 0.0    # 0.0 to 100.0
    brake_pct: float = 0.0       # 0.0 to 100.0
    steer_angle: float = 0.0
    drs_active: bool = False

    # Tyres & Thermal Dynamics
    tyre_compound: str = "UNKNOWN"
    tyre_age_laps: int = 0
    tyre_wear_pct: Dict[str, float] = field(default_factory=lambda: {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0})
    surface_temps_c: Dict[str, float] = field(default_factory=lambda: {"FL": 90.0, "FR": 90.0, "RL": 90.0, "RR": 90.0})
    carcass_temps_c: Dict[str, float] = field(default_factory=lambda: {"FL": 90.0, "FR": 90.0, "RL": 90.0, "RR": 90.0})
    brake_temps_c: Dict[str, float] = field(default_factory=lambda: {"FL": 300.0, "FR": 300.0, "RL": 300.0, "RR": 300.0})

    # Energy & Fuel
    fuel_remaining_kg: float = 0.0
    fuel_delta_laps: float = 0.0
    ers_battery_pct: float = 0.0

    # Environment & Race State
    track_temp_c: float = 30.0
    air_temp_c: float = 25.0
    rain_intensity_pct: float = 0.0
    track_wetness_pct: float = 0.0
    safety_car_status: str = "NONE"   # "NONE", "FULL_SC", "VSC"
    yellow_flag_sector: Optional[int] = None
    track_limits_warnings: int = 0
    illegal_pass_active: bool = False
    
    # Grid Vectors (For Traffic Rejoin Window calculations)
    grid_relative_gaps: List[Dict[str, Any]] = field(default_factory=list)


class SimTelemetryAdapter(ABC):
    """
    Abstract base class for all game-specific ingestion adapters.
    """
    @abstractmethod
    def start(self):
        """Initializes connection (UDP socket, Windows memory mapped file, or SDK pipe)."""
        pass

    @abstractmethod
    def stop(self):
        """Clean disconnect."""
        pass

    @abstractmethod
    def poll_latest_frame(self) -> Optional[NormalizedTelemetryFrame]:
        """Returns the latest normalized frame."""
        pass
