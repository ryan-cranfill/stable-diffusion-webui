import random
import time
import numpy as np
from PIL import Image
from pathlib import Path
import SharedArray as sa
from screeninfo import get_monitors

from src.sharing import make_shared_mem, SharedDict, SharedMemManager
from src.settings import TARGET_SIZE, IMAGE_OPTIONS

shared_settings = SharedDict(is_client=False)
shared_mem_manager = SharedMemManager(is_client=False)


# TEST_IMAGES = [Image.open(img) for img in IMAGE_OPTIONS[:10]]
# TEST_IMAGES = [img.resize(TARGET_SIZE) for img in TEST_IMAGES]
#
# monitors = get_monitors()
# print('monitors:', monitors)
#
# img_dim = np.array(TEST_IMAGES[0]).shape
# print('img_dim:', img_dim)
#
# changes = np.zeros(len(monitors), dtype=np.int8)
# changes_shared_mem = make_shared_mem('changes', changes.shape, dtype=changes.dtype)
#
# shared_mem_names = [f"img_{i}" for i in range(len(monitors))]
# shared_mems = [make_shared_mem(name, img_dim, dtype=np.uint8) for name in shared_mem_names]

while True:
    # for i in range(len(monitors)):
    #     if random.random() > 0.99:
    #         continue
    #     choice = random.choice(TEST_IMAGES)
    #     shared_mems[i][:] = np.array(choice)
    #     changes_shared_mem[i] = 1
    time.sleep(.5)
