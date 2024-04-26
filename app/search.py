from copy import deepcopy


class SearchEngine:
    """
    Методы поиска по массиву из БД
    """

    def __init__(self):
        self.employees = list()
        self.departments = list()
        self.filtered_data = list()
        self.child_departments_data = list()

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
        if page == 1:
            return self.filtered_data[:101]
        else:

            return self.filtered_data[int(str(page - 1) + '01'):int(str(page) + '01')]

    def __get_child_department_employees(self, department_id: str, organization_id: int, org_tree_name=None) -> list:
        """
        Рекурсивный поиск сотрудников дочерних подразделений
        """
        child_employees = list()
        child_departments = list(filter(lambda x: x['ParentID'] == department_id and x['OrganizationID'] == organization_id, self.departments))
        department_info = list(filter(lambda x: x['ID'] == department_id and x['OrganizationID'] == organization_id, self.departments))[0]
        temp = list(filter(lambda x: x['DepartmentID'] == department_id and x['OrganizationID'] == organization_id, self.employees))
        org_tree_name += (department_info['Name'], )
        if temp:
            temp[0]['org_tree_name'] = ' / '.join(org_tree_name[::-1])
            child_employees.append(temp)
        for child in child_departments:
            child_employees += self.__get_child_department_employees(child['ID'], child['OrganizationID'], org_tree_name)
        return child_employees

    def search(self, search_text: str = '', department: str = '', organization: int | str = '', page: int = 0) -> list:
        """
        Поиск по всему массиву
        :param search_text: Строка из поля поиска
        :param department: ID отдела
        :param organization: ID компании
        :param page: Номер страницы справочника
        :return: Отфильтрованный массив по указанным параметрам
        """

        self.filtered_data = deepcopy(self.employees)

        if not search_text and not department and not organization:
            return [self.get_page_data(page)]

        self.child_departments_data = list()

        if organization:
            self.filtered_data = list(filter(lambda item: item['OrganizationID'] == organization, self.filtered_data))

        if department and department != organization:
            self.filtered_data = list(filter(lambda item: item['DepartmentID'] == department, self.filtered_data))

            # Поиск сотрудников дочерних подразделений
            child_departments = list(filter(lambda x: x['ParentID'] == department and x['OrganizationID'] == organization, self.departments))
            department_info = list(filter(lambda x: x['ID'] == department and x['OrganizationID'] == organization, self.departments))[0]
            for child in child_departments:
                self.child_departments_data += self.__get_child_department_employees(child['ID'], organization, (department_info['Name'], ))

        if search_text and self.filtered_data:
            temp_data = list()
            for key in self.filtered_data[0].keys():
                if key in ['org_tree_name', 'OrgStructure', 'HideEmail', 'HideTelephoneNumberCorp',
                           'HideMobileNumberCorp', 'HideExtNumID', 'HideWorkPlace',
                           'HidePhotoID', 'HideAddress', 'EditedBy', 'EditedDate']:
                    continue
                temp_data += list(filter(lambda item: search_text.lower() in str(item[key]).lower() and item not in temp_data, self.filtered_data))
            self.filtered_data = temp_data

        if search_text and not self.filtered_data:
            return [self.filtered_data]

        if self.filtered_data:
            self.filtered_data[0]['org_tree_name'] = self.filtered_data[0]['DepartmentName']
        if self.child_departments_data and self.filtered_data:
            return [self.filtered_data] + self.child_departments_data
        elif self.child_departments_data:
            return self.child_departments_data

        return [self.get_page_data(page)]


