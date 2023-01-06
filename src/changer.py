import random
import time
import numpy as np
from PIL import Image
from pathlib import Path
import SharedArray as sa
from screeninfo import get_monitors


THIS_FILE = Path(__file__).resolve().absolute()
ROOT_DIR = THIS_FILE.parent
# IMAGE_OPTIONS = list((ROOT_DIR / 'outputs' / 'img2img-images').glob('*.png'))
IMAGE_OPTIONS = list(Path('/Users/ryan/Downloads/stained-glass-cats/donkey1_upscayled/').glob('*.png'))
TEST_IMAGES = [Image.open(img) for img in IMAGE_OPTIONS[:10]]

TARGET_SIZE = (512, 512)
TEST_IMAGES = [img.resize(TARGET_SIZE) for img in TEST_IMAGES]

monitors = get_monitors()
print('monitors:', monitors)

img_dim = np.array(TEST_IMAGES[0]).shape
print('img_dim:', img_dim)

changes = np.zeros(len(monitors), dtype=np.int8)
changes_shared_mem = sa.create(f"shm://changes", changes.shape, dtype=changes.dtype)

shared_mems = []
for i in range(len(monitors)):
    try:
        shared_mems.append(sa.create(f"shm://img_{i}", img_dim, dtype=np.uint8))
    except FileExistsError:
        print('FileExistsError, deleting and recreating', f"shm://img_{i}")
        sa.delete(f"shm://img_{i}")
        shared_mems.append(sa.create(f"shm://img_{i}", img_dim, dtype=np.uint8))
        # shared_mems.append(sa.attach(f"shm://img_{i}"))

while True:
    for i in range(len(monitors)):
        if random.random() > 0.1:
            continue
        choice = random.choice(TEST_IMAGES)
        shared_mems[i][:] = np.array(choice)
        changes_shared_mem[i] = 1
    time.sleep(.05)

# shared_mems = [sa.attach(f'shared_mem_{i}') for i in range(2)]