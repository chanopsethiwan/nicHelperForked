# AUTOGENERATED! DO NOT EDIT! File to edit: async.ipynb (unless otherwise specified).

__all__ = ['async_wrap', 'asyncMap', 'asyncAwaitMap']

# Cell
import asyncio
from functools import wraps, partial

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


# Cell
import multiprocessing.dummy
from typing import Callable, List, Any, Iterable
from beartype import beartype
@beartype
def asyncMap(f:Callable, data:Iterable[Any], threads:int = 5)->Any:
  p = multiprocessing.dummy.Pool(threads)
  return p.map(f,data)

# Cell
def asyncAwaitMap(f:Callable, data:Iterable[Any])->Any:
  af = async_wrap(f) # convert to async func
  async def runLoop():
    rtup = (af(i) for i in data)
    return await asyncio.gather(*rtup)
  return asyncio.run(runLoop())