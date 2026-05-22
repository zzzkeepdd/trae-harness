import time
import threading
from collections import OrderedDict

class Cache:
    def __init__(self, max_size=100):
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        self._max_size = max_size
        self._store = OrderedDict()
        self._ttl = {}
        self._lock = threading.Lock()

    def _now(self):
        return time.monotonic()

    def set(self, key, value, ttl=None):
        with self._lock:
            if key in self._store:
                self._store[key] = value
                self._store.move_to_end(key)
                if ttl is not None:
                    self._ttl[key] = self._now() + ttl
                elif key in self._ttl:
                    del self._ttl[key]
                return

            while len(self._store) >= self._max_size:
                self._store.popitem(last=False)

            self._store[key] = value
            if ttl is not None:
                self._ttl[key] = self._now() + ttl

    def get(self, key):
        with self._lock:
            if key not in self._store:
                return None

            if key in self._ttl and self._now() >= self._ttl[key]:
                del self._store[key]
                del self._ttl[key]
                return None

            self._store.move_to_end(key)
            return self._store[key]

    def delete(self, key):
        with self._lock:
            self._store.pop(key, None)
            self._ttl.pop(key, None)

    def size(self):
        with self._lock:
            return len(self._store)

    def clear(self):
        with self._lock:
            self._store.clear()
            self._ttl.clear()