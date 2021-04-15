from multiprocessing import Process, Queue
from os import getpid, getppid
from time import sleep

def proc1(q) -> None:
    try:
        i = 0
        while True:
            print(i)
            i += 1
            sleep(1)
    except KeyboardInterrupt:
        pass


def main():
    q = Queue()

    prod = Process(target=proc1, args=(q,))

    prod.start()

    print("Letting run for a bit...")
    sleep(3)
    prod.terminate()
    prod.join()
    prod.close()

    q.close()

