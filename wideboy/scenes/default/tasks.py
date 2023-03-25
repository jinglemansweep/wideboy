import aiohttp
import asyncio
import json
import logging
from datetime import datetime
from wideboy.state import STATE
from wideboy.utils.helpers import async_fetch
from wideboy.config import get_config_env_var

SCENE_BACKGROUND_CHANGE_INTERVAL_MINS = int(
    get_config_env_var("SCENE_BACKGROUND_CHANGE_INTERVAL_MINS", 5)
)
SCENE_WEATHER_FETCH_INTERVAL = int(
    get_config_env_var("SCENE_WEATHER_FETCH_INTERVAL", 600)
)
SCENE_WEATHER_LATITUDE = float(get_config_env_var("SCENE_WEATHER_LATITUDE", 52.0557))
SCENE_WEATHER_LONGITUDE = float(get_config_env_var("SCENE_WEATHER_LONGITUDE", 1.1153))


logger = logging.getLogger(__name__)

OPENMETEO_API_URL = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,precipitation_probability"


async def fetch_weather():
    loop = asyncio.get_event_loop()
    url = OPENMETEO_API_URL.format(
        latitude=SCENE_WEATHER_LATITUDE, longitude=SCENE_WEATHER_LONGITUDE
    )
    logger.info(f"task:fetch:weather url={url}")
    try:
        async with aiohttp.ClientSession(loop=loop) as session:
            json_resp = await async_fetch(session, url)
        data = json.loads(json_resp)
        # logger.debug(data)
        now = datetime.now()
        next_hour_str = now.strftime("%Y-%m-%dT%H:00")
        idx = data["hourly"]["time"].index(next_hour_str)
        STATE.weather_summary = weather_code_to_icon(
            data["current_weather"]["weathercode"]
        )
        STATE.temperature = data["hourly"]["temperature_2m"][idx]
        STATE.rain_probability = data["hourly"]["precipitation_probability"][idx]
        logger.info(
            f"weather:summary summary={STATE.weather_summary} temperature={STATE.temperature} rain_probability={STATE.rain_probability}"
        )
    except Exception as e:
        logger.error("task:fetch:weather:error", exc_info=e)
    await asyncio.sleep(SCENE_WEATHER_FETCH_INTERVAL)
    asyncio.create_task(fetch_weather())


def weather_code_to_icon(code: int) -> str:
    icon: str = None
    if code == 0:
        icon = "sunny"
    elif code == 1:
        icon = "clear-cloudy"
    elif code == 2:
        icon = "cloudy"
    elif code == 3:
        icon = "mostly-cloudy"
    elif code == 45 or code == 48:
        icon = "fog"
    elif code in ([51, 53, 55, 61, 63, 65, 80, 81, 82]):
        icon = "drizzle"
    elif code in ([56, 57, 66, 67, 77]):
        icon = "sleet"
    elif code == 71:
        icon = "snow-flurries"
    elif code in ([73, 75, 85, 86]):
        icon = "snow"
    elif code in ([95, 96]):
        icon = "thunderstorms"
    return icon


"""
0	Clear sky
1, 2, 3	Mainly clear, partly cloudy, and overcast
45, 48	Fog and depositing rime fog
51, 53, 55	Drizzle: Light, moderate, and dense intensity
56, 57	Freezing Drizzle: Light and dense intensity
61, 63, 65	Rain: Slight, moderate and heavy intensity
66, 67	Freezing Rain: Light and heavy intensity
71, 73, 75	Snow fall: Slight, moderate, and heavy intensity
77	Snow grains
80, 81, 82	Rain showers: Slight, moderate, and violent
85, 86	Snow showers slight and heavy
95 *	Thunderstorm: Slight or moderate
96, 99 *	Thunderstorm with slight and heavy hail
"""
