#! /usr/bin/env python3
import logging
import threading
from threading import Event
from queue import Queue
import time
import random

def serial_thread(name):
    logging.info("awoken")
    while True:
        job = jobs.get()
        logging.info(f"doing work {job[0]} ({job[1]}):")
        time.sleep(job[1])
        if job[0] == "shutdown":
            break
    logging.info("shutdown and cleanup complete")

if __name__ == "__main__":
    format = "%(asctime)s: %(funcName)s - %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("starting serial_thread")
    jobs = Queue()
    s = threading.Thread(target=serial_thread, args=(1,))
    s.start()
    try:
        while True:
            logging.info("doing stuff")
            time.sleep(random.randint(1,9))
            jobs.put(("importantjob", random.randint(1,9)))
    except (KeyboardInterrupt, SystemExit):
        logging.info("KeyboardInterrupt or SystemExit, shutting down main thread")
        jobs.put(("shutdown", 0))

    logging.info("waiting for serial_thread to finish")
    s.join()
    logging.info("all done")
