from datetime import datetime


def is_valid_date(deadline_date, deadline_time):
    
    if deadline_date and deadline_time:
        # Convert deadline_date string to datetime object
        deadline_datetime = datetime.strptime(f"{deadline_date} {deadline_time}", "%Y-%m-%d %H:%M")
        # Compare datetimes
        if deadline_datetime < datetime.now():
            return False
    return True