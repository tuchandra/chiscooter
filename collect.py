"""
collect.py

Collection script for scooter data.

"""

import asyncio
import json
import requests

from loguru import logger
from typing import NamedTuple
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


class StreamParams(NamedTuple):
    name: str
    url: str
    cooldown: int


def write_to_file(data: Dict[Any, Any], stream_name: str, last_updated: int) -> None:
    """Write response data to an output file.

    Parameters
    --------
    data: Dict[Any, Any]
        Dictionary of response data. This will be written as to a JSON file without
        concern for its contents.

    stream_name: str
        The name of the stream from which the data came

    last_updated: int
        The Unix time at which the data was generated. We say int, but this is really what
        the filename will be; it could be anything.

    """

    outdir = Path(stream_name)
    if not outdir.exists():
        outdir.mkdir()

    with open(outdir.joinpath(f"{last_updated}.json"), "w") as f:
        json.dump(data, f, indent=4)
        logger.info(f"Wrote data from {stream_name} at {last_updated} to file")


async def stream_data(name: str, url: str, cooldown: int) -> Any:
    """Asyncrhonously data from some endpoint at a regular interval

    Hit the provided URL with a GET request at an interval specified by the cooldown. If
    new data is available, yield it back to the caller. In the meantime, sleep and cede
    control back to the main event loop.

    Parameters
    --------
    name: str
        The (preferably short) name of the stream that we're getting data from

    url: str
        URL to get data from; must be accessible via GET request.

    cooldown: int
        The interval at which the data is refreshed.
    """

    last_updated = 0  # after request is made, will be unixtime
    while True:
        data = requests.get(url).json()

        if data["last_updated"] > last_updated:
            last_updated = data["last_updated"]
            logger.debug(f"New data available for {name}: {last_updated}")

            write_to_file(data, name, last_updated)
            await asyncio.sleep(cooldown - 1)

        else:
            logger.debug(f"No data available yet for {name}")
            await asyncio.sleep(0.5)


async def all_streams():
    stream_params: List[StreamParams] = [
        StreamParams(name="bird", url="https://mds.bird.co/gbfs/chicago/free_bike_status.json", cooldown=15),
        StreamParams(name="lime", url="https://data.lime.bike/api/partners/v1/gbfs/chicago/free_bike_status", cooldown=10),
    ]

    await asyncio.gather(
        *[stream_data(params.name, params.url, params.cooldown) for params in stream_params]
    )


if __name__ == "__main__":
    asyncio.run(all_streams())
