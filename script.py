import os
from flask import Flask, jsonify
import pandas as pd
import datetime
import pytz

app = Flask(__name__)

pd.options.display.max_colwidth = 200                       # Настройки для корректного отображения таблички
pd.options.display.max_columns = 20
pd.options.display.max_rows = 999
pd.set_option("expand_frame_repr", True)


tags = ["Идентификатор",                                    # Набор заголовков для таблички и карточки обьекта
        "Название",
        "Название Ascii",
        "Альтернативные названия",
        "Широта",
        "Долгота",
        "Класс обьекта",
        "Код обьекта",
        "Код страны",
        "cc2",
        "admin1code",
        "admin2code",
        "admin3code",
        "admin4code",
        "Население",
        "elevation",
        "dem",
        "Временная зона",
        "Дата изменения",
        ]


class Locality:
    """
        Тут храним обьекты
    """
    def __init__(self, line):
        self.info = line.split('	')                      # Строка с информацией из файлика
        self.id = self.info[0]                              # Geonameid
        self.name = self.info[1]                            # Название пункта на алглийском
        self.alternate_names = self.info[3].split(',')      # Альтернативные названия
        self.latitude = self.info[4]                        # Широта(Для определения кто севернее)
        self.timezone = self.info[len(self.info) - 2]       # Временная зона
        self.population = self.info[len(self.info) - 5]     # Население

    def __str__(self):
        """
            Отображение карточки обьекта
        """
        table = pd.DataFrame([self.info], columns=tags)
        return table.to_string(index=False)


@app.route("/find_by_id/<string:geo_name_id>", methods=['GET'])
def find_by_id(geo_name_id):
    """
        Функция поиска обьекта по его geonameid
    """
    current_object = None

    with open('RU.txt', 'r') as file:
        for line in file:
            if line.split()[0] == str(geo_name_id):                             # Ищем по geonameid
                current_object = Locality(line)
                break

    if current_object is None:
        return 'Обьектов с таким geonameid не найдено!'                       # Если не нашли говорим что нет такого!
    else:

        # Обычный вывод через табличку pandas
        """ 
            return 'Информация об обьекте:' + '\n' + str(current_object) 
        """

        # Вывод через html страничку
        html = '<h1>Информация об обьекте:</h1>' + '<table><thead><tr>'

        for el in tags:                                                         # Заполняем Заголовки
            if el != 'Альтернативные названия' and el != 'admin2code' and el != 'admin3code' and el != 'admin4code'\
                    and el != 'elevation' and el != 'dem':
                html += '<th>' + el + '</th>'
        html += '</tr></thead><tbody>'

        for i in range(len(current_object.info)):                               # Заполняем Основную часть
            if i != 3 and i != 11 and i != 12 and i != 13 and i != 15 and i != 16:
                html += '<td>' + current_object.info[i] + '</td>'
        html += '</tr></tbody></table>'

        return html


@app.route("/open_page/<int:page_num>/<int:objects_on_page>", methods=['GET'])
def open_page(page_num, objects_on_page):
    """
        Вывод странички с обьектами
    """
    with open('RU.txt', 'r') as file:

        if (page_num - 1) * objects_on_page > 363118:               # проверяем есть ли вообще такая страничка
            return 'Такой страницы не существует'

        page_data = []
        is_on_page = False
        page_line = 1

        for index, line in enumerate(file):
            if index == ((page_num - 1) * objects_on_page):         # Нашли начало странички
                is_on_page = True

            if is_on_page:                                          # Запоминаем страничку в список
                page_data.append(Locality(line))
                page_line += 1
                if page_line == objects_on_page + 1:
                    break

        # Обычный вывод через табличку pandas
        """ 
        page_table = pd.DataFrame(page_data, columns=tags)          # Засовываем все в Pandas, чтобы было красиво
        page_table = page_table.drop('Альтернативные названия', 1)
        return page_table.to_string(index=False)                    # возвращаем Pandas табличку содержащей страничку
        """

        # Вывод через html страничку
        html = '<h1>Страница номер: {}, Обьектов на странице: {}</h1>'.format(page_num, objects_on_page) \
                 + '<table><thead><tr>'

        for el in tags:                                             # Заполняем Заголовки
            if el != 'Альтернативные названия' and el != 'admin2code' and el != 'admin3code' and el != 'admin4code'\
                    and el != 'elevation' and el != 'dem':
                html += '<th>' + el + '</th>'
        html += '</tr></thead><tbody>'

        for current_object in page_data:                            # Заполняем Страничку
            for i in range(len(current_object.info)):
                if i != 3 and i != 11 and i != 12 and i != 13 and i != 15 and i != 16:
                    html += '<td>' + current_object.info[i] + '</td>'
            html += '</tr>'
        html += '</tbody></table>'
        return html


@app.route("/objects_comparison/<string:first_object_name>/<string:second_object_name>", methods=['GET'])
def objects_comparison(first_object_name, second_object_name):
    """
        Сравнение 2х обьектов
    """
    with open('RU.txt', 'r') as file:

        first_objects_list = []                                     # Два списка для сравнения одноименцев по населению
        second_objects_list = []

        for line in file:
            current_object = Locality(line)

            for name in current_object.alternate_names:             # Ищем по русским именам и сохраняем в списки
                if name == first_object_name:
                    first_objects_list.append(current_object)
                if name == second_object_name:
                    second_objects_list.append(current_object)

        if len(first_objects_list) == 0:                            # Если список пустой - говорим что ничего не нашли
            return 'Не найден первый обьект'
        elif len(first_objects_list) == 1:                          # Если там кто то один - запоминаем его
            first_object = first_objects_list[0]
        else:                                                       # Иначе смотрим у кого население больше
            first_object = first_objects_list[0]
            for current_object in first_objects_list:
                if int(current_object.population) > int(first_object.population):
                    first_object = current_object

        if len(second_objects_list) == 0:                           # То же самое для второго обьекта
            return 'Не найден второй обьект'
        elif len(second_objects_list) == 1:
            second_object = second_objects_list[0]
        else:
            second_object = second_objects_list[0]
            for current_object in second_objects_list:
                if int(current_object.population) > int(second_object.population):
                    second_object = current_object

        if float(second_object.latitude) > float(first_object.latitude):   # Сравниваем широты и запоминаем кто севернее
              northern_object = second_object_name
        else:
              northern_object = first_object_name

        if second_object.timezone == first_object.timezone:                 # Сравниваем временные зоны
            timezone_info = 'Оба обьекта находятся в одной временной зоне'
        else:                                                               # Если они разные то ищем разницу по времени
            timezone_difference = datetime.datetime.now(pytz.timezone(second_object.timezone)).hour - \
                                  datetime.datetime.now(pytz.timezone(first_object.timezone)).hour
            timezone_info = 'разница между временными зонами(часов): {}'.format(abs(timezone_difference))

        # Обычный вывод через табличку pandas
        """  
        objects_table = pd.DataFrame([first_object.info, second_object.info], columns=tags)
        objects_table = objects_table.drop('Альтернативные названия', 1) 
        return objects_table.to_string(index=False) + '\n' \
               + 'Находится севернее: ' + northern_object + '\n' \
               + timezone_info
        """

        # Вывод через html таблицу
        html = 'Информация обб обьектах: {} и {}'.format(first_object_name, second_object_name) \
                 + '<table><thead><tr>'

        for el in tags:                                                                 # Заполняем Заголовки
            if el != 'Альтернативные названия' and el != 'admin2code' and el != 'admin3code' and el != 'admin4code' \
                    and el != 'elevation' and el != 'dem':
                html += '<th>' + el + '</th>'
        html += '</tr></thead><tbody>'

        for i in range(len(first_object.info)):                                         # Заполняем 1 обьект
            if i != 3 and i != 11 and i != 12 and i != 13 and i != 15 and i != 16:
                html += '<td>' + first_object.info[i] + '</td>'
        html += '</tr><tr>'

        for i in range(len(second_object.info)):                                        # Заполняем 2 обьект
            if i != 3 and i != 11 and i != 12 and i != 13 and i != 15 and i != 16:
                html += '<td>' + second_object.info[i] + '</td>'

        html += '</tbody></table><BR><H1>Находится Севернее: {}</H1><H1>{}</H1>'.format(northern_object, timezone_info)

        return html


@app.route("/continue_name/<string:name>", methods=['GET'])
def continue_name(name):
    """
        Ищем продолжения введенной строки в файлике
    """
    with open('RU.txt', 'r') as file:
        find_list = []
        for line in file:
            current_object = Locality(line)
            if current_object.name.find(name) != -1:                    # Поиск подстроки в основном имени
                find_list.append(current_object.name)
            else:
                for alternate_name in current_object.alternate_names:   # Поиск подстроки в альтернативных именах
                    if alternate_name.find(name) != -1:
                        find_list.append(alternate_name)                # Все что нашли складываем в список
                        break

        # Обычный вывод
        """
        output_list = 'Возможные обьекты: \n'
        for el in find_list:
            output_list += str(el) + ', '
        return output_list
        """

        # Вывод html
        html = 'Возможные обьекты: <BR>'

        for el in find_list:
            html += str(el) + '<BR>'

        return html


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
