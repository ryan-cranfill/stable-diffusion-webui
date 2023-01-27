import qrcode
import shelve
import random
from threading import Lock

from src import settings

mutex = Lock()


# A class to manage current passcodes and validate them
class CodeManager:
    def __init__(self):
        pass

    def get_code(self):
        # Check if there is an unclaimed code and return it if so
        with mutex:
            with shelve.open(settings.CODES_CACHE_PATH) as db:
                if 'codes' in db:
                    if len(db['codes']) > 0:
                        return random.choice(list(db['codes']))

        return self.generate_code()

    def generate_code(self, length=6):
        # Generate a random code of length 'length'
        code = ''.join(random.choice('0123456789') for i in range(length))
        self.save_code(code)
        return code

    def save_code(self, code):
        # Save the code to the database, letting us know that a client has taken it
        with mutex:
            with shelve.open(settings.CODES_CACHE_PATH, writeback=True) as db:
                if 'codes' not in db:
                    db['codes'] = set()
                db['codes'].add(code)

    def confirm_code(self, code):
        # Confirm that a code has been claimed
        with mutex:
            with shelve.open(settings.CODES_CACHE_PATH, writeback=True) as db:
                if 'codes' not in db:
                    return False

                if code in db['codes']:
                    db['codes'].remove(code)
                    if 'confirmed_codes' not in db:
                        db['confirmed_codes'] = set()
                    db['confirmed_codes'].add(code)
                    return True
                else:
                    return False

    def code_is_unclaimed(self, code):
        # Check if the code is in the database
        with mutex:
            with shelve.open(settings.CODES_CACHE_PATH) as db:
                if 'codes' not in db:
                    return False

                if code in db['codes']:
                    return True
                else:
                    print(db['codes'])
                    return False

    def validate_code(self, code):
        # Check if the code is in the database
        with mutex:
            with shelve.open(settings.CODES_CACHE_PATH) as db:
                if 'confirmed_codes' not in db:
                    return False

                if code in db['confirmed_codes']:
                    return True
                else:
                    return False

    def remove_code(self, code):
        # Remove the code from the database
        with mutex:
            with shelve.open(settings.CODES_CACHE_PATH, writeback=True) as db:
                if 'confirmed_codes' not in db:
                    return False

                if code in db['confirmed_codes']:
                    db['confirmed_codes'].remove(code)
                    return True
                else:
                    return False

    def expire(self, code):
        # alias for remove_code
        self.remove_code(code)
