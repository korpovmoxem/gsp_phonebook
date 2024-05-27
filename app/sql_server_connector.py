from datetime import datetime
import os
import base64

import pyodbc
import yaml
from yaml.loader import SafeLoader
import openpyxl

from search import SearchEngine


class SqlServerConnector:
    """
    Подключение к БД Microsoft Sql-Server
    """

    def __init__(self):
        with open('configs.yaml', 'r') as file:
            sql_server_config = yaml.load(file, Loader=SafeLoader)['SQL']

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
        self.__table_fields = dict()

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

    def __get_column_names(self) -> list:
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

    def update_data(self, data: dict, table_name: str = 'EditedEmployees') -> dict:
        """
        Обновляет данные в таблицах, в зависимости от ключа в словаре
        :param data: Словарь, в котором ключ - название атрибута таблицы в БД, значение - новое значение атрибута
        :param table_name: Название таблицы
        :return: Преобразованные данные для запроса в БД
        """
        if table_name == 'Positions':
            query = f"SELECT [PositionID] FROM {self.__db_name}.Employees WHERE ID='{data['ID']}'"
            entry = self.__execute_query(query)
            position_id = entry[0][0]
            query = f"UPDATE {self.__db_name}.{table_name} SET [Order]={data['Order']} WHERE ID='{position_id}'"
            self.__execute_query(query)

        elif table_name == 'EditedEmployees':
            query = f"SELECT * FROM {self.__db_name}.{table_name} WHERE ID = '{data['ID']}'"
            entry = self.__execute_query(query)
            hide_columns = filter(lambda x: 'Hide' in x, self.__get_column_names())
            for column in hide_columns:
                if column in data:
                    data[column] = 1
                else:
                    data[column] = 0

            data = dict(map(lambda x: (f"[{x[0]}]",f"'{x[1]}'" if x[1] else 'NULL'), data.items()))
            data = dict(map(lambda x: (x[0], int(x[1].strip("'")) if x[1].strip("'").isdigit() else x[1]), data.items()))
            if entry:
                employee_id = data.pop('[ID]')
                query = f"UPDATE {self.__db_name}.{table_name} SET {','.join([f'{i[0]}={i[1]}' for i in data.items()])} WHERE ID = {employee_id}"
            else:
                query = f"INSERT INTO {self.__db_name}.{table_name} ({','.join(data.keys())}) VALUES ({','.join(map(str, data.values()))})"

            self.__execute_query(query)
            return data

    def update_positions(self, row_data: dict):
        self.__execute_query(f"UPDATE {self.__db_name}.Positions SET [Order]={row_data['Order']} WHERE [ID] = '{row_data["ID"]}'")

    def change_department_order(self, department: str, department_order: int):
        query = f"UPDATE {self.__db_name}.Departments SET [Order]={department_order} WHERE [ID]='{department}'"
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
            if employee['ID'] != employee['ManagerID']:
                boss_info = list(filter(lambda boss: boss['ID'] == employee['ManagerID'], employee_list))
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

    def __create_organization_tree(self):
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

    def create_positions_file(self):
        pass

    def __init__(self):
        super().__init__()
        connector = SqlServerConnector()
        self.employees = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.employees")
        self.departments = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.departments ORDER BY [Order], [Name] ASC")
        self.organizations = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.organizations ORDER BY [Order], [Name] ASC")
        self.edited_data = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.EditedEmployees")
        self.positions = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.Positions WHERE Category NOT IN ('Рабочие', 'Служащие')")
        self.categories = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.Categories")

        self.employees = list(filter(lambda x: x['Fired'] != 1 and x['Decret'] != 1 and x['PositionID'] in map(lambda y: y['ID'], self.positions), self.employees))
        with open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}static{os.sep}content{os.sep}no_avatar.jpg', 'rb') as file:
            no_avatar = file.read()

        for row in self.employees:

            # Фото
            photo_name = None
            photo = None
            if row['Email']:
                photo_name = row['Email']
            elif row['FL_ID']:
                photo_name = row['FL_ID']

            if photo_name:
                if os.path.isdir("/mnt/phonebook_photo/") and f"{photo_name}.jpg" in os.listdir('/mnt/phonebook_photo/'):
                    with open(f"/mnt/phonebook_photo/{photo_name}.jpg", 'rb') as file:
                        photo = file.read()
            if not photo:
                photo = no_avatar

            row['Photo'] = base64.b64encode(photo).decode("utf-8")

            # Дополнение массива названием департамента и компании
            row['OrgStructure'] = list()
            row['insert_date'] = row['insert_date'].strftime('%d.%m.%Y %H:%M:%S') if isinstance(row['insert_date'], datetime) else row['insert_date']
            row['update_date'] = row['update_date'].strftime('%d.%m.%Y %H:%M:%S') if isinstance(row['update_date'], datetime) else row['update_date']
            category_info = list(filter(lambda x: x['ID'] == row['CategoryID'], self.categories))
            row['CategoryOrder'] = category_info[0]['Order'] if category_info and category_info[0]['Order'] else 100
            organization_info = list(filter(lambda org: org['ID'] == row['OrganizationID'], self.organizations))[0]
            row['OrganizationName'] = organization_info['Name']
            position_info = list(filter(lambda x: x['ID'] == row['PositionID'], self.positions))
            row['PositionOrder'] = position_info[0]['Order'] if position_info[0]['Order'] else 20000
            row['OrganizationOrder'] = organization_info['Order'] if organization_info['Order'] else 20000
            department = list(filter(lambda dep: dep['ID'] == row['DepartmentID'] and dep['OrganizationID'] == row['OrganizationID'], self.departments))
            if department:
                row['DepartmentName'] = department[0]['Name']
                row['ManagerID'] = department[0]['ManagerID']
                row['ParentID'] = department[0]['ParentID']

            else:
                row['DepartmentName'] = ''
                row['ManagerID'] = ''
                row['ParentID'] = ''

            # Сокрытие данных и замена редактированными
            employee_edited_data = list(filter(lambda x: x['ID'] == row['ID'], list(filter(lambda y: 'ID' in y, self.edited_data))))
            if employee_edited_data:
                employee_edited_data[0].pop('ID')
                for key, value in employee_edited_data[0].items():
                    if isinstance(value, str):
                        value = value.strip("'") if value != 'NULL' else ''
                    if value:
                        row[key] = value
            else:
                for key in ['HideEmail', 'HideTelephoneNumberCorp', 'HideMobileNumberCorp', 'HideExtNumID',
                            'HideWorkPlace', 'HidePhotoID', 'HideAddress', 'EditedBy', 'EditedDate']:
                    if key not in row:
                        row[key] = 0

        self.employees = sorted(self.employees, key=lambda x: (x['OrganizationOrder'], x['CategoryOrder'], x['PositionOrder'], x['Order'], x['FullNameRus']))

        # Формирование оргструктуры сотрудника
        for row in self.employees:
            if row['DepartmentName']:
                row['OrgStructure'] += self.__fill_organizational_structure(row, self.employees, self.departments)

        # Формирование древовидной структуры департаментов
        self.__create_organization_tree()

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

    def update_edited_data(self, data: dict) -> None:
        """
        Обновляет запись пользователя в массиве хранилища
        :param data: ID пользователя
        """
        connector = SqlServerConnector()
        position_order = data.pop('PositionOrder')
        connector.update_data({'ID': data['ID'], 'Order': position_order}, 'Positions')
        edited_data = connector.update_data(data)
        employee_data = list(filter(lambda x: x['ID'] == data['ID'], self.employees))[0]
        employee_data_index = self.employees.index(employee_data)
        data['PositionOrder'] = position_order
        for key, value in edited_data.items():
            if isinstance(value, str):
                value = value.strip("'") if value != 'NULL' else ''
            employee_data[key.replace('[', '').replace(']', '')] = value
        self.employees[employee_data_index] = employee_data

    @property
    def organization_tree(self) -> list:
        return self.__organization_tree

    def update_department_order(self, data: dict):
        connector = SqlServerConnector()
        connector.change_department_order(data['department'], data['department_order'])
        self.departments = connector.get_formatted_data(f"SELECT * FROM {connector.db_name}.departments ORDER BY [Order], [Name] ASC")
        self.__create_organization_tree()

    def create_position_file(self) -> None:
        filename = f"{os.path.dirname(os.path.realpath(__file__))}{os.sep}static{os.sep}xlsx{os.sep}positions.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['ID', 'Name', 'Category', 'insert_date', 'update_date', 'Order'])
        for row in self.positions:
            sheet.append(list(row.values()))
        workbook.save(filename)

    def update_positions_from_file(self) -> None:
        workbook = openpyxl.load_workbook(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}static{os.sep}xlsx{os.sep}new_positions.xlsx')
        sheet = workbook.active
        row_title = None
        connector = SqlServerConnector()
        for row in sheet:
            row = list(map(lambda cell: cell.value, row))
            if not row_title:
                row_title = row
            else:
                data = dict(zip(row_title, row))
                current_positions = list(filter(lambda x: x['ID'] == data['ID'], self.positions))
                if data['Order'] != current_positions[0]['Order']:
                    print(data)
                    connector.update_positions(data)



