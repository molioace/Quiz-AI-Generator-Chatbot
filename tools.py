from langchain_core.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


@tool("get_time", description="Get the current time and date for any city provided by the user.")
def get_time(city: str) -> str:
    """
    Get the current local time for a given city.

    Args:
        city: City name provided by the user, for example: Gaza, Cairo, London, New York.

    Returns:
        Current date and time in that city's timezone.
    """

    geolocator = Nominatim(user_agent="my_chatbot_time_tool")
    location = geolocator.geocode(city)

    if location is None:
        return f"Sorry, I could not find the city: {city}"

    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(
        lat=location.latitude,
        lng=location.longitude
    )

    if timezone_name is None:
        return f"Sorry, I could not detect the timezone for: {city}"

    local_time = datetime.now(ZoneInfo(timezone_name))

    return (
        f"The current time in {city} is "
        f"{local_time.strftime('%Y-%m-%d %H:%M:%S')} "
        f"({timezone_name})"
    )