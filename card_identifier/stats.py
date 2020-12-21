import functools
import time


def measure_time(func):
    @functools.wraps(func)
    def wrapper(*arg, **kwds):
        t = time.time()
        res = func(*arg, **kwds)
        print("Function took " + str(time.time() - t) + " seconds to run")
        return res

    return wrapper
