# chiscooter
Analyzing Chicago's scooter trial.

## Data collection
The Chicago scooter trial runs between the hours of 5AM and 10PM. The collection script is scheduled via crontab (`0 5 * * * cd ~/repos/scooter && make collect` is the line I use), and the script has logic to stop running at 10PM. Here, we use `make collect` to run the collection script; this requires GNU Make, and you'll have to update the paths to work for your machine. We started data collection on Thursday, September 19th.

## Requirements
We use Python 3.7. Lower versions will not work, as we make use of dataclasses and (I believe) newer features of asyncio. The environment is documented in `conda_env.yml`; it's Python 3.7 + [requests](https://github.com/psf/requests) + [loguru](https://github.com/Delgan/loguru).
