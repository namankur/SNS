import os
import sys
from datetime import datetime

# Add simple path hacking for relative imports if run as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import generate_response

def run_tests():
    print("Testing 5 Scenarios with Claude AI (Dry run unless ANTHROPIC_API_KEY is set)\n")
    
    # Base routine profile matching the prompt's examples
    routine = {
        'wake_time_avg': '6:30 AM',
        'nap_window_start': '2:00 PM',
        'nap_window_end': '4:00 PM',
        'sleep_time_avg': '10:30 PM',
        'walk_days': ['MON', 'WED', 'FRI']
    }
    
    # Scenario 1: Napping (score 0.1)
    print("--- SCENARIO 1: Napping (Score 0.1) ---")
    signals_napping = [{
        'screen_active_last_mins': 0,
        'movement_type': 'STILL',
        'battery_level': 85,
        'is_charging': False,
        'network_type': 'WIFI',
        'dnd_active': True
    }]
    print(generate_response(
        "u1", "Maa", "hindi", signals_napping, routine, 0.1, 
        current_datetime="2024-05-15 15:00:00" # 3:00 PM (Nap Window)
    ))
    print("\n")
    
    # Scenario 2: On walk (score 0.05)
    print("--- SCENARIO 2: On walk (Score 0.05) ---")
    signals_walk = [{
        'screen_active_last_mins': 15,
        'movement_type': 'WALKING',
        'battery_level': 70,
        'is_charging': False,
        'network_type': 'MOBILE',
        'dnd_active': False
    }]
    print(generate_response(
        "u1", "Papa", "english", signals_walk, routine, 0.05, 
        current_datetime="2024-05-15 08:30:00" # Wed Walk Time
    ))
    print("\n")
    
    # Scenario 3: Unusually quiet (score 0.45)
    print("--- SCENARIO 3: Unusually quiet (Score 0.45) ---")
    signals_quiet = [{
        'screen_active_last_mins': 0,
        'movement_type': 'STILL',
        'battery_level': 45,
        'is_charging': False,
        'network_type': 'WIFI',
        'dnd_active': False
    }]
    print(generate_response(
        "u1", "Dadi", "hindi", signals_quiet, routine, 0.45, 
        current_datetime="2024-05-15 18:00:00" # 6 PM (Usually active)
    ))
    print("\n")

    # Scenario 4: Very concerning (score 0.75)
    print("--- SCENARIO 4: Very concerning (Score 0.75) ---")
    signals_concerning = [{
        'screen_active_last_mins': 0,
        'movement_type': 'STILL',
        'battery_level': 20,
        'is_charging': False,
        'network_type': 'WIFI',
        'dnd_active': False
    }]
    print(generate_response(
        "u1", "Maa", "english", signals_concerning, routine, 0.75, 
        current_datetime="2024-05-15 11:00:00" # 11 AM (Usually highly active)
    ))
    print("\n")

    # Scenario 5: Phone offline (score 0.8)
    print("--- SCENARIO 5: Offline (Score 0.8) ---")
    # Empty signals array to simulate offline for >8 hours
    print(generate_response(
        "u1", "Papa", "hindi", [], routine, 0.8, 
        current_datetime="2024-05-15 20:00:00" 
    ))
    print("\n")

if __name__ == "__main__":
    run_tests()
