"""
Analytics Engine: Categorizes Race Insights into:
1. DESCRIPTIVE ANALYTICS ("What is happening right now?") -> Tier 1 (<5ms instant read)
2. PRESCRIPTIVE ANALYTICS ("What ACTION should the driver take?") -> Multi-factor composite score calculation
"""

from typing import Dict, Any, Tuple

class TelemetryAnalyticsEngine:
    """
    Computes instant Descriptive facts and multi-factor Prescriptive directives.
    Zero external dependencies, pure standard library math for sub-millisecond execution.
    """

    @staticmethod
    def get_descriptive_metrics(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        DESCRIPTIVE ANALYSIS:
        Objective facts extracted instantly from the telemetry stream.
        Answers: 'What is my position, tyre wear, temperatures, and gaps?'
        """
        player = state.get("player", {})
        car_ahead = state.get("car_ahead") or {}
        car_behind = state.get("car_behind") or {}
        
        return {
            "pos": state.get("position"),
            "lap": f"{state.get('current_lap')}/{state.get('total_laps')}",
            "gap_ahead": car_ahead.get("gap_seconds"),
            "gap_behind": car_behind.get("gap_seconds"),
            "tyre_compound": player.get("tyre_compound"),
            "tyre_age": player.get("tyre_age_laps"),
            "tyre_wear_avg": player.get("tyre_wear_avg_pct"),
            "temps": player.get("tyre_surface_temps", {}),
            "fuel_delta": player.get("fuel_delta_laps", 0.0),
            "battery_pct": player.get("ers_battery_pct", 0)
        }

    @classmethod
    def evaluate_prescriptive_formula(cls, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRESCRIPTIVE ANALYSIS:
        Calculates a multi-factor decision matrix (Weather, Thermal load, Delta, Opponent Wear).
        Answers: 'WHAT SHOULD I DO RIGHT NOW?' (Lift & Coast, Box, Attack, Defend, Save battery).
        """
        player = state.get("player", {})
        temps = player.get("tyre_surface_temps", {"FL": 100, "FR": 100, "RL": 100, "RR": 100})
        wear = player.get("tyre_wear_avg_pct", 0)
        fuel = player.get("fuel_delta_laps", 0.0)
        battery = player.get("ers_battery_pct", 50)
        
        car_ahead = state.get("car_ahead") or {}
        gap_ahead = car_ahead.get("gap_seconds", 999.0)
        ahead_tyre_age = car_ahead.get("tyre_age_laps", 0)
        
        car_behind = state.get("car_behind") or {}
        gap_behind = car_behind.get("gap_seconds", 999.0)
        
        rear_temp_max = max(temps.get("RL", 100), temps.get("RR", 100))
        sc_status = state.get("safety_car_status")

        # --- MULTI-FACTOR WEIGHTED RISK & OPPORTUNITY FORMULA ---
        # 1. Thermal Degradation Risk Score (0 - 100)
        thermal_risk = 0
        if rear_temp_max > 115:
            thermal_risk = min(100, (rear_temp_max - 110) * 6.5)
            
        # 2. Attack Opportunity Score (0 - 100)
        # Factors: Gap < 1.2s, Opponent tyre age advantage, Battery availability, Excess fuel
        attack_score = 0
        if gap_ahead < 1.5:
            tyre_advantage_factor = max(0, ahead_tyre_age - player.get("tyre_age_laps", 0)) * 4.0
            battery_factor = (battery / 100.0) * 30.0
            fuel_factor = 20.0 if fuel > 0 else 0.0
            proximity_factor = max(0, (1.5 - gap_ahead) / 1.5) * 50.0
            attack_score = min(100, proximity_factor + battery_factor + tyre_advantage_factor + fuel_factor)

        # 3. Defensive Threat Score (0 - 100)
        defense_threat = 0
        if gap_behind < 1.0:
            defense_threat = min(100, (1.0 - gap_behind) * 80.0 + (wear * 0.4))

        # --- PRESCRIPTIVE DIRECTIVES (PRIORITIZED) ---
        # Priority 1: Safety Car Pit Window
        if sc_status in ["FULL_SC", "VSC"] and wear > 40:
            return {
                "priority": "CRITICAL",
                "action": "BOX_NOW",
                "directive": "Box box under Safety Car. High wear + 12s cheap delta.",
                "actionable_setting": "PIT_LIMITER_ON / PIT_ENTRY"
            }

        # Priority 2: Critical Thermal / Tyre Failure
        if thermal_risk > 75 and defense_threat < 60:
            return {
                "priority": "HIGH",
                "action": "MANAGE_TRACTION_LIFT_COAST",
                "directive": f"Rears critical at {rear_temp_max}C. Lift and coast 50m before braking.",
                "actionable_setting": "BRAKE_BIAS +2% FORWARD"
            }

        # Priority 3: Attack / Overtake Execution
        if attack_score > 65:
            return {
                "priority": "HIGH",
                "action": "EXECUTE_OVERTAKE",
                "directive": f"Opponent tyres dying ({ahead_tyre_age} laps old). Dump ERS into main straight.",
                "actionable_setting": "ERS_MODE_OVERTAKE"
            }

        # Priority 4: Defensive Stand
        if defense_threat > 70:
            return {
                "priority": "HIGH",
                "action": "DEFEND_LINE",
                "directive": f"Car behind {gap_behind:.1f}s. Protect the inside apex, deploy battery on exit.",
                "actionable_setting": "ERS_MODE_DEFEND"
            }

        # Priority 5: Optimal Fuel / Cruise Management
        if fuel < -0.3:
            return {
                "priority": "MEDIUM",
                "action": "SAVE_FUEL",
                "directive": f"Fuel deficit {fuel:.1f} laps. Short shift in gears 3 and 4.",
                "actionable_setting": "STRAT_MODE_CONSERVE"
            }

        # Default: Hit Target Delta (Prost style)
        return {
            "priority": "LOW",
            "action": "MAINTAIN_PACE",
            "directive": "Pace is optimal. Hit the apex target delta cleanly.",
            "actionable_setting": "CRUISE_NOMINAL"
        }
