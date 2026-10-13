class Pair:
    def __init__(self, key, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pair):
            return NotImplemented
        return self._key == other._key and self._value == other._value

    def __iter__(self):
        yield self._key
        yield self._value

    def __repr__(self) -> str:
        return f"Pair({self._key!r}, {self._value!r})"

    def __str__(self) -> str:
        return f"{self._key} = {self._value}"


class PairMap:
    def __init__(self, pairs=()):
        self._pairs = []
        for key, value in pairs:
            self.put(key, value)

    @property
    def size(self) -> int:
        return len(self._pairs)

    def _find(self, key):
        for pair in self._pairs:
            if pair.key == key:
                return pair
        return None

    def put(self, key, value):
        found = self._find(key)
        if found is None:
            self._pairs.append(Pair(key, value))
        else:
            found.value = value

    def get(self, key, default=None):
        found = self._find(key)
        return default if found is None else found.value

    def remove(self, key) -> bool:
        found = self._find(key)
        if found is None:
            return False
        self._pairs.remove(found)
        return True

    def bump(self, key, step: int = 1) -> int:
        value = int(self.get(key, 0)) + step
        self.put(key, value)
        return value

    def keys(self) -> tuple:
        return tuple(pair.key for pair in self._pairs)

    def values(self) -> tuple:
        return tuple(pair.value for pair in self._pairs)

    def items(self) -> tuple:
        return tuple(self._pairs)

    def clear(self):
        self._pairs.clear()

    def __getitem__(self, key):
        found = self._find(key)
        if found is None:
            raise KeyError(key)
        return found.value

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        if not self.remove(key):
            raise KeyError(key)

    def __contains__(self, key) -> bool:
        return self._find(key) is not None

    def __iter__(self):
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._pairs)

    def __bool__(self) -> bool:
        return bool(self._pairs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PairMap):
            return NotImplemented
        return self.items() == other.items()

    def __repr__(self) -> str:
        return f"PairMap({[tuple(pair) for pair in self._pairs]!r})"

    def __str__(self) -> str:
        return "; ".join(str(pair) for pair in self._pairs)
