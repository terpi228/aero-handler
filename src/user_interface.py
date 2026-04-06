# функция user_interaction()
from src.opensky_api import OpenSkyAPI
from src.json_storage import JSONSaver


def user_menu():
    name_cuntry = input(str("введите название страны:"))
    api = OpenSkyAPI()
    saver = JSONSaver()
    data = api.get_aircraft_by_country(name_cuntry)
    saved_path = saver.save_snapshot(name_cuntry, data)

    print(
        f"получено {data['count']} самолетов из странны {name_cuntry}. "
        f"Данные автоматически сохранены: {saved_path}"
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
