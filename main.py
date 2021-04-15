#!/usr/bin/env python3
from time import sleep
from argparse import ArgumentParser

from song_service import SongService
import controls
from logging_util import setup_logger

# To avoid aggressive restarting
RESTART_DELAY_SECS = 3


main_logger = setup_logger("main", "main.log")


def main():
    with SongService() as service:
        controls.handle_controls(service)


def resilient_main():
    """Will attempt to recover from failure to maintain uptime.
    Allow for exiting via keyboard interrupts."""
    while True:
        try:
            main()
        except Exception as e:
            main_logger.warning(f"Music Pi service died with error: {e}. Restarting...")
        except KeyboardInterrupt:
            break
        sleep(RESTART_DELAY_SECS)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", "--resilient", action="store_true")
    args = parser.parse_args()

    if args.resilient:
        resilient_main()
    else:
        main()

