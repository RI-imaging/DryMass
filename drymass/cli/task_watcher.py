import multiprocessing as mp
import sys
import time
from threading import Thread


def print_percentage(print_prefix, count, max_count, abort):
    """Track count and max_count and print percentage on command line"""
    while max_count.value == 0 or count.value != max_count.value:
        if max_count.value == 0:
            perc = 0
        else:
            perc = count.value/max_count.value * 100
        print("{}{:.1f}%".format(print_prefix, perc), end="\r", flush=True)
        time.sleep(0.1)
        if abort.value:
            break
    # cleanup the console
    print(" "*(6+len(print_prefix)), end="\r")
    print(print_prefix, end="", flush=True)


class TaskWatcher(object):
    def __init__(self, print_prefix="Performing task..."):
        """A progress watcher for the command line"""
        self.print_prefix = print_prefix
        self.count = mp.Value('I', 0, lock=True)
        self.max_count = mp.Value('I', 0, lock=True)
        self.abort = mp.Value('I', 0, lock=True)
        self.thread = Thread(target=print_percentage,
                             args=(print_prefix, self.count, self.max_count,
                                   self.abort))
        # causes the thread to terminate when the main process ends
        self.thread.daemon = True

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, type, value, traceback):
        # check whether an exception has been raised
        if sys.exc_info() != (None, None, None):
            # A traceback will be printed; Keep the last line of the
            # progress visible.
            print("", flush=True)
        else:
            self.abort.value += 1  # tell the printer to stop doing its thing
            self.thread.join(timeout=.2)  # be patient
            if (self.max_count.value != 0
                    and self.max_count.value != self.count.value):
                # The tracked function is not properly updating
                # count and max_count.
                raise ValueError(
                    "`count`={} did not count to `max_count`={}".format(
                        self.count.value, self.max_count.value))
