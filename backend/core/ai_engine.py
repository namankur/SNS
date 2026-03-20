import os
from datetime import datetime, timezone, timedelta
import anthropic
from database import get_db

IST = timezone(timedelta(hours=5, minutes=30))

anthropic_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=anthropic_key) if anthropic_key else None

def get_score_label(score: float) -> str:
    if score <= 0.3:
        return "completely normal"
    elif score <= 0.6:
        return "slightly quieter than usual"
    else:
        return "unusually quiet — worth checking"

def get_expected_activity_label(hour: int, baseline: dict = None) -> str:
    # Basic heuristic without full baseline logic yet
    if 22 <= hour or hour <= 6:
        return "typically asleep"
    elif 13 <= hour <= 16:
        return "usually resting"
    elif 7 <= hour <= 9:
        return "walk time"
    else:
        return "should be active"

def generate_today_summary(signals: list) -> str:
    """
    Summarizes today's signals in plain English based on the rules.
    """
    if not signals:
        return "Aaj ka koi naya data record nahi hua hai."
    
    # Simple aggregation of unique movements or significant events today
    movements = list(set([s.get('movement_type', 'STILL') for s in signals[:5]]))
    avg_battery = sum([s.get('battery_level', 0) for s in signals]) / len(signals) if signals else 0
    
    summary = f"Phone abhi {movements[0].lower()} mode mein hai. "
    if len(movements) > 1:
        summary += f"Din mein {', '.join(movements[1:]).lower()} activity dekhi gayi. "
    
    summary += f"Battery average {int(avg_battery)}% rahi hai."
    return summary

def generate_response(
    user_id: str, 
    dear_one_nickname: str, 
    language: str,
    signals: list,
    routine_profile: dict,
    deviation_score: float,
    current_datetime: str
) -> str:
    """
    Core function that turns signal data into a warm human message using Claude.
    """
    if not client:
        ai_offline = True
    else:
        ai_offline = False

    score_label = get_score_label(deviation_score)
    expected_activity_label = get_expected_activity_label(datetime.now(IST).hour)
    today_summary = generate_today_summary(signals)
    
    # Extract latest signal context (mocked default mapping for MVP)
    latest_signal = signals[0] if signals else {}
    last_active_mins = latest_signal.get('screen_active_last_mins', 'unknown')
    movement = latest_signal.get('movement_type', 'STILL')
    battery = latest_signal.get('battery_level', 'unknown')
    charging_status = "Charging" if latest_signal.get('is_charging') else "Not Charging"
    network_raw = latest_signal.get('network_type', 'unknown')
    is_wifi = latest_signal.get('is_wifi', False)
    network = f"Wi-Fi ({network_raw})" if is_wifi else network_raw
    dnd_status = "ON (Do Not Disturb)" if latest_signal.get('dnd_active') else "OFF (Ringer On)"
    last_interaction = latest_signal.get('last_interaction_time', 'N/A')
    synced_at = latest_signal.get('synced_at', 'unknown')
    ringer_mode = latest_signal.get('ringer_mode', 'NORMAL')
    ringer_vol = latest_signal.get('ringer_volume', 50)
    headphones = "Plugged in / Bluetooth" if latest_signal.get('is_headphone_plugged') else "Disconnected"
    
    # New privacy-safe signals
    light = latest_signal.get('ambient_light', 'NORMAL')
    orientation = latest_signal.get('phone_orientation', 'FLAT')
    proximity = latest_signal.get('proximity', 'FAR')
    
    # Check if this is a missed call fallback situation
    missed_call_time = None
    if signals and signals[0].get('movement_type') == 'CHECKED_IN_MISSED_CALL':
        missed_call_time = signals[0].get('timestamp', str(datetime.now(IST)))
        last_active_mins = 'N/A'
        battery = 'N/A'
        charging_status = 'unknown'
        network = 'offline'
        dnd_status = 'unknown' # dnd_status for missed call scenario
        last_interaction = 'N/A'
        synced_at = 'N/A'
        ringer_mode = 'unknown'
        ringer_vol = 'unknown'
        headphones = 'unknown'
        last_app = 'unknown'
    
    # Routine profile fallback
    wake_time = routine_profile.get('wake_time_avg', '6:00 AM') if routine_profile else '6:00 AM'
    nap_start = routine_profile.get('nap_window_start', '1:00 PM') if routine_profile else '1:00 PM'
    nap_end = routine_profile.get('nap_window_end', '2:30 PM') if routine_profile else '2:30 PM'
    sleep_time = routine_profile.get('sleep_time_avg', '10:00 PM') if routine_profile else '10:00 PM'
    walk_days = ", ".join(routine_profile.get('walk_days', ['MON','WED','FRI'])) if routine_profile else 'MON, WED, FRI'
    
    if ai_offline:
        return (
            f"Device Status: {dear_one_nickname}\n\n"
            f"• Last Active: {last_active_mins}m ago\n"
            f"• Battery: {battery}% ({charging_status})\n"
            f"• Network: {network}\n"
            f"• Audio: {ringer_mode} (Vol: {ringer_vol}%)\n"
            f"• DND Status: {dnd_status}\n"
            f"• Environment: {light} | {orientation} | {proximity}\n"
            f"• Headphones: {headphones}\n"
            f"• Movement: {movement}\n\n"
            f"Last Synced: {synced_at}"
        )
    
    system_prompt = '''You are a clean, minimalist Apple-style system assistant generating a device status report.
You have access to device telemetry signals. 

Rules:
1. Output in English ONLY. Never use Hindi, never use terms like 'Ji', 'Namaste', or cultural honorifics.
2. Format as a clean, highly readable bulleted list (using •) exactly like an iOS system alert.
3. You MUST include ALL available signal parameters from the prompt in the list.
4. No emotional reassurance, no conversational filler, no emojis. Keep it sterile, professional, and data-driven.
5. Provide a one sentence "Trend" at the bottom based on the deviation score and routine.
6. If data is old (>3 hours), append a "Warning: Stale data" line.'''
    
    missed_call_clause = ""
    if missed_call_time:
        missed_call_clause = f'''
Note: This dear one uses missed call check-in (no app installed). 
Last missed call received: {missed_call_time}
No other signal data available.
Generate response acknowledging this limitation but still being reassuring about the check-in.
'''

    user_prompt = f'''Current time: {current_datetime}
Day: {datetime.now(IST).strftime('%A')}
Dear one's name: {dear_one_nickname}
Deviation from normal: {score_label} ({deviation_score})

Latest signals:
- Phone last active: {last_active_mins} minutes ago
- Room brightness: {light}
- Phone orientation: {orientation}
- Proximity: {proximity}
- Current movement: {movement}
- Battery: {battery}% {charging_status}
- Internet: {network}
- Phone silenced: {dnd_status}

Their normal routine:
- Usually wakes: {wake_time}
- Nap window: {nap_start} to {nap_end}  
- Sleep time: {sleep_time}
- Walk days: {walk_days}
- Activity level right now should be: {expected_activity_label}

Today's pattern so far: {today_summary}
{missed_call_clause}
Generate a warm reassuring response for the caller 
in {language}.'''

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error contacting AI service: {str(e)}"
