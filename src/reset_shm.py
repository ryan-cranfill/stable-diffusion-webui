# Clean up/delete all shared memories
import SharedArray as sa
from UltraDict import UltraDict

if __name__ == '__main__':

    from src import settings
    from src.utils import connect_to_shared

    # Delete shared settings
    # Unlink both shared memory buffers possibly used by UltraDict
    print('Deleting shared settings...')
    name = settings.SHARED_SETTINGS_MEM_NAME
    UltraDict.unlink_by_name(name, ignore_errors=True)
    UltraDict.unlink_by_name(f'{name}_memory', ignore_errors=True)
    print('Done')

    # Delete image shared memories
    print('Deleting image shared memories...')
    for name in settings.SHM_NAMES:
        print(f'Deleting {name}...')
        try:
            sa.delete(name)
        except FileNotFoundError:
            print(f'FileNotFoundError: {name} does not exist')
        try:
            sa.delete(f'shm://{name}')
        except FileNotFoundError:
            print(f'FileNotFoundError: shm://{name} does not exist')
    print('Done')

    UltraDict.get_memory()