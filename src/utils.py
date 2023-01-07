import numpy as np
import SharedArray as sa


def make_shared_mem(name, shape, dtype=np.uint8):
    # Create a shared array, or delete and recreate if it already exists
    try:
        mem = sa.create(f'shm://{name}', shape, dtype=dtype)
    except FileExistsError:
        print('FileExistsError, deleting and recreating', name)
        sa.delete(name)
        mem = sa.create(f'shm://{name}', shape, dtype=dtype)
    return mem
