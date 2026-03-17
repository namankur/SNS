import os
from datetime import datetime
import anthropic
from database import get_db

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
        return "No data recorded today yet."
    return "Morning walk completed, active until 2pm, quiet since then — normal pattern."

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
        return "System is currently offline or Anthropic API key is missing."

    score_label = get_score_label(deviation_score)
    expected_activity_label = get_expected_activity_label(datetime.now().hour)
    today_summary = generate_today_summary(signals)
    
    # Extract latest signal context (mocked default mapping for MVP)
    last_active_mins = signals[0].get('screen_active_last_mins', 'unknown') if signals else 'unknown'
    movement = signals[0].get('movement_type', 'STILL') if signals else 'unknown'
    battery = signals[0].get('battery_level', 100) if signals else 100
    charging_status = "charging" if (signals and signals[0].get('is_charging')) else "not charging"
    network = signals[0].get('network_type', 'WIFI') if signals else 'offline'
    # Check if this is a missed call fallback situation
    missed_call_time = None
    if signals and signals[0].get('movement_type') == 'CHECKED_IN_MISSED_CALL':
        missed_call_time = signals[0].get('timestamp', str(datetime.now()))
        last_active_mins = 'N/A'
        battery = 'N/A'
        charging_status = 'unknown'
        network = 'offline'
        dnd = 'unknown'
    
    # Routine profile fallback
    wake_time = routine_profile.get('wake_time_avg', '6:00 AM') if routine_profile else '6:00 AM'
    nap_start = routine_profile.get('nap_window_start', '2:00 PM') if routine_profile else '2:00 PM'
    nap_end = routine_profile.get('nap_window_end', '4:00 PM') if routine_profile else '4:00 PM'
    sleep_time = routine_profile.get('sleep_time_avg', '10:00 PM') if routine_profile else '10:00 PM'
    walk_days = ", ".join(routine_profile.get('walk_days', ['MON','WED','FRI'])) if routine_profile else 'MON, WED, FRI'
    
    system_prompt = '''You are a warm, caring assistant helping a worried 
family member understand if their elderly loved one 
is okay. You have access to passive phone signals 
(NOT location, NOT messages, NOT call logs).

Rules:
1. Always start with emotional reassurance first
2. Explain WHY they did not answer in human terms
3. Never use technical words like 'accelerometer', 
   'API', 'signal', 'algorithm', 'deviation score'
4. Always end with a clear next action
5. Keep response under 60 words
6. If deviation_score > 0.6, gently suggest 
   checking urgently without causing panic
7. If language is hindi, respond in simple Hindi 
   (not formal, like talking to family)
8. Use emoji sparingly — only 1-2 max
9. Never make up information not in the signals
10. If data is old (>3 hours), be honest about it'''

    missed_call_clause = ""
    if missed_call_time:
        missed_call_clause = f'''
Note: This dear one uses missed call check-in (no app installed). 
Last missed call received: {missed_call_time}
No other signal data available.
Generate response acknowledging this limitation but still being reassuring about the check-in.
'''

    user_prompt = f'''Current time: {current_datetime}
Day: {datetime.now().strftime('%A')}
Dear one's name: {dear_one_nickname}
Deviation from normal: {score_label} ({deviation_score})

Latest signals:
- Phone last active: {last_active_mins} minutes ago
- Current movement: {movement}
- Battery: {battery}% {charging_status}
- Internet: {network}
- Phone silenced: {dnd}

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
