import json
import re

import yaml
from yaml.loader import SafeLoader
from ldap3 import Server, Connection
from cryptography.fernet import Fernet


class AuthenticationConfig:
    def __init__(self):
        with open('active_directory_config.yaml', 'r', encoding='utf-8') as file:
            self.config = yaml.load(file, Loader=SafeLoader)


class ActiveDirectoryConnection:
    """
    Подключение к серверу Active Directory через LDAP
    """

    def __init__(self):
        self.__config = AuthenticationConfig().config
        self.__server = Server(self.__config['AD_SERVER'])
        self.__connection = Connection(
            self.__server,
            user=self.__config['AD_LOGIN'],
            password=self.__config['AD_PASSWORD']
        )

        if not self.__connection.bind():
            raise Exception('Не удалось установить соединение с ActiveDirectory')

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Проверка соответствия логина и пароля учетной записи в Active Directory
        """
        connection = Connection(
            self.__server,
            user=username,
            password=password,
        )

        if not connection.bind():
            return False
        return True

    def authorize_user(self, username: str) -> bool:
        """
        Проверка нахождения учетной записи в необходимой группе Active Directory
        """
        self.__connection.search(
            search_base=self.__config['AD_SEARCH_TREE'],
            search_filter=self.__config['AD_FILTER'],
            attributes=['sAMAccountName'],
            size_limit=0,
            paged_size=1000,
            paged_cookie=None,
        )
        for entry in self.__connection.entries:
            entry_info = json.loads(entry.entry_to_json())['attributes']
            username = re.findall(r'\\(.+)', username)
            if username and username[0] == entry_info['sAMAccountName'][0]:
                return True
        return False


class CookieUserName:
    """
    Формирование данных cookie для сохранения авторизации в системе
    """

    @classmethod
    def write_cookie_key(cls) -> None:
        """
        Создание ключа шифрования
        """
        key = Fernet.generate_key()
        with open('cookie.key', 'wb') as key_file:
            key_file.write(key)

    @staticmethod
    def load_cookie_key() -> bytes:
        """
        Получение ключа шифрования
        """
        return open('cookie.key', 'rb').read()

    @classmethod
    def verify_token(cls, token: str | bytes) -> str:
        """
        Верификация токена, переданного в cookie
        :return Расшифрованный токен
        """
        return Fernet(cls.load_cookie_key()).decrypt(token).decode('utf-8')

    def __init__(self, username: str):
        self.key = 'token'
        self.value = (Fernet(self.load_cookie_key()).encrypt(bytes(username, 'utf-8'))).decode('utf-8')
        self.max_age = 1800     # Время жизни cookie в секундах
