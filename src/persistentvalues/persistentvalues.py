from functools import partial
from hashlib import sha256
import os
import __main__
from os import PathLike
from typing import Generic, TypeVar, Union

from cachier import cachier

T = TypeVar('T')

class PersistentValue(Generic[T]):

    def __init__(self, value: T = None, id: str = None, access: str | int = "script",
                 cache_dir: str | PathLike | None = None, separate_files: bool = False) -> None:
        """
        The PersistentValue object. Stores the value in the cache with access determined by the access value.

        :param value: The value to store
        :param id: Unique identifier of the persistent value
        :param access: Whether to store the value locally for only the current script ("script" or 0), locally for the current working directory ("cwd" or "local" or 1), or globally across the whole device ("global" or 2).
        :param cache_dir: (Default automatic) The directory to store the cached value in. Default relies on access, "~/.cachier/" for global, ".cache/" for the rest
        :param separate_files: Instead of a single cache file per-function, each function's cache is split between several files, one for each argument set. This can help if your per-function cache files become too large.
        """

        self.cache_dir = cache_dir or (None if access in ("global", 2, "2") else ".cache/")
        self.cached = True

        @cachier(cache_dir=self.cache_dir, separate_files=separate_files)
        def get_value(id):
            _ = id
            self.cached = False
            return self._value

        self.get_value = get_value

        if access not in (0, 1, 2, "0", "1", "2", "script", "cwd", "local", "global"):
            raise ValueError("Access must be 0, 1, 2, '0', '1', '2', 'script', 'cwd', 'local', or 'global'.")

        if not hasattr(__main__, "__file__"):
            access = 1

        self.id = sha256((repr(id if id is not None else value) + (
            __main__.__file__ if access in ("script", 0, "0") else (
                os.getcwd() if access in ("cwd", "local", 1, "1") else ""))).encode()).hexdigest()

        self._value = value
        self._value = get_value(self.id)

    def __setattr__(self, key, value):
        if key in ['_value', 'id', 'value', 'cache_dir', 'get_value', 'cached']:
            return object.__setattr__(self, key, value)
        return setattr(self.value, key, value)

    def _mutate_attr(self, name, *args, **kwargs):
        l = self.value
        func_value = getattr(l, name)(*args, **kwargs)
        self.value = l

        return func_value

    def __getattr__(self, name):
        return partial(self._mutate_attr, name)

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        l = self.value
        l[key] = value
        self.value = l

    def set(self, value):
        self.value = value

    def sync(self):
        self._value = self.value

    def update_cache(self):
        self.get_value(self.id, cachier__overwrite_cache=True)

    def clear_cache(self):
        self.get_value.clear_cache()

    @property
    def value(self):
        return self.get_value(self.id)

    @value.setter
    def value(self, value):
        self._value = value
        self.update_cache()

    def __call__(self):
        return self.value

    def __eq__(self, other):
        return object.__eq__(self.value, other)

    def __hash__(self):
        return self.value.__hash__()

    def __str__(self):
        return self.value.__str__()

    def __repr__(self):
        return self.value.__repr__()