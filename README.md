# INFORMATICS SOFT
### Веб-сайт для МОАУ "Лицей №2" <br>г. Оренбурга
__Разработчик: Перов Евгений Дмитриевич*__
____
## Запуск сервера
__1. Клонируйте данный репозиторий__
```
git clone https://github.com/aeonva1ues/InformaticsSoft.git
```
__2. Создайте и активируйте виртуальное окружение__
```
python -m venv venv
.\venv\Scripts\activate
```
__3. Установите все необходимые зависимости__
```
pip install -r requirements.txt
```
__4. Секретные данные не располагаются в репозитории. Вам необходимо создать файл с названием .env в папке проекта на одном уровне с manage.py. В данном файле укажите значения SECRET_KEY, ALLOWED_HOSTS, DEBUG по образцу ниже. Если разрешенных хостов несколько, значения писать через пробел.__
```py
SECRET_KEY = writeyoursecretkeyhere
DEBUG = writetrueorfalse
ALLOWED_HOSTS = address0 address1 addrres2 addressN
```
__5. Запуск__
```
cd infromaticssoft
python manage.py runserver
```