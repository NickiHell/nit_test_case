from hashlib import pbkdf2_hmac


def encrypt_password(password: str) -> str:
    """
    Хеширует пароль
    :param password: сырая строка с паролем
    :return:
    """
    # Пока без соли, но если что можно SECRET_KEY
    hash_pass = pbkdf2_hmac('sha256', password.encode('utf-8'), b'', 100000)
    return hash_pass.hex()


def check_password(raw_pass, hashed_pass):
    """
    Проверяют совпадают ли пароли
    :param raw_pass: Строка с паролем
    :param hashed_pass: Хеш пароля
    """
    return True if hashed_pass == encrypt_password(raw_pass) else False
