import datetime
from datetime import datetime, time

def is_nyse_open() -> bool:
    """
    Check if the NYSE is currently open based on the date, time, and holidays.
    """
    now = datetime.now()
    current_time = now.time()
    current_date = now.date()

    market_open = time(9, 30)
    market_close = time(16, 0)

    holidays = [
        "2024-01-01",  # New Year's Day
        "2024-01-15",  # Martin Luther King Jr. Day
        "2024-02-19",  # Presidents' Day
        "2024-03-29",  # Good Friday
        "2024-05-27",  # Memorial Day
        "2024-07-04",  # Independence Day
        "2024-09-02",  # Labor Day
        "2024-11-28",  # Thanksgiving Day
        "2024-12-25",  # Christmas Day
    ]
    holidays = [datetime.strptime(date, "%Y-%m-%d").date() for date in holidays]

    early_closing_days = [
        "2024-07-03",
        "2024-11-29",
        "2024-12-24",
    ]
    early_closing_days = [datetime.strptime(date, "%Y-%m-%d").date() for date in early_closing_days]
    early_closing_time = time(13, 0)

    if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False

    if current_date in holidays:
        return False

    if current_date in early_closing_days:
        return market_open <= current_time <= early_closing_time

    return market_open <= current_time <= market_close

if __name__ == "__main__":
    print("NYSE is currently open.") if is_nyse_open() else print("NYSE is currently closed.")