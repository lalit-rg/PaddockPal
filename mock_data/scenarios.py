"""
Realistic telemetry scenarios simulating different in-race conditions for F1.
Each scenario represents a snapshot from the telemetry buffer + driver query.
"""

MOCK_SCENARIOS = {
    # Scenario 1: Hunting car ahead with fresher tyres
    "hunting_for_p2": {
        "title": "Scenario 1: Hunting P2 (Closing In)",
        "driver_query": "Can I push now? What's the gap ahead?",
        "telemetry_state": {
            "current_lap": 38,
            "total_laps": 57,
            "track": "Bahrain International Circuit",
            "position": 3,
            "car_ahead": {
                "driver": "VER",
                "gap_seconds": 0.85,
                "tyre_age_laps": 22,
                "tyre_compound": "HARD",
            },
            "car_behind": {
                "driver": "NOR",
                "gap_seconds": 4.20,
                "tyre_age_laps": 12,
                "tyre_compound": "MEDIUM",
            },
            "player": {
                "tyre_compound": "MEDIUM",
                "tyre_age_laps": 8,
                "tyre_wear_avg_pct": 21.4,
                "tyre_surface_temps": {
                    "FL": 102,
                    "FR": 103,
                    "RL": 104,
                    "RR": 105,
                },  # optimal
                "fuel_delta_laps": +0.8,  # +0.8 laps of excess fuel
                "ers_battery_pct": 74,
                "drs_available": True,
                "last_lap_time": "1:32.410",
                "fastest_lap_time": "1:32.100",
            },
        },
    },
    # Scenario 2: Tyres dying, under attack from behind
    "defending_worn_tyres": {
        "title": "Scenario 2: Defending P1 on dying Softs",
        "driver_query": "Tyres feel like ice, rear is sliding everywhere. Should we box?",
        "telemetry_state": {
            "current_lap": 24,
            "total_laps": 53,
            "track": "Monza",
            "position": 1,
            "car_ahead": None,
            "car_behind": {
                "driver": "HAM",
                "gap_seconds": 0.45,
                "tyre_age_laps": 6,
                "tyre_compound": "MEDIUM",
            },
            "player": {
                "tyre_compound": "SOFT",
                "tyre_age_laps": 19,
                "tyre_wear_avg_pct": 68.2,  # severely worn
                "tyre_surface_temps": {
                    "FL": 112,
                    "FR": 111,
                    "RL": 124,
                    "RR": 126,
                },  # overheating rears
                "fuel_delta_laps": -0.2,
                "ers_battery_pct": 32,
                "drs_available": False,
                "pit_window_open": True,
                "pit_loss_seconds": 23.5,
                "rejoin_position_estimate": 4,
            },
        },
    },
    # Scenario 3: Strategy / Safety Car Opportunity
    "safety_car_dilemma": {
        "title": "Scenario 3: Safety Car Deployed - Box or Stay Out?",
        "driver_query": "Safety Car! Do we box? What's Plan B?",
        "telemetry_state": {
            "current_lap": 42,
            "total_laps": 70,
            "track": "Hungaroring",
            "position": 2,
            "safety_car_status": "FULL_SC",
            "car_ahead": {"driver": "LEC", "gap_seconds": 1.2, "status": "STAYED_OUT"},
            "car_behind": {"driver": "RUS", "gap_seconds": 5.8, "status": "PITTING"},
            "player": {
                "distance_to_pit_entry_m": 250,  # Pit entry right ahead!
                "tyre_compound": "HARD",
                "tyre_age_laps": 28,
                "tyre_wear_avg_pct": 52.0,
                "fresh_tyres_available": ["SOFT_SET_2", "MEDIUM_SET_1"],
                "pit_delta_under_sc_seconds": 12.0,  # Normal 22s -> 12s under SC
                "rejoin_position_if_box": 3,
            },
        },
    },
    # Scenario 4: Fast System Check (Tier 1 vs Tier 2 test)
    "system_check_status": {
        "title": "Scenario 4: Simple System Check (Telemetry Slot-filling)",
        "driver_query": "Radio check and status update.",
        "telemetry_state": {
            "current_lap": 15,
            "total_laps": 58,
            "track": "Silverstone",
            "position": 4,
            "car_ahead": {"driver": "PIA", "gap_seconds": 1.9},
            "car_behind": {"driver": "SAI", "gap_seconds": 2.3},
            "player": {
                "tyre_compound": "MEDIUM",
                "tyre_age_laps": 15,
                "tyre_wear_avg_pct": 34.0,
                "tyre_surface_temps": {"FL": 100, "FR": 104, "RL": 102, "RR": 103},
                "fuel_delta_laps": +0.4,
                "ers_battery_pct": 61,
                "damage": {"front_wing_left": 0, "front_wing_right": 0, "floor": 0},
            },
        },
    },
}
