import time
import functools as fct
CACHED_FUNS = set()

def timing(fun, logger):
  key = fun.__name__
  @fct.wraps(fun)
  def wrapped(*args, **kwargs):
    global CACHED_FUNS
    warmup = False
    if fun not in CACHED_FUNS:
      warmup = True
      CACHED_FUNS |= {fun,}
    t1 = time.time()
    out = fun(*args, **kwargs)
    t2 = time.time()
    if isinstance(out, tuple):
      for o in out:
        if hasattr(o, 'block_until_ready'):
          o.block_until_ready()
          break
    else:
      if hasattr(out, 'block_until_ready'):
        out.block_until_ready()
    t3 = time.time()
    dt = time.time() - t1 - t3 + t2
    if key not in logger:
      logger[key] = dict()
    if warmup:
      logger[key]['warmup'] = dt
    else:
      if 'subsequent' not in logger[key]:
        logger[key]['subsequent'] = []
      logger[key]['subsequent'].append(dt)

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
