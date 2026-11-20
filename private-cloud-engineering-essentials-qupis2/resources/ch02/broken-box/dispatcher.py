#!/usr/bin/python3
"""dispatcher: starts one child process per job and then forgets about it.

Installed as /opt/dispatcher/dispatcher.py and started by box-init.
The bug is deliberate: the parent never collects the exit status of its children.
"""
import os
import time

JOBS = 5


def run_job(number):
    """Pretend to do some work in a child process."""
    time.sleep(0.2)
    print("job %d done in pid %d" % (number, os.getpid()), flush=True)


def main():
    for number in range(1, JOBS + 1):
        pid = os.fork()
        if pid == 0:
            run_job(number)
            os._exit(0)
        print("dispatched job %d to pid %d" % (number, pid), flush=True)
        time.sleep(1)
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
