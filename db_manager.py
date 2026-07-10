# db_manager.py
from database import Database

class DBManager:
    """
    Класс для выполнения аналитических запросов к БД.
    """

    def __init__(self):
        self.db = Database()

    def get_countries_and_aeroplanes_count(self):
        """
        Возвращает список всех стран и количество самолётов,
        наблюдавшихся в их воздушном пространстве.
        """
        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(a.id) as count
                FROM countries c
                LEFT JOIN aircraft a ON c.id = a.country_id
                GROUP BY c.id, c.name
                ORDER BY count DESC;
            """)
            return cur.fetchall()

    def get_all_aeroplanes(self):
        """
        Возвращает список всех воздушных судов с информацией о стране,
        где они были зафиксированы.
        """
        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT a.icao24, a.callsign, a.origin_country, a.altitude, a.velocity, c.name as country
                FROM aircraft a
                JOIN countries c ON a.country_id = c.id;
            """)
            return cur.fetchall()

    def get_avg_speed(self):
        """
        Возвращает среднюю скорость всех самолётов.
        """
        with self.db.conn.cursor() as cur:
            cur.execute("SELECT AVG(velocity) FROM aircraft WHERE velocity IS NOT NULL;")
            return cur.fetchone()[0]

    def get_aeroplanes_with_higher_speed(self):
        """
        Возвращает список самолётов, у которых скорость выше средней.
        """
        avg = self.get_avg_speed()
        if avg is None:
            return []
        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT icao24, callsign, origin_country, altitude, velocity, country_id
                FROM aircraft
                WHERE velocity > %s;
            """, (avg,))
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword):
        """
        Возвращает список самолётов, в позывном которых содержится переданная подстрока.
        Поиск регистронезависимый (ILIKE).
        """
        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT icao24, callsign, origin_country, altitude, velocity, country_id
                FROM aircraft
                WHERE callsign ILIKE %s;
            """, (f'%{keyword}%',))
            return cur.fetchall()