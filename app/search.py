class SearchEngine:
    """
    Методы поиска по массиву из БД
    """

    def __init__(self):
        self.employees = list()
        self.filtered_data = list()

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

    def search(self, search_text: str = '', department: str = '', organization: int = '', page: int = 0) -> list:
        """
        Поиск по всему массиву
        :param search_text: Строка из поля поиска
        :param department: ID отдела
        :param organization: ID компании
        :param page: Номер страницы справочника
        :return: Отфильтрованный массив по указанным параметрам
        """
        self.filtered_data = self.employees

        if organization:
            self.filtered_data = list(filter(lambda item: item['OrganizationID'] == organization, self.filtered_data))

        if department and department != organization:
            self.filtered_data = list(filter(lambda item: item['DepartmentID'] == department, self.filtered_data))

        if search_text:
            temp_data = list()
            for key in self.filtered_data[0].keys():
                temp_data += list(filter(lambda item: search_text.lower() in str(item[key]).lower() and item not in temp_data, self.filtered_data))
            self.filtered_data = temp_data
        return self.get_page_data(page)


