from time import sleep
from functools import partial

from managed_audio_player import ManagedAudioPlayer
from logging_util import setup_logger

try:
    from gpiozero import Button, LED
except ImportError:
    raise RuntimeError("You need GPIOZero to use controls. Run with --no-controls to start without controls enabled.")

is_playing = True

mod_but = Button(18)
prev_but = Button(23)
next_but = Button(25)
play_but = Button(24)
pin_a = Button(13)
pin_b = Button(19)
rotor_but = Button(26)
next_led = LED(12)
play_led = LED(16)
prev_led = LED(20)
mod_led = LED(21)

player_logger = setup_logger("player", "player.log")


# FIXME: Switch to RotaryEncoder class
def pin_a_rising(player: ManagedAudioPlayer) -> None:
    if pin_b.is_pressed:
        if mod_but.is_pressed:
            player_logger.info("Song Pitch Down 1")
            player.adjust_pitch(-0.01)
        else:
            player_logger.info("Volume Down 1")
            player.adjust_volume(-5)


def pin_b_rising(player: ManagedAudioPlayer) -> None:
    if pin_a.is_pressed:
        if mod_but.is_pressed:
            player_logger.info("Song Pitch Up 1")
            player.adjust_pitch(0.01)
        else:
            player_logger.info("Volume Up 1")
            player.adjust_volume(5)


def previous_button(player: ManagedAudioPlayer) -> None:
    if mod_but.is_pressed:
        player_logger.info("Seek Back")
        player.seek_by(-400000)
    else:
        player_logger.info("Previous Song")
        player.previous_song()
        player.stop()
    prev_led.on()
    sleep(1)
    prev_led.off()


def next_button(player: ManagedAudioPlayer) -> None:
    if mod_but.is_pressed:
        player_logger.info("Seek Forwards")
        player.seek_by(400000)
    else:
        player_logger.info("Next Song")
        player.next_song()
        player.stop()
    next_led.on()
    sleep(1)
    next_led.off()


def play_button(player: ManagedAudioPlayer) -> None:
    global is_playing
    if mod_but.is_pressed:
        player_logger.info("Pause Song")
        player.toggle_pause()
    else:
        player_logger.info("Play Song")
        is_playing = True
    play_led.on()
    sleep(1)
    play_led.off()


def rotor_button(player: ManagedAudioPlayer) -> None:
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
    sleep(1)
    mod_led.off()
    prev_led.off()
    play_led.off()
    next_led.off()


def main_control_loop(player: ManagedAudioPlayer, loop_retry_delay: int) -> None:
    pin_a.when_pressed = partial(pin_a_rising, player)
    pin_b.when_pressed = partial(pin_b_rising, player)
    prev_but.when_pressed = partial(previous_button, player)
    next_but.when_pressed = partial(next_button, player)
    play_but.when_pressed = partial(play_button, player)
    rotor_but.when_pressed = partial(rotor_button, player)
    mod_but.when_pressed = mod_led.on
    mod_but.when_released = mod_led.off

    while True:
        if is_playing:
            song_finished = player.play_current_song()  # Will block during playback
            if song_finished:
                player.next_song()
        sleep(loop_retry_delay)
