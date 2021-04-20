from time import sleep
from gpiozero import Button,LED
from managed_audio_player import ManagedAudioPlayer

SONG_BREAK_DELAY_SECS = 2

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

def main_control_loop(player: ManagedAudioPlayer) -> None:
    def pin_a_rising():
        if pin_b.is_pressed:
            if mod_but.is_pressed:
                print("Song Pitch Down 1")
                player.adjust_pitch(-0.01)
            else:
                print("Volume Down 1")
                player.adjust_volume(-5)

    def pin_b_rising():
        if pin_a.is_pressed:
            if mod_but.is_pressed:
                print("Song Pitch Up 1")
                player.adjust_pitch(0.01)
            else:
                print("Volume Up 1")
                player.adjust_volume(5)

    def previous_button():
        if mod_but.is_pressed:
            print("Seek Back")
            player.seek_by(-400000)
        else:
            print("Previous Song")
            player.previous_song()
            player.stop()
        prev_led.on()
        sleep(1)
        prev_led.off()

    def next_button():
        if mod_but.is_pressed:
            print("Seek Forwards")
            player.seek_by(400000)
        else:
            print("Next Song")
            player.next_song()
            player.stop()
        next_led.on()
        sleep(1)
        next_led.off()

    def play_button():
        global is_playing
        if mod_but.is_pressed:
            print("Pause Song")
            player.toggle_pause()
        else:
            print("Play Song")
            is_playing = True
        play_led.on()
        sleep(1)
        play_led.off()

    def rotor_button():
        if mod_but.is_pressed:
            print("Reset Pitch")
            player.set_pitch(0)
        else:
            print("Mute")
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

    pin_a.when_pressed = pin_a_rising
    pin_b.when_pressed = pin_b_rising
    prev_but.when_pressed = previous_button
    next_but.when_pressed = next_button
    play_but.when_pressed = play_button
    rotor_but.when_pressed = rotor_button
    mod_but.when_pressed = mod_led.on
    mod_but.when_released = mod_led.off
    # global is_playing  # TODO: Eww
    # play_button.on_press = play_callback
    # stop_button.on_press = lambda: stop_callback(player)
    # next_button.on_press = lambda: next_song_callback(player)
    # previous_button.on_press = lambda: previous_song_callback(player)
    #
    while True:
        if is_playing:
            song_finished = player.play_current_song()  # Will block during playback
            if song_finished:
                player.next_song()
        sleep(SONG_BREAK_DELAY_SECS)
