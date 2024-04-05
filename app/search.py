class SearchEngine:
    """
    Методы поиска по массиву из БД
    """

    def __init__(self):
        self.employees = list()
        self.departments = list()
        self.filtered_data = list()
        self.parent_departments_data = list()

    def get_pages_count(self) -> list:
        """
        Подсчет количества страниц на основе количества элементов в массиве
        :return: Массив с количеством страниц
        """
        count = len(self.filtered_data) // 100
        if len(self.filtered_data) % 100 != 0:
            count += 1
        return list(range(1, count + 1))

    def get_page_data(self, page: int) -> list:
        """
        Возвращает массив данных справочника в разрезе указанной страницы
        :param page: Номер страницы
        :return:
        """
        if page == 0:
            return self.filtered_data[:101]
        else:
            return self.filtered_data[int(str(page) + '01'):int(str(page + 1) + '01')]

    def search(self, search_text: str = '', department: str = '', organization: int | str = '', page: int = 0) -> list:
        """
        Поиск по всему массиву
        :param search_text: Строка из поля поиска
        :param department: ID отдела
        :param organization: ID компании
        :param page: Номер страницы справочника
        :return: Отфильтрованный массив по указанным параметрам
        """
        self.filtered_data = self.employees
        self.parent_departments_data = list()

        if organization:
            self.filtered_data = list(filter(lambda item: item['OrganizationID'] == organization, self.filtered_data))

        if department and department != organization:
            self.filtered_data = list(filter(lambda item: item['DepartmentID'] == department, self.filtered_data))

            # Поиск сотрудников родительских подразделений
            department_info = list(filter(lambda x: x['ID'] == department, self.departments))[0]
            while department_info['ParentID'] != '00000000-0000-0000-0000-000000000000':
                print(department_info['ID'], department_info['ParentID'])
                department_info = list(filter(lambda x: x['ID'] == department_info['ParentID'] and department_info['OrganizationID'] == x['OrganizationID'], self.departments))
                if not department_info:
                    break
                department_info = department_info[0]
                employees = list(filter(lambda x: x['OrganizationID'] == department_info['OrganizationID'] and x['DepartmentID'] == department_info['ID'], self.employees))
                if employees:
                    self.parent_departments_data.append(employees)

        if search_text:
            temp_data = list()
            for key in self.filtered_data[0].keys():
                temp_data += list(filter(lambda item: search_text.lower() in str(item[key]).lower() and item not in temp_data, self.filtered_data))
            self.filtered_data = temp_data

        if self.parent_departments_data and self.filtered_data:
            return [self.filtered_data] + self.parent_departments_data

        return [self.get_page_data(page)]


