# infotecs

https://github.com/Rainbowsf/infotecs

*В файле реализованы все 5 заданий (3 основных и 2 дополнительных)

*Весь вывод реализован через html таблички по данным Url, Однако есть возможнось откомментить и нормальный вывод через таблички Pandas

*Серверная часть реализована на flask

*В файлике есть класс для хранения географических обьектов, и 4 метода:
  1. find_by_id(geo_name_id) 
      
      Ищет географический обьект по предоставленному geo_name_id(string)
      
      Пример: http://127.0.0.1:8000/find_by_id/524894
  
  2. open_page(page_num, objects_on_page)
      
      Отрисовывает страницу номер page_num(int) на которой находится objects_on_page(int) географических обьектов
      
      Пример:http://127.0.0.1:8000/open_page/2/5
     
  3. objects_comparison(first_object_name, second_object_name) принимает названия обьектов на всех языках.
      
      Выводит табличку с информаицей о 2х указаных обьектах, какой обьект находится северней, а также разницу между часовыми поясами
      
      Возможный расчет часовых поясов при разных датах в обьектах вроде учтен
      
      Пример: http://127.0.0.1:8000/objects_comparison/Москва/Санкт-Петербург
      
      Пример (с разными поясами): http://127.0.0.1:8000/objects_comparison/Москва/Владивосток
     
  4. continue_name(name) 
      
      Ищет возможные продолжения названия name(string), Возвращает полный список возможных названий
      
      Пример: http://127.0.0.1:8000/continue_name/Ижевск

*Во всех случаях вывода избегаю вывод альтернативных названий потому что это зачастую занимает много места, а также из за арабских названий ломается структура таблички

*Если что то пойдет не так в Файле test.py есть те же самые методы в обычной обработке с нормальным выводом

Как использовать:
  1. pip install -r req.txt
  2. python script.py
  3. переходим на 127.0.0.1:8000/<Наазвание метода>/<Аргумент 1>/<Аргумент 2(Если есть)>
