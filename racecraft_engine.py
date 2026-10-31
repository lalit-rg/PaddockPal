"""
F1 Strategy & Racecraft Dynamics Engine.
Models track-specific Safety Car probability, Pit Window traffic gaps, 
Track Condition Evolution, and Flag/Stewards regulations.
"""

from typing import Dict, Any, List, Optional

# Historical baseline Safety Car probabilities per circuit
CIRCUIT_SC_PROBABILITY = {
    "Monaco": 0.82,
    "Singapore": 0.89,
    "Baku": 0.76,
    "Jeddah": 0.72,
    "Melbourne": 0.65,
    "Montreal": 0.64,
    "Spa": 0.48,
    "Silverstone": 0.42,
    "Monza": 0.38,
    "Bahrain": 0.35,
    "Barcelona": 0.28,
    "Paul Ricard": 0.15,
    "DEFAULT": 0.40
}

# Standard pit lane time loss under Green vs Safety Car (seconds)
CIRCUIT_PIT_DELTAS = {
    "Monza": {"green": 24.0, "sc": 13.5},
    "Silverstone": {"green": 28.5, "sc": 16.0},
    "Bahrain": {"green": 23.5, "sc": 13.0},
    "Singapore": {"green": 29.0, "sc": 17.5},
    "DEFAULT": {"green": 24.0, "sc": 14.0}
}


class RacecraftStrategyEngine:
    """
    Advanced on-prem strategy calculation:
    1. Regulation/Flag Directives (Black & White Flag, Giving back position, Track limits)
    2. Traffic & Clean Air Rejoin Slot Evaluation
    3. Track Condition Evolution (Rain/Dry crossover, Rubbering)
    4. Undercut vs Overcut vs Safety Car Window Optimization
    """

    @classmethod
    def evaluate_stewards_and_flags(cls, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Highest Priority: Regulatory mandates, track limits, and flags.
        """
        flags = state.get("active_flags", {})
        track_limits_warnings = state.get("track_limits_warnings", 0)
        offtrack_pass = state.get("illegal_overtake_detected", False)

        # Illegal overtake (gained lasting advantage off-track)
        if offtrack_pass:
            return {
                "priority": "CRITICAL_STEWARD",
                "code": "GIVE_POSITION_BACK",
                "directive": "Give the position back immediately before Turn 4 to avoid a 5-second penalty.",
                "setting": "LIFT_AND_LET_PASS"
            }

        # Track Limits Strike 3 (Black and White Flag)
        if track_limits_warnings == 3:
            return {
                "priority": "HIGH_STEWARD",
                "code": "BLACK_AND_WHITE_FLAG",
                "directive": "Black and white flag for track limits. Next strike is a 5-second time penalty. Stay off the white lines.",
                "setting": "TIGHTEN_ENTRY_LINES"
            }

        # Yellow Flag / Debris
        if flags.get("yellow_flag_sector"):
            sector = flags.get("yellow_flag_sector")
            return {
                "priority": "HIGH_FLAG",
                "code": "YELLOW_FLAG",
                "directive": f"Yellow flag Sector {sector}. Debris reported, no overtaking, respect the delta.",
                "setting": "DELTA_POSITIVE"
            }

        return None

    @classmethod
    def analyze_traffic_rejoin_window(cls, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates grid gaps to find if pitting drops the driver into 'dirty air traffic'
        or a clean slot of free air.
        """
        track = state.get("track", "DEFAULT")
        pit_deltas = CIRCUIT_PIT_DELTAS.get(track, CIRCUIT_PIT_DELTAS["DEFAULT"])
        is_sc = state.get("safety_car_status") in ["FULL_SC", "VSC"]
        
        pit_loss = pit_deltas["sc"] if is_sc else pit_deltas["green"]
        grid_positions: List[Dict[str, Any]] = state.get("grid_relative_gaps", [])
        
        # Current driver position & timestamp
        current_gap_behind_leader = state.get("player", {}).get("gap_to_leader", 0.0)
        projected_rejoin_gap = current_gap_behind_leader + pit_loss

        # Find where driver lands relative to other cars
        slot_clean = True
        traffic_ahead_driver = None
        traffic_distance = 999.0

        for car in grid_positions:
            gap = car.get("gap_to_leader", 0.0)
            delta_to_rejoin = gap - projected_rejoin_gap
            
            # If a car is within 1.5 seconds ahead of projected rejoin slot, it's dirty air!
            if 0.0 < delta_to_rejoin < 2.0:
                slot_clean = False
                traffic_ahead_driver = car.get("driver")
                traffic_distance = delta_to_rejoin
                break

        return {
            "pit_time_loss": pit_loss,
            "projected_rejoin_gap_to_leader": projected_rejoin_gap,
            "is_clean_air_slot": slot_clean,
            "traffic_blocker": traffic_ahead_driver,
            "buffer_ahead_seconds": traffic_distance
        }

    @classmethod
    def evaluate_track_evolution(cls, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates track crossover (slick vs wet) and track grip evolution.
        """
        weather = state.get("weather", {})
        track_temp = weather.get("track_temp_c", 35)
        rain_pct = weather.get("rain_intensity_pct", 0)
        track_wetness_pct = weather.get("track_wetness_pct", 0)

        # Crossover windows:
        # Slick -> Intermediate crossover: ~20% wetness
        # Intermediate -> Full Wet crossover: ~65% wetness
        if track_wetness_pct > 65:
            recommendation = "FULL_WET"
            urgency = "HIGH"
        elif track_wetness_pct > 20:
            recommendation = "INTERMEDIATE"
            urgency = "HIGH"
        elif rain_pct > 30 and track_wetness_pct < 20:
            recommendation = "PREPARE_INTERS_RAIN_INCOMING"
            urgency = "MEDIUM"
        else:
            recommendation = "SLICK"
            urgency = "LOW"

        return {
            "track_temp_c": track_temp,
            "track_wetness_pct": track_wetness_pct,
            "rain_intensity_pct": rain_pct,
            "recommended_compound": recommendation,
            "urgency": urgency
        }

    @classmethod
    def compute_strategic_verdict(cls, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Master decision matrix combining:
        Steward rules + Traffic Rejoin slot + Weather + SC Probability
        """
        # 1. Regulation Checks
        steward_check = cls.evaluate_stewards_and_flags(state)
        if steward_check:
            return steward_check

        # 2. Weather Evolution Check
        weather_eval = cls.evaluate_track_evolution(state)
        current_compound = state.get("player", {}).get("tyre_compound", "DRY")
        if weather_eval["urgency"] == "HIGH" and weather_eval["recommended_compound"] not in current_compound:
            return {
                "priority": "CRITICAL_WEATHER",
                "code": "BOX_WEATHER_CROSSOVER",
                "directive": f"Box this lap for {weather_eval['recommended_compound']}. Crossover reached, rain intensity {weather_eval['rain_intensity_pct']}%.",
                "setting": f"PIT_FOR_{weather_eval['recommended_compound']}"
            }

        # 3. Traffic & Pit Slot Check
        traffic_info = cls.analyze_traffic_rejoin_window(state)
        track = state.get("track", "DEFAULT")
        sc_prob = CIRCUIT_SC_PROBABILITY.get(track, CIRCUIT_SC_PROBABILITY["DEFAULT"])
        player = state.get("player", {})
        tyre_wear = player.get("tyre_wear_avg_pct", 0)

        # Undercut opportunity: High wear, but pitting lands us into clean air
        if tyre_wear > 55 and traffic_info["is_clean_air_slot"]:
            return {
                "priority": "STRATEGIC_CALL",
                "code": "TRIGGER_UNDERCUT",
                "directive": f"Box this lap to undercut! Clean air slot identified with {traffic_info['pit_time_loss']}s delta.",
                "setting": "BOX_OPPOSITE_RIVAL"
            }

        # Traffic alert: Driver wants to pit, but will drop behind a slow car
        if tyre_wear > 55 and not traffic_info["is_clean_air_slot"]:
            return {
                "priority": "STRATEGIC_CALL",
                "code": "EXTEND_AVOID_TRAFFIC",
                "directive": f"Extend 2 laps! Pitting now rejoins directly behind {traffic_info['traffic_blocker']}. Clear air needed.",
                "setting": "STRETCH_STINT"
            }

        # Default pace hold
        return {
            "priority": "NOMINAL",
            "code": "HOLD_PACE",
            "directive": f"Pace is nominal. Track SC probability is {int(sc_prob * 100)}%. Target lap times achieved.",
            "setting": "CRUISE_STRATEGY"
        }
