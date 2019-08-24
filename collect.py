"""
collect.py

Collection script for scooter data.

"""

import json
import requests
import time

from loguru import logger
from pathlib import Path


def stream_data(url: str, cooldown: int) -> None:
    """Stream data from some endpoint at a regular interval

    Hit the provided URL with a GET request at an interval specified by the cooldown. If
    new data is available, yield it back to the caller.

    Parameters
    --------
    url: str
        URL to access data from; must be accessible via GET request.

    cooldown: int
        The interval at which the data is refreshed.

    """

    last_updated = 0  # after request is made, will be unixtime
    while True:
        resp = requests.get(url)
        data = resp.json()

        if data["last_updated"] > last_updated:
            last_updated = data["last_updated"]
            logger.debug(f"New data available: {last_updated}")

            yield data
            time.sleep(cooldown)

        else:
            logger.debug(f"No data available yet")
            time.sleep(0.5)


def stream_and_write(name: str, url: str, cooldown: int):
    """Write streamed data to a file as it becomes available."""

    outdir = Path(name)
    if not outdir.exists():
        outdir.mkdir()

    stream = stream_data(url, cooldown)
    for data in stream:
        last_updated = data["last_updated"]
        with open(outdir.joinpath(f"{last_updated}.json"), "w") as f:
            json.dump(data, f, indent=4)
            logger.info(f"Wrote data from {last_updated} to file")


if __name__ == "__main__":
    stream_and_write("bird", "https://mds.bird.co/gbfs/chicago/free_bike_status.json", 14)
