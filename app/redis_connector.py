from datetime import datetime, timedelta
import json

import redis
import yaml
from yaml.loader import SafeLoader


class RedisConnector:
    """
    Подключение к БД Redis и методы взаимодействия с ней
    """

    def __init__(self):
        with open('configs.yaml', 'r') as file:
            redis_config = yaml.load(file, Loader=SafeLoader)['Redis']
        self.__host = redis_config['host']
        self.__port = redis_config['port']

    def update_admin_logs(self, changed_data: dict) -> None:
        """
        Запись в БД данных в формате строки по имени employee_id и по ключу текущего времени и даты в iso формате.
        Перед записью данные сериализуются из json
        :param changed_data: Словарь с измененными данными
        """
        employee_id = changed_data.pop('ID')
        time = (datetime.now() + timedelta(hours=3)).isoformat()
        with redis.Redis(host=self.__host, port=self.__port, db=0) as r:
            r.hset(employee_id, time, json.dumps(changed_data))

    def read_admin_logs(self, employee_id: str) -> dict:
        """
        Чтение записей из БД по имени employee_id и по всем возможным ключам.
        После получения данные десериализуются в json
        :param employee_id: ID сотрудника
        :return:
        """
        with redis.Redis(host=self.__host, port=self.__port, db=0) as r:
            result = {employee_id: dict()}
            try:
                keys = r.hkeys(employee_id)
            except KeyError:
                return result
            for key in keys:
                result[employee_id][datetime.fromisoformat(key.decode('utf-8'))] = json.loads(r.hget(employee_id, key))
        return result

    def update_ip_logs(self, ip_address: str) -> None:
        """
        Запись в БД данных в формате множества по имени текущей даты и по значению ip-адреса.
        :param ip_address: IP-адрес пользователя
        """
        if ip_address:
            date = datetime.now().strftime('%d.%m.%Y')
            with redis.Redis(host=self.__host, port=self.__port, db=1) as r:
                r.sadd(date, ip_address)

    def read_ip_logs(self, begin_date: datetime, end_date: datetime):
        """
        Чтение записей из БД по имени указанной даты.
        """
        result_summary = 0
        result = {'Всего за день': dict(), 'IP': dict()}
        while begin_date != end_date + timedelta(days=1):
            with redis.Redis(host=self.__host, port=self.__port, db=1) as r:
                str_date = begin_date.strftime('%d.%m.%Y')
                date_logs = r.smembers(str_date)
                result['IP'][str_date] = date_logs
                result['Всего за день'][str_date] = len(date_logs)
                result_summary += len(date_logs)
                begin_date = begin_date + timedelta(days=1)
        result['Всего за выбранные дни'] = result_summary
        return result

