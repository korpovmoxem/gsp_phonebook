# Телефонный справочник АО "Газстройпром"

Телефонный справочник позволяет осуществлять поиск по компаниям, отделам, сотрудникам и по персональным атрибутам (телефон, email, адрес и тд.)
Источником данных выступает "ЕИБД" - БД Microsoft SQL Server.
Справочник состоит из двух частей - публичная и административная.


## Публичная часть
Публичная часть состоит из нескольких блоков:
- Хедер
- Поиск
- Древо компаний и департаментов
- Результаты поиска в виде таблиц
- Футер

### Хедер
![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/c44c0165-a5bc-4673-bf3b-8a5953cc0b30)

В хедере расположены следующие интерактивные элементы:
* Логотип компании с ссылкой на интранет
* Вход в административную часть ![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/5ac1ef13-d63c-4b5f-b94e-01b2535d0585)
* Отключение анимации хедера ![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/ffe9d8d0-5011-4e78-8e9d-99f7602bb224)
* Переключение светлой и темной темы ![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/ababcf92-2d59-453c-aa9b-f46ff8edc73a)

### Поиск
![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/be8b4835-dab9-4ed7-bb49-fc629742c33f)

Поиск существляется по всем параметрам атрибутам сотрудника. При вводе строки будут найдены все сотрудники, у которых введеная строка содержится минимум один раз в каком-либо атрибуте.<br>
Кнопка ![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/6a370a16-47aa-457c-aaa7-7cf60b2f6a1e) копирует email всех отображенных на странице сотрудников.<br>
Если был выбран отдел или компания, то поиск будет осуществляться по выбранной структуре. Для сброса выбранной сотруктуры необходимо нажать на кнопку "Сбросить поиск"

### Древо компаний и департаментов
![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/539afd96-b773-42c7-a7f4-b4b5a4862ad0)

При нажатии на компанию будет осуществлен поиск сотрудников по выбранной компании<br>
Каждая компания является раскрывающимся списком, элементами которого являются департаменты и их дочерние элементы<br>
При нажатии на департамент будет осуществлен поиск по выбранной компании и по родительским элементам не включая саму компанию<br>
Кнопка "Свернуть" сворачивает все раскрытые списки<br>

### Результаты поиска в виде таблиц
Результаты поиска делятся до 100 записей на каждой странице<br>
При текстовом поиске отобразятся все подходящие под запрос сотрудники в одной таблице ![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/a3c68079-0ea7-4d6c-a18b-906f74e7fd76)<br>
При поиске по департаменту будут отображены несколько таблиц - одна на департамент ![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/6979502d-417e-41fe-b3e0-2bf427591ea9)<br>
При поиске по компании будет отображена одна таблица ![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/7dcf3471-d399-4b56-916a-8a29428aafe2)<br>
При нажатии на строку с сотрудником в таблице будет открыта карточка с подробной информацией и оргструктурой сотрудника<br>![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/76b8115b-020e-4cee-b664-8e01c7b84cc3)<br>
Нажатие в карточке сотрудника по компании, отделу или по отделу в оргуструктуре осуществит поиск по соответствующему значению


### Футер
В футере расположена нумерация страниц. При нажатии на номер страниц в результатах поиска отобразится соответствующая странице информация<br>
![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/c2f76a17-f1d1-42b5-a647-16e470b864d7)

## Административная часть

### Авторизация
Для входа в административную часть справочника необходимо пройти авторизацию используя логин и пароль от короткой четкой записи ActiveDirectory на домене gsprom<br>
![image](https://github.com/korpovmoxem/gsp_phonebook/assets/105490028/94693143-efae-42d0-9cd8-dc4f62541d66)<br>

### Панель администратора/модератора
Для соответствующих прав учетной записи будет открыта одна из страниц: модератора или администратора<br>




