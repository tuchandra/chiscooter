"""
collect.py

Collection script for scooter data.

"""

import asyncio
import json
import requests

from loguru import logger
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


@dataclass
class StreamParams:
    name: str
    url: str
    cooldown: int

    def __post_init__(self):
        """Replace cooldown of zero"""

        if self.cooldown == 0:
            self.cooldown = 15


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

    outdir = Path("data") / datetime.now().strftime("%Y%m%d") / stream_name
    if not outdir.exists():
        outdir.mkdir(parents=True)

    with open(outdir.joinpath(f"{last_updated}.json"), "w") as f:
        json.dump(data, f, indent=4)
        logger.debug(f"Wrote data from {stream_name} at {last_updated} to file")


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
    while datetime.now().hour < 22:  # trial period ends at 10 PM nightly
        data = requests.get(url).json()

        if "lastUpdated" in data.keys():  # edge case for VeoRide not following the spec
            data["last_updated"] = data["lastUpdated"]

        if data["last_updated"] > last_updated:
            last_updated = data["last_updated"]
            logger.info(f"New data available for {name}: {last_updated}")

            write_to_file(data, name, last_updated)

            logger.debug(f"Sleeping {name} for {cooldown}")
            await asyncio.sleep(cooldown - 1)

        else:
            logger.debug(f"No data available yet for {name}")
            await asyncio.sleep(0.5)


@logger.catch
async def all_streams():
    stream_params: List[StreamParams] = [
        StreamParams(
            name="bird",
            url="https://mds.bird.co/gbfs/chicago/free_bike_status.json",
            cooldown=60,
        ),
        StreamParams(
            name="bolt",
            url="https://www.bolt.miami/bolt2/chi/gbfs/en/free_bike_status.json",
            cooldown=60,
        ),
        StreamParams(
            name="gruv",
            url="https://portal.clevrmobility.com/api/gbfs/chicago/en/free_bike_status/?format=json",
            cooldown=60,
        ),
        StreamParams(
            name="jump",
            url="https://gbfs.uber.com/v1/chicago/free_bike_status.json",
            cooldown=60,
        ),
        StreamParams(
            name="lime",
            url="https://data.lime.bike/api/partners/v1/gbfs/chicago/free_bike_status",
            cooldown=0,
        ),
        StreamParams(
            name="lyft",
            url="https://s3.amazonaws.com/lyft-lastmile-production-iad/lbs/chi/free_bike_status.json",
            cooldown=300,
        ),
        StreamParams(
            name="sherpa",
            url="https://mds.bird.co/gbfs/platform-partner/sherpa/chicago/free_bike_status.json",
            cooldown=60,
        ),
        StreamParams(
            name="spin",
            url="https://web.spin.pm/api/gbfs/v1/chicago/free_bike_status",
            cooldown=0,
        ),
        StreamParams(
            name="wheels",
            url="https://chicago-gbfs.getwheelsapp.com/free_bike_status.json",
            cooldown=30,
        ),
        StreamParams(
            name="veoride",
            url="https://share.veoride.com/api/share/gbfs/free_bike_status?area_name=Chicago",
            cooldown=0,
        ),
    ]

    await asyncio.gather(
        *[
            stream_data(params.name, params.url, params.cooldown)
            for params in stream_params
        ]
    )


if __name__ == "__main__":
    # Exception handling is overrated
    logger.add("logs/{time:YYYYMMDD}.log")
    while True:
        try:
            asyncio.run(all_streams())
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f"Restarting with a new log file ...")
