"""
TODO: import log this way is not best practice
The best practice is to config the logger in the main module, and get
```
logger = logging.getLogger(__name__)
```
in every module as a module level variable.
"""
import functools
import logging
import time

import logging as log


def pretty_time(t):
    if t < 1:
        return f'{t * 1000:.1f} ms'
    return f'{t:.3f} s'


def timing(
        func=None, *,
        log_params: bool = False,
        log_start: bool = False,
        log_level: int = logging.DEBUG,
):
    """
    Log the time used by the function call.

    Parameters
    ----------
    func
    log_params
        Log the input arguments of the function.
    log_start
        Log the time when the function is being called.
    log_level
        Use logging.DEBUG (10), logging.INFO (20), logging.WARNING (30), and etc.

    Examples
    --------
    >>> from utils import timing
    >>> @timing
    ... def f():
    ...     pass

    >>> @timing(log_params=True)
    ... def g():
    ...     pass
    """

    if func is None:
        return functools.partial(
            timing,
            log_params=log_params,
            log_start=log_start,
            log_level=log_level,
        )

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if log_start:
            log.log(log_level, '`%s` starts', func.__qualname__)
        if log_params:
            log.log(log_level, '`%s` args %s, %s', func.__qualname__, args, kwargs)

        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()

        log.log(
            log_level,
            '`%s` takes %s', func.__qualname__, pretty_time(time_end - time_start)
        )
        return result

    return wrapper


def log_error(func):
    """Strongly **discouraged** to use it. Only use it to clean the legacy code."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if result is not None:
                raise ValueError('Functions with return values should not use this decorator.')
        except:
            log.exception('Error in `%s`', func.__qualname__)

    return wrapper
