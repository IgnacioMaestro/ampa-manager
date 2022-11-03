from random import choice


class SecretKeyManager:
    @staticmethod
    def load_or_create_key(secret_file: str) -> str:
        try:
            secret_key_file = open(secret_file)
            secret_key = secret_key_file.read().strip()
            secret_key_file.close()
        except IOError:
            try:
                with open(secret_file, 'w') as f:
                    secret_key = SecretKeyManager.gen_secret_key()
                    f.write(secret_key)
            except IOError:
                raise FileNotFoundError('Cannot open file `%s` for writing.' % secret_file)
        return secret_key

    @staticmethod
    def gen_secret_key():
        return SecretKeyManager.gen_secret_key_params(
            character_list='abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)', length=50)

    @staticmethod
    def gen_secret_key_params(character_list, length):
        return ''.join([choice(character_list) for _ in range(length)])
