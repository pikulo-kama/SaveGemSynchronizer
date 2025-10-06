import cProfile
import pstats
import functools
import logging
import sys
import time

from savegem.common.util.logger import get_logger


def measure_time(when=logging.DEBUG):
    """
    Decorator that measures execution time.
    Logs only if logger is enabled for the given level.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            module = sys.modules[func.__module__]
            logger = get_logger(module.__name__)

            if not logger.isEnabledFor(when):
                return func(*args, **kwargs)

            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()

            logger.log(when, f"{module.__name__}:{func.__name__} took {end - start:.2f} seconds")
            return result

        return wrapper

    return decorator


def profile(function):  # pragma: no cover
    """
    Used to measure execution time
    of provided function.
    """

    profiler = cProfile.Profile()
    profiler.enable()

    function()

    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumtime')
    stats.print_stats(20)
