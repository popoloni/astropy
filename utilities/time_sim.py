from datetime import datetime, timedelta
import pytz

# Store the simulated time if set
SIMULATED_DATETIME = None

def get_simulated_datetime(simulation_time_str, timezone=None):
    """Convert a time string to a simulated datetime object with the current date."""
    if not simulation_time_str:
        return None
    
    try:
        # Parse the simulation time (format: HH:MM or HH:MM:SS)
        time_parts = [int(part) for part in simulation_time_str.split(':')]
        hour = time_parts[0]
        minute = time_parts[1] if len(time_parts) > 1 else 0
        second = time_parts[2] if len(time_parts) > 2 else 0
        
        # Get current date but with the simulated time
        current = datetime.now()
        simulated_datetime = current.replace(hour=hour, minute=minute, second=second)
        
        # If the simulated time is in the future, move it to the previous day
        if simulated_datetime > current:
            simulated_datetime = simulated_datetime - timedelta(days=1)
        
        # Apply timezone if provided
        if timezone is not None:
            if simulated_datetime.tzinfo is None:
                simulated_datetime = timezone.localize(simulated_datetime)
            else:
                simulated_datetime = simulated_datetime.astimezone(timezone)
            
        return simulated_datetime
    except Exception as e:
        print(f"Error parsing simulation time: {e}")
        return None

def get_current_datetime(timezone=None):
    """Get current datetime, using simulated time if set, otherwise actual time."""
    global SIMULATED_DATETIME
    if SIMULATED_DATETIME is not None:
        if timezone is None:
            return SIMULATED_DATETIME
        return SIMULATED_DATETIME.astimezone(timezone)
    
    if timezone is None:
        return datetime.now()
    return datetime.now(timezone) 