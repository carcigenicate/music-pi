import subprocess as sp

def test():
    with sp.Popen(["mpg123", "-R"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.DEVNULL) as proc:
        proc.stdout = sp.DEVNULL

        proc.stdin.write(b"load test.mp3\n")
        proc.stdin.flush()

        print("Playing...")

        while True:
            line = proc.stdout.readline()

            if not line:
                break

            print(line)

        print("Ended")