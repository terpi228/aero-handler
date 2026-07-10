# check_db.py
from db_manager import DBManager

if __name__ == "__main__":
    dm = DBManager()
    
    print("=== Страны и количество самолётов ===")
    for row in dm.get_countries_and_aeroplanes_count():
        print(row)
    
    print("\n=== Первые 5 самолётов ===")
    for row in dm.get_all_aeroplanes()[:5]:
        print(row)
    
    print("\n=== Средняя скорость ===")
    print(dm.get_avg_speed())
    
    print("\n=== Самолёты со скоростью выше средней (первые 5) ===")
    for row in dm.get_aeroplanes_with_higher_speed()[:5]:
        print(row)
    
    print("\n=== Самолёты с позывным, содержащим 'AIR' ===")
    for row in dm.get_aeroplanes_with_keyword("AIR"):
        print(row)
    
    dm.db.close()