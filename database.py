# database.py
import psycopg2
from psycopg2 import sql
from config import DB_CONFIG

class Database:
    """
    Класс для подключения к PostgreSQL и выполнения базовых операций.
    """

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Устанавливает соединение с БД."""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def close(self):
        """Закрывает соединение и курсор."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """
        Создаёт таблицы countries и aircraft, если они не существуют.
        Для aircraft добавлен уникальный индекс (icao24, country_id),
        чтобы избежать дублирования для одной страны.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                lamin FLOAT,
                lamax FLOAT,
                lomin FLOAT,
                lomax FLOAT
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS aircraft (
                id SERIAL PRIMARY KEY,
                icao24 VARCHAR(10) NOT NULL,
                callsign VARCHAR(20),
                origin_country VARCHAR(100),
                altitude FLOAT,
                velocity FLOAT,
                country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
                UNIQUE(icao24, country_id)
            );
        """)
        self.conn.commit()

    def insert_country(self, name, lamin, lamax, lomin, lomax):
        """
        Вставляет страну или обновляет её координаты.
        Возвращает id страны.
        """
        self.cursor.execute("""
            INSERT INTO countries (name, lamin, lamax, lomin, lomax)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET lamin = EXCLUDED.lamin,
                lamax = EXCLUDED.lamax,
                lomin = EXCLUDED.lomin,
                lomax = EXCLUDED.lomax
            RETURNING id;
        """, (name, lamin, lamax, lomin, lomax))
        return self.cursor.fetchone()[0]

    def insert_aircraft(self, icao24, callsign, origin_country, altitude, velocity, country_id):
        """
        Вставляет самолёт или обновляет его данные при конфликте.
        """
        self.cursor.execute("""
            INSERT INTO aircraft (icao24, callsign, origin_country, altitude, velocity, country_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (icao24, country_id) DO UPDATE
            SET callsign = EXCLUDED.callsign,
                origin_country = EXCLUDED.origin_country,
                altitude = EXCLUDED.altitude,
                velocity = EXCLUDED.velocity;
        """, (icao24, callsign, origin_country, altitude, velocity, country_id))
        self.conn.commit()