import pandas as pd
import datetime
import pytz

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
        """
        locality_str = ''
        for i in range(0, 19):
            locality_str += tags[i] + ': ' + self.info[i] + '\n'
        return locality_str
        """
        table = pd.DataFrame([self.info], columns=tags)
        return table.to_string(index=False)


def find_by_id(geo_name_id):
    """
        Функция поиска обьекта по его geonameid
    """
    current_object = None

    with open('RU.txt', 'r') as file:
        for line in file:
            if line.split()[0] == str(geo_name_id):                     # Ищем по geonameid
                current_object = Locality(line)
                break

    if current_object is None:
        return 'Обьектов с таким geonameid не найдено!'                 # Если не нашли говорим что нет такого!
    else:
        return 'Информация об обьекте:' + '\n' + str(current_object)    # Если нашли - выводим карточку


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
                page_data.append(line.split('	'))
                page_line += 1
                if page_line == objects_on_page + 1:
                    break

        page_table = pd.DataFrame(page_data, columns=tags)          # Засовываем все в Pandas, чтобы было красиво
        page_table = page_table.drop('Альтернативные названия', 1)
        return page_table.to_string(index=False)                    # возвращаем Pandas табличку содержащей страничку


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
              northern_object = second_object
        else:
              northern_object = first_object

        if second_object.timezone == first_object.timezone:                 # Сравниваем временные зоны
            timezone_info = 'Оба обьекта находятся в одной временной зоне'

        elif datetime.datetime.now(pytz.timezone(second_object.timezone)).day > \
                datetime.datetime.now(pytz.timezone(first_object.timezone)).day:
            timezone_difference = 24 + datetime.datetime.now(pytz.timezone(second_object.timezone)).hour - \
                                  datetime.datetime.now(pytz.timezone(first_object.timezone)).hour
            timezone_info = 'разница между временными зонами(часов): {}'.format(abs(timezone_difference))

        elif datetime.datetime.now(pytz.timezone(second_object.timezone)).day < \
                datetime.datetime.now(pytz.timezone(first_object.timezone)).day:
            timezone_difference = 24 - datetime.datetime.now(pytz.timezone(second_object.timezone)).hour + \
                                  datetime.datetime.now(pytz.timezone(first_object.timezone)).hour
            timezone_info = 'разница между временными зонами(часов): {}'.format(abs(timezone_difference))

        else:
            timezone_difference = datetime.datetime.now(pytz.timezone(second_object.timezone)).hour - \
                                  datetime.datetime.now(pytz.timezone(first_object.timezone)).hour
            timezone_info = 'разница между временными зонами(часов): {}'.format(abs(timezone_difference))

        objects_table = pd.DataFrame([first_object.info, second_object.info], columns=tags)
        objects_table = objects_table.drop('Альтернативные названия', 1)    # убрал альтернативныее названия тк из-за
                                                                            # арабского и китайского языков все ехало
        return objects_table.to_string(index=False) + '\n'\
               + 'Находится севернее: ' + northern_object.name + '\n' + timezone_info


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
        output_list = 'Возможные обьекты: \n'
    for el in find_list:
        output_list += str(el) + ', '
    return output_list
