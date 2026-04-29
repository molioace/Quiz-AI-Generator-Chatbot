from langchain_core.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo



@tool("get_time", description="Get the current time and date for a city provided by the user.")
def get_time(city: str) -> str:
    """
    Get the current local time for a supported city.

    Args:
        city: City name provided by the user, for example:
              Gaza, Cairo, London, New York.

    Returns:
        Current date and time in that city's timezone.
    """

    CITY_TIMEZONES = {
        "gaza": "Asia/Gaza",
        "rafah": "Asia/Gaza",
        "khan yunis": "Asia/Gaza",
        "jerusalem": "Asia/Jerusalem",
        "cairo": "Africa/Cairo",
        "amman": "Asia/Amman",
        "riyadh": "Asia/Riyadh",
        "dubai": "Asia/Dubai",
        "doha": "Asia/Qatar",
        "istanbul": "Europe/Istanbul",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "berlin": "Europe/Berlin",
        "new york": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "tokyo": "Asia/Tokyo",
    }

    city_key = city.strip().lower()

    timezone_name = CITY_TIMEZONES.get(city_key)

    if timezone_name is None:
        supported_cities = ", ".join(CITY_TIMEZONES.keys())
        return (
            f"Sorry, I do not currently support '{city}'. "
            f"Supported cities are: {supported_cities}."
        )

    local_time = datetime.now(ZoneInfo(timezone_name))

    return (
        f"The current time in {city.title()} is "
        f"{local_time.strftime('%Y-%m-%d %H:%M:%S')} "
        f"({timezone_name})"
    )