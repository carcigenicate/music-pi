from time import sleep
from functools import partial

from managed_audio_player import ManagedAudioPlayer
from logging_util import setup_logger

try:
    from gpiozero import Button, LED, RotaryEncoder
except ImportError as e:
    raise ImportError("You need GPIOZero to use controls. Run with --no-controls to start without controls enabled.") \
        from e


SONG_BREAK_DELAY_SECS = 2

SEEK_STEP = 400000
VOLUME_STEP = 5
PITCH_STEP = 0.01

mod_but = Button(18)
prev_but = Button(23)
next_but = Button(25)
play_but = Button(24)
rotor_enc = RotaryEncoder(13, 19)
rotor_but = Button(26)
next_led = LED(12)
play_led = LED(16)
prev_led = LED(20)
mod_led = LED(21)


player_logger = setup_logger("player", "player.log")


def rotor_clockwise(player: ManagedAudioPlayer) -> None:
    """Callback for volume/pitch control associated with the clockwise rotation of the rotary encoder"""
    if mod_but.is_pressed:
        player_logger.info("Song Pitch Up 1%")
        player.adjust_pitch(PITCH_STEP)
    else:
        player_logger.info("Volume Up 5%")
        player.adjust_volume(VOLUME_STEP)
    mod_led.blink(0.025, 0, 1, background=False)
    prev_led.blink(0.025, 0, 1, background=False)
    play_led.blink(0.025, 0, 1, background=False)
    next_led.blink(0.025, 0, 1, background=False)


def rotor_counter_clock(player: ManagedAudioPlayer) -> None:
    """Callback for volume/pitch control associated with the counter-clockwise rotation of the rotary encoder"""
    if mod_but.is_pressed:
        player_logger.info("Song Pitch Down 1%")
        player.adjust_pitch(-PITCH_STEP)
    else:
        player_logger.info("Volume Down 5%")
        player.adjust_volume(-VOLUME_STEP)
    next_led.blink(0.025, 0, 1, background=False)
    play_led.blink(0.025, 0, 1, background=False)
    prev_led.blink(0.025, 0, 1, background=False)
    mod_led.blink(0.025, 0, 1, background=False)


def previous_button(player: ManagedAudioPlayer) -> None:
    """Callback to control the previous song/seek back features associated with the previous button  """
    if mod_but.is_pressed:
        player_logger.info("Seek Back")
        player.seek_by(-SEEK_STEP)
    else:
        player_logger.info("Previous Song")
        player.previous_song()
        player.stop()
    prev_led.on()


def next_button(player: ManagedAudioPlayer) -> None:
    """Callback to control the next song/seek forwards features associated with the next button."""
    if mod_but.is_pressed:
        player_logger.info("Seek Forwards")
        player.seek_by(SEEK_STEP)
    else:
        player_logger.info("Next Song")
        player.next_song()
        player.stop()
    next_led.on()


def play_button(player: ManagedAudioPlayer) -> None:
    """Callback to control play/pause features associated with the play button."""
    player_logger.info("Toggle Pause")
    player.toggle_pause()
    play_led.on()


def rotor_button(player: ManagedAudioPlayer) -> None:
    """Callback to control mute/pitch reset features associated with the rotary encoder button."""
    if mod_but.is_pressed:
        player_logger.info("Reset Pitch")
        player.set_pitch(0)
    else:
        player_logger.info("Mute")
        player.toggle_mute()
    mod_led.on()
    prev_led.on()
    play_led.on()
    next_led.on()


def leds_off() -> None:
    """Turns all LED's off simultaneously."""
    prev_led.off()
    play_led.off()
    mod_led.off()
    next_led.off()


def main_control_loop(player: ManagedAudioPlayer, loop_try_delay: int) -> None:
    """Main playback loop for the controls.
    Blocks forever."""
    rotor_enc.when_rotated_clockwise = partial(rotor_clockwise, player)
    rotor_enc.when_rotated_counter_clockwise = partial(rotor_counter_clock, player)
    prev_but.when_pressed = partial(previous_button, player)
    next_but.when_pressed = partial(next_button, player)
    play_but.when_pressed = partial(play_button, player)
    rotor_but.when_pressed = partial(rotor_button, player)
    mod_but.when_pressed = mod_led.on

    mod_but.when_released = mod_led.off
    play_but.when_released = play_led.off
    next_but.when_released = next_led.off
    prev_but.when_released = prev_led.off
    rotor_but.when_released = leds_off

    try:
        while True:
            song_finished = player.play_current_song()  # Will block during playback
            if song_finished:
                player.next_song()
            sleep(loop_try_delay)
    finally:
        leds_off()

