# функция user_interaction()
from src.opensky_api import OpenSkyAPI


def user_menu():
    name_cuntry = input(str("введите название страны:"))
    api = OpenSkyAPI()
    data = api.get_aircraft_by_country(name_cuntry)

    print(
        f"получено {data['count']} самолетов из странны {name_cuntry} данные будут сохронятся в дальнейшей версии"
    )
    print("--------------menu--------------")
    print("""1. Топ N по высоте
2. Самолёты по стране регистрации
3. Фильтр по диапазону высот
4. Выход
Выберите действие
""")

    users_input = input("Введите действие:")
    if users_input == "1":
        print("выбран №1")
    elif users_input == "2":
        print("выбран №2")
    elif users_input == "3":
        print("выбран №3")
    elif users_input == "4":
        print("выбран №4")
