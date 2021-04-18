from time import sleep

from managed_audio_player import ManagedAudioPlayer

SONG_BREAK_DELAY_SECS = 2

is_playing = True

def next_song_callback(player: ManagedAudioPlayer) -> None:
    player.next_song()
    player.stop()  # To stop current playback so the next song can run

def previous_song_callback(player: ManagedAudioPlayer) -> None:
    player.previous_song()
    player.stop()

def stop_callback(player: ManagedAudioPlayer) -> None:
    global is_playing
    is_playing = False
    player.stop()

def play_callback() -> None:
    global is_playing
    is_playing = True

def main_control_loop(player: ManagedAudioPlayer) -> None:
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