#!/usr/bin/env python3
from time import sleep
from argparse import ArgumentParser

from managed_audio_player import ManagedAudioPlayer
from logging_util import setup_logger

# To avoid aggressive restarting
RESTART_DELAY_SECS = 3
SONG_BREAK_DELAY_SECS = 2

main_logger = setup_logger("main", "main.log")


def main(use_controls: bool = True) -> None:
    with ManagedAudioPlayer() as player:
        if use_controls:
            # Importing locally so main.py can be run without gpiozero installed if run with --no-controls.
            import controls
            controls.main_control_loop(player)
        else:
            while True:
                song_finished = player.play_current_song()  # Will block during playback
                if song_finished:
                    player.next_song()
                sleep(SONG_BREAK_DELAY_SECS)


def resilient_main(use_controls: bool = True) -> None:
    """Will attempt to recover from failure to maintain uptime.
    Allow for exiting via keyboard interrupts."""
    while True:
        try:
            main(use_controls)
        except Exception as e:
            main_logger.warning(f"Music Pi service died with error: {e}. Restarting...")
        except KeyboardInterrupt:
            break
        sleep(RESTART_DELAY_SECS)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", "--resilient", action="store_true",
                        help="Will restart itself on failure until a keyboard interrupt is received.")
    parser.add_argument("-n", "--no-controls", action="store_false",
                        help="Disables controls")
    args = parser.parse_args()

    if args.resilient:
        resilient_main(args.no_controls)
    else:
        main(args.no_controls)
