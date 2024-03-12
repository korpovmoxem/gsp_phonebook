import json

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

        sql_connector = pyodbc.connect(
            f'DRIVER={sql_server_config["DRIVER"]};'
            f'SERVER={sql_server_config["SERVER"]};'
            f'UID={sql_server_config["UID"]};'
            f'PWD={sql_server_config["PWD"]};'
            f'Trusted_Connection=No;'
            f'Database={sql_server_config["Database"]};'
        )
        self.db_name = f'{sql_server_config["Database"]}.dbo'
        self.cursor = sql_connector.cursor()

    def execute_query(self, query: str) -> list:
        """
        Выполняет запрос и возвращает массив типа list
        :param query: строка с SQL запросом
        :return: Данные, полученные запросом в БД
        """
        return self.cursor.execute(query).fetchall()

    def get_column_names(self):
        """
        Получает наименования колонок в таблице БД, к которой последний раз отправлялся запрос
        :return:
        """
        return [i[0] for i in self.cursor.description]

    def get_formatted_data(self, query: str) -> list:
        """
        Возвращает данные, полученные SQL запросом в формате dict, где ключ - название столбца из таблицы
        :param query: строка с SQL запросом
        :return: Список, в котором каждый элемент - строка таблицы в формате dict
        """
        raw_data = self.execute_query(query)
        for i in range(len(raw_data)):
            raw_data[i] = list(map(lambda x: '' if not x else x, raw_data[i]))
        data_fields = self.get_column_names()
        return list(map(lambda x: dict(zip(data_fields, x)), raw_data))


class DataBaseStorage(SearchEngine):
    """
    Хранилище всех данных из БД
    """

    def fill_department_children(self, department: dict, departments_list: list) -> list:
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
                        'Children': self.fill_department_children(child, departments_list),
                    }
                )
        return current_tree

    def __init__(self):
        super().__init__()
        connector = SqlServerConnector()
        self.employees = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.employees")
        self.departments = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.departments")
        self.organizations = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.organizations")

        # Дополнение массива названием департамента и компании
        for row in self.employees:
            row['OrganizationName'] = list(filter(lambda organization: organization['ID'] == row['OrganizationID'], self.organizations))[0]['Name']
            department_name = list(filter(lambda department: department['ID'] == row['DepartmentID'] and department['OrganizationID'] == row['OrganizationID'], self.departments))
            if department_name:
                row['DepartmentName'] = department_name[0]['Name']
            else:
                row['DepartmentName'] = ''
                print(row)

        # Формирование древовидной структуры департаментов
        self.organization_tree = list()
        for organization in list(sorted(self.organizations, key=lambda org: org['order'])):
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
                        'Children': self.fill_department_children(department, self.departments),
                    }
                )
            self.organization_tree.append(child_tree)
        with open('templates/organization_tree.json', 'w', encoding='utf-8') as file:
            json.dump(self.organization_tree, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    test = DataBaseStorage()
