import aiohttp
import asyncio
import json
import logging
from datetime import datetime
from pprint import pprint
from wideboy.utils.state import StateStore
from wideboy.utils.helpers import async_fetch
from wideboy.config import (
    WEATHER_FETCH_INTERVAL,
    WEATHER_LATITUDE,
    WEATHER_LONGITUDE,
)

logger = logging.getLogger(__name__)

OPENMETEO_API_URL = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,precipitation_probability"


async def fetch_weather(loop: asyncio.AbstractEventLoop, state: StateStore):
    url = OPENMETEO_API_URL.format(
        latitude=WEATHER_LATITUDE, longitude=WEATHER_LONGITUDE
    )
    logger.info(f"task:fetch:weather url={url}")
    try:
        async with aiohttp.ClientSession(loop=loop) as session:
            json_resp = await async_fetch(session, url)
        data = json.loads(json_resp)
        now = datetime.now()
        next_hour_str = now.strftime("%Y-%m-%dT%H:00")
        idx = data["hourly"]["time"].index(next_hour_str)
        state.temperature = data["hourly"]["temperature_2m"][idx]
        state.rain_probability = data["hourly"]["precipitation_probability"][idx]
        logger.info(
            f"weather:summary temperature={state.temperature} rain_probability={state.rain_probability}"
        )
    except Exception as e:
        logger.error("task:fetch:weather:error", exc_info=e)
    await asyncio.sleep(WEATHER_FETCH_INTERVAL)
    asyncio.create_task(fetch_weather(loop, state))
