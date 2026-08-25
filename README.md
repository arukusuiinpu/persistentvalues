# persistentvalues

Contains a PersistentValue object that stores the input object as self.value and allows you to interact with it directly as if the object is its own value.

---
To modify the stored value, use:
```pycon
persistentValue.value = (something)
```
or
```pycon
persistentValue.set((something))
```

---
To get the stored value, use:
```pycon
(variable) = persistentValue.value
```
or
```pycon
(variable) = persistentValue()
```

---
Mutations work too!
```pycon
persistentValue = PersistentValue([2, 3, 1])
persistentValue.sort()
print(persistentValue)
[1, 2, 3]
```


---
Unfortunately I could not yet implement generic hinting for persistent values, so here is one of the ways to tell your IDE that your persistent value should behave almost the same as its value:
```pycon
l: Union[list, PersistentValue] = PersistentValue([1, 2, 3])
"""
^ l now has both 'PersistentValue' and 'list' hints
"""
```
or if you're on Python 3.10 and higher:
```pycon
l: list | PersistentValue = PersistentValue([1, 2, 3])
```
(Remember that assignment to l is still requiring l.value to be modified, it's just now easier to work with your value)

---
The input value of PersistentValue(0) is an id determining what cache corresponds to which PersistentValue. That means the following code will use the same cached value despite the intention obviously being in creation of two different persistent values:
```pycon
a = PersistentValue(0) # <- create a new persistentValue
b = PersistentValue(0) # <- has the same id as the previous one, so behaves like the same object

a += 2 # <- now stores 2
b += 3 # <- now stores 5
```

---
You can define your own id using:
```pycon
a = PersistentValue(0, id=(your id))
```
Which means:
```pycon
a = PersistentValue(0, "a") # <- create a new persistentValue with id "a"
b = PersistentValue(0, "b") # <- create a new persistentValue with id "b"

a += 2 # <- "a" now stores 2
b += 3 # <- "b" now stores 3
```

---
Your persistent values may have different types of access depending on your intentions:
```pycon
acc_0 = PersistentValue(None, id="acc_0", access=("script" or 0))
"""
^ (Default) Local script access, values with the same id from different scripts don't overlap.
  Python console is the exception, it is actually access=1 by default.
"""

acc_1 = PersistentValue(None, id="acc_1", access=("cwd" or "local" or 1))
"""
^ Local current working directory access, values with the same id from different working directories
  don't overlap, but can be accessed across different scripts from the same working directory.
"""

acc_2 = PersistentValue(None, id="acc_2", access=("global" or 2))
"""
^ Global device access, any values with the same id will be accessible across any scripts on your
  device from any projects as long as they all use the same cache_dir folder (Default "~/.cachier/").
  Requires access to the cache_dir from the script context.
"""
```

---
Additional parameters:
```pycon
PersistentValue(cache_dir=(your path))
"""
^ Cache path to store values at. Overrides the default automatic one determined by access.
  
  Default:
      access=0 -> ".cache/"
      access=1 -> ".cache/"
      access=2 -> "~/.cachier/"
"""

PersistentValue(separate_files=(True or False))
"""
^ Instead of a single cache file per-function, each function's cache is split between
  several files, one for each argument set. This can help if your per-function cache
  files become too large.
  
  Default: False
"""
```

---
PersistentValue functions:
```pycon
persistentValue.sync() # <- Syncs the uncached stored value with the cached one. (sets self._value = (cached)self.value)

persistentValue.update_cache() # <- Syncs the cached stored value with the uncached one. (sets (cached)self.value = self._value)

persistentValue.clear_cache() # <- Clears the cached value
```

---
Example usage:
```pycon
import random
from persistentvalues import PersistentValue

a = """Option 0
Option 1
Option 2
Option 3
Option 4
Option 5
Option 6""".split("\n")

b: list | PersistentValue = PersistentValue([(i, 0) for i in a], "b") # <- store the initial value under id "b"
last: list | PersistentValue = PersistentValue([None for _ in range(2)]) # <- store the initial value under procedural id derived from the initial value

def get_random_option():
    global last, b
    ch = random.choices(b(), weights=[(1 / j if i not in last() else 0) if j > 0 else 1 for i, j in b()], k=1)[0] # <- get the values here and use them just like the initial ones

    b[b.index(ch)] = (ch[0], ch[1] + 1) # <- modify b using assignment

    last.insert(0, ch); last.pop(-1) # <- modify last using mutation

    return ch[0]

if __name__ == "__main__":
    print(get_random_option()) # <- each time the program is executed we update the list of already chosen options 
```

Console Example:
```pycon
>>> from persistentvalues import PersistentValue
>>> a = PersistentValue(0)
>>> a.value += 1
>>> a
1

Process finished with exit code 0

>>> from persistentvalues import PersistentValue
>>> a = PersistentValue(0)
>>> a
1

Process finished with exit code 0
```

Local current working directory access:
```pycon
# ./test_pers0.py

from persistentvalues import PersistentValue

a = PersistentValue(0, access=1)

a.value += 1

print(a)
1
```

```pycon
# ./test_pers1.py

from persistentvalues import PersistentValue

a = PersistentValue(0, access=1)

print(a)
1
```