import inspect
from dataclasses import dataclass
from typing import Any, Callable, List


@dataclass
class Depends:
    fn: Callable


async def resolve_dependencies(fn: Callable, args: List[Any]) -> List[Any]:
    n = 0
    sig = inspect.signature(fn)
    args.extend([None] * (len(sig.parameters) - len(args)))
    for param in sig.parameters.values():
        if isinstance(param.default, Depends):
            args[n] = await param.default.fn()
        n += 1
    return args
