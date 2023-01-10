import json

import SharedArray as sa
import numpy as np

from src.settings import TARGET_SIZE, SHARED_SETTINGS_MEM_NAME, DEFAULT_SHARED_SETTINGS


def make_shared_mem(name, shape, dtype=np.uint8):
    # Create a shared array, or delete and recreate if it already exists
    try:
        mem = sa.create(f'shm://{name}', shape, dtype=dtype)
    except FileExistsError:
        print('FileExistsError, deleting and recreating', name)
        sa.delete(name)
        mem = sa.create(f'shm://{name}', shape, dtype=dtype)
    return mem


class SharedMemManager:
    # Store several shared memory arrays in a single shared dict
    def __init__(self, names: list[str] = [], is_client=True, default_shape=TARGET_SIZE + (3,), default_dtype=np.uint8):
        self.names = names
        self.default_shape = default_shape
        self.default_dtype = default_dtype
        self.is_client = is_client
        self.shared_mems = {}

        if is_client:
            for name in names:
                self.shared_mems[name] = sa.attach(f'shm://{name}')
        else:
            for name in names:
                self.shared_mems[name] = make_shared_mem(name, default_shape, default_dtype)

    def add_item(self, name, shape=None, dtype=None):
        if name not in self.names:
            self.names.append(name)
            if self.is_client:
                self.shared_mems[name] = sa.attach(f'shm://{name}')
            else:
                self.shared_mems[name] = make_shared_mem(name, shape or self.default_shape, dtype or self.default_dtype)

    def __getitem__(self, name):
        return self.shared_mems.get(name)

    def __setitem__(self, name, value):
        self.shared_mems[name][:] = value

    def __delitem__(self, name):
        del self.shared_mems[name]

    def __contains__(self, name):
        return name in self.shared_mems

    def __iter__(self):
        return iter(self.shared_mems)

    def __len__(self):
        return len(self.shared_mems)

    def __repr__(self):
        return f"SharedMemManager({self.names})"

    def __str__(self):
        return f"SharedMemManager({self.names})"


class SharedDict:
    # A dictionary that is stored in shared memory
    # Gets serialized to JSON and stored in a shared memory numpy array
    # Only one process can be the "owner" of the shared memory
    # The rest can access it as clients
    def __init__(self, name: str = SHARED_SETTINGS_MEM_NAME, defaults: dict = DEFAULT_SHARED_SETTINGS,
                 # is_client=True, shm_size=1024*50):
                 is_client=True, shm_size=int(1e8)):
        self.name = name
        self.is_client = is_client
        if not is_client:
            dummy_arr = np.array([' ' * shm_size])
            self.shared = make_shared_mem(name, dummy_arr.shape, dtype=dummy_arr.dtype)
            self.shared[0] = json.dumps(defaults)
        else:
            self.shared = sa.attach(f"shm://{name}")

    def get(self, prop, default=None):
        items = json.loads(self.shared[0])
        return items.get(prop, default)

    def set(self, prop, value):
        items = json.loads(self.shared[0])
        items[prop] = value
        self.shared[0] = json.dumps(items)

    def __getitem__(self, prop):
        return self.get(prop)

    def __setitem__(self, prop, value):
        self.set(prop, value)

    def __contains__(self, prop):
        return prop in self.get(prop)

    def __del__(self):
        if not self.is_client:
            sa.delete(f"shm://{SHARED_SETTINGS_MEM_NAME}")

    def __repr__(self):
        return f"SharedDict({json.loads(self.shared[0])})"
