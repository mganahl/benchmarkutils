import time
import functools as fct
from typing import Callable, Dict
CACHED_FUNS = set()

def log_timing(fun:Callable, logger:Dict, key=None):
  """
  Decorator function to time `fun`, and store result
  in `logger`. `logger` is a `dict` type to which the
  timing results are written. The timings for `fun` are
  stored in the key `key = fun.__name__`.
  `logger[key]` is another `dict` type holding
  timings for calls to `fun`. If any of the
  outputs of `fun` is a jax type with an attribute
  `block_until_ready()`, the timing of the the first
  call to `fun` is stored in `logger[key]['warmup']`.
  All other timings are are stored in a list in
  `logger[key]['timings']`.

  Args:
    fun: Function to be timed.
    logger: A dictionary to store timings.

  Returns:
    Wrapped `fun`.
  """
  if key is None:
    key = fun.__name__
  @fct.wraps(fun)
  def wrapped(*args, **kwargs):
    global CACHED_FUNS
    warmup = fun not in CACHED_FUNS
    needs_blocking = False
    if fun not in CACHED_FUNS:
      CACHED_FUNS |= {fun,}
    t1 = time.time()
    out = fun(*args, **kwargs)
    t2 = time.time()
    if isinstance(out, tuple):
      for o in out:
        if hasattr(o, 'block_until_ready'):
          o.block_until_ready()
          needs_blocking = True
          break
    else:
      if hasattr(out, 'block_until_ready'):
        out.block_until_ready()
        needs_blocking = True
    t3 = time.time()
    dt = time.time() - t1 - t3 + t2
    if key not in logger:
      logger[key] = dict()
    if warmup and needs_blocking:
      logger[key]['warmup'] = dt
    else:
      if 'timings' not in logger[key]:
        logger[key]['timings'] = []
      logger[key]['timings'].append(dt)
    return out
  return wrapped

def dict_depth(dictionary, current_depth):
  """
  Return the depth of the dictionary + current_depth.
  """
  if isinstance(dictionary, dict):
    if len(dictionary.keys()) > 0:
      return dict_depth(list(dictionary.values())[0], current_depth + 1)
    return current_depth + 1
  return current_depth


def insert(keys, value, dictionary):
  """
  Insert 'value' into a nested dict 'dictionary',
  using elements of `keys` on the different nesting
  levels
  """
  assert (dict_depth(dictionary, 0)
          == len(keys)) or (len(dictionary)
                            == 0), 'dict depth does not match key length'
  if len(keys) > 1:
    if keys[0] not in dictionary:
      dictionary[keys[0]] = {}
    insert(keys[1:], value, dictionary[keys[0]])
    return dictionary

  if keys[0] not in dictionary:
    dictionary[keys[0]] = []

  dictionary[keys[0]].append(value)
  return dictionary


def record_value(keys, values, iteration, value, dictionary):
  """
  Record `values` into `dictionary`.
  """
  if iteration == 0:
    last_key = ['initial']
  else:
    last_key = ['subsequent']
  dict_keys = [f'{k}={v}' for k, v in zip(keys, values)] + last_key
  return insert(dict_keys, value, dictionary)
