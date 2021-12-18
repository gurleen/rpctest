import functools
from typing import Callable
from beartype import beartype

rpc_functions = {}


def remote_proc_deco(func):
    rpc_functions[func.__name__] = func

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        value = func(*args, **kwargs)
        return value
    return wrapper_decorator


def remote_proc(func: Callable) -> Callable:
    return remote_proc_deco(beartype(func))