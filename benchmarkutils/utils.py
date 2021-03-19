

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
  level.s
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


def record_timing(keys, values, iteration, walltime, dictionary):
  """
  Record `values` into `dictionary`.
  """
  if iteration == 0:
    last_key = ['initial']
  else:
    last_key = ['subsequent']
  dict_keys = [f'{k}={v}' for k, v in zip(keys, values)] + last_key
  return insert(dict_keys, walltime, dictionary)
