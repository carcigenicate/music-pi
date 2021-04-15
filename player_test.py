from threading import Thread
from managed_audio_player import ManagedAudioPlayer
from time import sleep


def player_loop(player: ManagedAudioPlayer):
    while True:
        result = player.play_current_song()
        if result:
            print("Song Ended...")
            print(2)
        else:
            print("Failed...")
            sleep(5)


def main():
    player = ManagedAudioPlayer()
    t = Thread(target=player_loop, args=[player], daemon=True)
    t.start()
    return t, player
