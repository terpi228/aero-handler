# main.py
import logging
from database import Database
from api_client import OpenSkyAPI
from config import COUNTRIES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    db = Database()

        # Сброс таблиц (только для перезаполнения)
    db.cursor.execute("DROP TABLE IF EXISTS aircraft CASCADE;")
    db.cursor.execute("DROP TABLE IF EXISTS countries CASCADE;")
    db.conn.commit()

    db.create_tables()
    api = OpenSkyAPI()

    for country in COUNTRIES:
        logging.info("Processing country: %s", country)
        bbox = api.get_bounding_box(country)
        if not bbox:
            logging.warning("Skipping %s - no bounding box", country)
            continue

        # Вставляем страну и получаем её id
        country_id = db.insert_country(country, bbox["lamin"], bbox["lamax"],
                                       bbox["lomin"], bbox["lomax"])
        states = api.get_aircraft(bbox)

        for state in states:
            # Извлекаем поля согласно документации OpenSky
            icao24 = state[0] if len(state) > 0 else None
            callsign = state[1].strip() if len(state) > 1 and state[1] else None
            origin_country = state[2] if len(state) > 2 else None
            # Высота: предпочитаем geo_altitude (index 13), иначе baro_altitude (index 7)
            geo_alt = state[13] if len(state) > 13 else None
            baro_alt = state[7] if len(state) > 7 else None
            altitude = geo_alt if geo_alt is not None else baro_alt
            velocity = state[9] if len(state) > 9 else None

            # Приводим к float, если возможно
            try:
                altitude = float(altitude) if altitude is not None else None
            except (ValueError, TypeError):
                altitude = None
            try:
                velocity = float(velocity) if velocity is not None else None
            except (ValueError, TypeError):
                velocity = None

            db.insert_aircraft(icao24, callsign, origin_country, altitude, velocity, country_id)

    db.close()
    logging.info("Data population complete. Total countries: %d", len(COUNTRIES))

if __name__ == "__main__":
    main()