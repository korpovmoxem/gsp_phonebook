import json
from datetime import datetime

import pyodbc
import yaml
from yaml.loader import SafeLoader

from search import SearchEngine


class SqlServerConnector:
    """
    Подключение к БД Microsoft Sql-Server
    """

    def __init__(self):
        with open('sql_server_config.yaml', 'r') as file:
            sql_server_config = yaml.load(file, Loader=SafeLoader)

        self.__sql_connector = pyodbc.connect(
            f'DRIVER={sql_server_config["DRIVER"]};'
            f'SERVER={sql_server_config["SERVER"]};'
            f'UID={sql_server_config["UID"]};'
            f'PWD={sql_server_config["PWD"]};'
            f'Trusted_Connection=No;'
            f'Database={sql_server_config["Database"]};'
        )
        self.__db_name = f'{sql_server_config["Database"]}.dbo'
        self.__cursor = self.__sql_connector.cursor()

    @property
    def db_name(self) -> str:
        return self.__db_name

    def __execute_query(self, query: str) -> list | None:
        """
        Выполняет запрос и возвращает массив типа list если был указан 'SELECT' запрос
        :param query: Строка с SQL запросом
        :return: Данные, полученные запросом в БД
        """
        if 'select' in query.lower():
            return self.__cursor.execute(query).fetchall()

        self.__cursor.execute(query)
        self.__sql_connector.commit()

    def __get_column_names(self):
        """
        Получает наименования колонок в таблице БД, к которой последний раз отправлялся запрос
        """
        return [i[0] for i in self.__cursor.description]

    def get_formatted_data(self, query: str) -> list:
        """
        Возвращает данные, полученные SQL запросом в формате dict, где ключ - название столбца из таблицы
        :param query: Строка с SQL запросом
        :return: Список, в котором каждый элемент - строка таблицы в формате dict
        """
        raw_data = self.__execute_query(query)
        for i in range(len(raw_data)):
            raw_data[i] = list(map(lambda x: '' if not x else x, raw_data[i]))
        data_fields = self.__get_column_names()
        return list(map(lambda x: dict(zip(data_fields, x)), raw_data))

    def update_data(self, data: dict):
        """
        Обновляет данные в таблицах, в зависимости от ключа в словаре
        :param data: Словарь, в котором ключ - название атрибута таблицы в БД, значение - новое значение атрибута
        :return:
        """
        table_name = 'EditedEmployees'
        query = f"SELECT ID FROM {self.__db_name}.{table_name} WHERE ID = '{data['ID']}'"
        entry = self.__execute_query(query)
        data = dict(filter(lambda x: x[1], data.items()))
        data = dict(map(lambda x: (f"{x[0]}", f"'{x[1].replace('on', '1').replace('off', '0')}'"), data.items()))
        if entry:
            employee_id = data.pop('ID')
            query = f"UPDATE {self.__db_name}.{table_name} SET {','.join([f'{i[0]}={i[1]}' for i in data.items()])} WHERE ID = {employee_id}"
        else:
            query = f"INSERT INTO {self.__db_name}.{table_name} ({','.join(data.keys())}) VALUES ({','.join(data.values())})"
        print(query)
        self.__execute_query(query)


class DataBaseStorage(SearchEngine):
    """
    Хранилище всех данных из БД
    """

    def __fill_organizational_structure(self, employee: dict, employee_list: list, department_list: list) -> list:
        """
        Рекурсивное формирование последовательной оргструктуры департаментов в виде list
        :param employee: Данные сотрудника, для которого формируется оргструктура
        :param employee_list: Массив со всеми сотрудниками
        :param department_list: Массив со всеми департаментами
        """
        org_structure = list()
        if employee['ParentID'] != '00000000-0000-0000-0000-000000000000':
            if employee['ID'] != employee['BossID']:
                boss_info = list(filter(lambda boss: boss['ID'] == employee['BossID'], employee_list))
                if not boss_info:
                    return org_structure
                else:
                    boss_info = boss_info[0]
                org_structure += [
                    {
                        'DepartmentName': employee['DepartmentName'],
                        'DepartmentID': employee['DepartmentID'],
                        'OrganizationID': employee['OrganizationID'],
                        'FullNameRus': boss_info['FullNameRus'],
                        'PositionTitle': boss_info['PositionTitle'],
                        'ID': boss_info['ID']
                    }
                ]
                org_structure += self.__fill_organizational_structure(boss_info, employee_list, department_list)

        return org_structure

    def __fill_department_children(self, department: dict, departments_list: list) -> list:
        """
        Рекурсивное формирование структуры департаментов в виде dict
        :param department: Данные департамента, для которого формируется дерево дочерних департаментов
        :param departments_list: Массив со всеми департаментами
        """
        children_departments = list(filter(lambda children: children['ParentID'] == department['ID'], departments_list))
        current_tree = list()
        if children_departments:
            for child in children_departments:
                current_tree.append(
                    {
                        'ID': child['ID'],
                        'Name': child['Name'],
                        'Filial': child['Filial'],
                        'Inn': child['OrganizationID'],
                        'Children': self.__fill_department_children(child, departments_list),
                    }
                )
        return current_tree

    def __init__(self):
        super().__init__()
        connector = SqlServerConnector()
        self.employees = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.employees")
        self.departments = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.departments")
        self.organizations = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.organizations")
        self.edited_data = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.EditedEmployees")

        for row in self.employees:

            # Дополнение массива названием департамента и компании
            row['OrgStructure'] = list()
            row['insert_date'] = row['insert_date'].strftime('%d.%m.%Y %H:%M:%S') if isinstance(row['insert_date'], datetime) else row['insert_date']
            row['update_date'] = row['update_date'].strftime('%d.%m.%Y %H:%M:%S') if isinstance(row['update_date'], datetime) else row['update_date']
            row['OrganizationName'] = list(filter(lambda org: org['ID'] == row['OrganizationID'], self.organizations))[0]['Name']
            department = list(filter(lambda dep: dep['ID'] == row['DepartmentID'] and dep['OrganizationID'] == row['OrganizationID'], self.departments))
            if department:
                row['DepartmentName'] = department[0]['Name']
                row['BossID'] = department[0]['BossID']
                row['ParentID'] = department[0]['ParentID']

            else:
                row['DepartmentName'] = ''
                row['BossID'] = ''
                row['ParentID'] = ''

            # Сокрытие данных и замена редактированными
            employee_edited_data = list(
                filter(lambda x: x['ID'] == row['ID'], list(filter(lambda y: 'ID' in y, self.edited_data))))
            if employee_edited_data:
                employee_edited_data[0].pop('ID')
                for key, value in sorted(employee_edited_data[0].items(), key=lambda x: 'Hide' not in str(x[1])):
                    if value is True and 'Hide' in key:
                        value = ''
                    elif value is False and 'Hide' in key:
                        continue
                    key = key.replace('Hide', '')
                    row[key] = value

        # Формирование оргструктуры сотрудника
        for row in self.employees:
            if row['DepartmentName']:
                row['OrgStructure'] += self.__fill_organizational_structure(row, self.employees, self.departments)

        # Формирование древовидной структуры департаментов
        self.__organization_tree = list()
        for organization in list(sorted(self.organizations, key=lambda org: org['Order'])):
            child_tree = {
                'ID': organization['ID'],
                'Name': organization['Name'],
                'Filial': -1,
                'Inn': organization['ID'],
                'Children': list(),
            }
            for department in list(filter(lambda dep: dep['Level'] == 1 and dep['OrganizationID'] == organization['ID'], self.departments)):
                child_tree['Children'].append(
                    {
                        'ID': department['ID'],
                        'Name': department['Name'],
                        'Filial': department['Filial'],
                        'Inn': department['OrganizationID'],
                        'Children': self.__fill_department_children(department, self.departments),
                    }
                )
            self.__organization_tree.append(child_tree)

    def get_dep_org_info(self, organization: int, department: str) -> dict:
        """
        Получение имени компании и департамента
        :param organization: ID (ИНН) организации
        :param department: ID департамента
        :return: dict с ID и NAME организации и департамента
        """
        dep_org_info = {
            'department': {
                'ID': str(),
                'Name': str(),
            },
            'organization': {
                'ID': int(),
                'Name': str()
            }
        }
        if organization:
            organization_info = list(filter(lambda org: org['ID'] == organization, self.organizations))[0]
            dep_org_info['organization']['ID'] = organization_info['ID']
            dep_org_info['organization']['Name'] = organization_info['Name']
        if department:
            department_info = list(filter(lambda dep: dep['ID'] == department, self.departments))[0]
            dep_org_info['department']['ID'] = department_info['ID']
            dep_org_info['department']['Name'] = department_info['Name']
        return dep_org_info

    @property
    def organization_tree(self) -> list:
        return self.__organization_tree


if __name__ == '__main__':
    test = DataBaseStorage()
