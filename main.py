from datetime import datetime as dt, timedelta
import tkinter as tk
import requests
import json
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


URL_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
URL_MEASURE_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/"
URL_MEASURE_DATA = "https://api.gios.gov.pl/pjp-api/rest/data/getData/"
URL_AIR_QUALITY_INDEX = "https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/"


DATABASE_FILE = "air_quality.db"

def create_table():
    """
        Tworzy tabelę w bazie danych o nazwie 'measurement_data'.
        Tabela zawiera kolumny: station_id (INTEGER), sensor_id (INTEGER), date (TEXT), value (REAL).
        """
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS measurement_data
                 (station_id INTEGER, sensor_id INTEGER, date TEXT, value REAL)''')

    conn.commit()
    conn.close()

create_table()

stop_flag = False  # Flaga do zatrzymania pobierania danych

def download_data(url, id="-1"):
    """
       Pobiera dane z podanego URL.
       Parametry:
           - url (str): Adres URL do pobrania danych.
           - id (str, opcjonalny): ID stacji/sensora. Domyślnie "-1".
       Zwraca:
           - response (Response): Obiekt odpowiedzi HTTP.
       """
    global stop_flag  # Dodano globalną flagę zatrzymania pobierania danych
    headers = {'User-Agent': 'Mozilla/5.0'}
    timeout = 2000  # Ustaw w sekundach

    if id == "-1":
        response = requests.get(url, headers=headers, timeout=timeout)
    else:
        response = requests.get(f'{url}{id}', headers=headers, timeout=timeout)

    if response.ok:
        print(f'Kod odpowiedzi: {response.status_code}')
        return response
    else:
        print(f'Błąd pobierania danych: {response.status_code}')
        stop_flag = True  # Ustawienie flagi na True w przypadku błędu
        exit()

def generate_station_map():
    """
        Generuje mapę lokalizacji stacji pomiarowych.
        Wykorzystuje moduł Basemap z biblioteki matplotlib.
        """
    all_station_data = download_data(URL_STATION)
    all_station = conv_data_to_json(all_station_data)

    lats = []
    lons = []
    for station in all_station:
        lats.append(float(station['gegrLat']))
        lons.append(float(station['gegrLon']))

    # Tworzenie mapy
    fig = plt.figure(figsize=(12, 10))
    m = Basemap(projection='lcc', resolution='l', lat_0=52, lon_0=19,
                width=2E6, height=1.4E6)
    m.shadedrelief()
    m.drawcoastlines(color='gray')
    m.drawcountries(color='gray')
    m.drawstates(color='gray')

    # Rysowanie lokalizacji stacji
    x, y = m(lons, lats)
    m.scatter(x, y, s=50, color='red', edgecolor='black')


    plt.title('Mapa lokalizacji stacji pomiarowych')
    plt.show()


def conv_data_to_json(response):
    """
        Konwertuje dane z formatu JSON na słownik.
        Parametry:
            - response (Response): Obiekt odpowiedzi HTTP.
        Zwraca:
            - data_dict (dict): Słownik zawierający przekonwertowane dane.
        """
    try:
        data = response.json()
        return data
    except json.decoder.JSONDecodeError:
        print('Niepoprawny format danych JSON')
        return None


def get_measurement_data():
    def generate_station_list():
        """
            Generuje listę stacji, pobiera ich dane i wypisuje ich identyfikatory oraz lokalizacje.

            Zwraca:
                None
            """
        global stop_flag  # Dodano globalną flagę zatrzymania pobierania danych
        all_station_data = download_data(URL_STATION)
        all_station = conv_data_to_json(all_station_data)
        print("Lista ID stacji:")
        for station in all_station:
            station_coords = (station['gegrLat'], station['gegrLon'])
            station_location = get_location_from_coordinates(station_coords)
            print(f"ID: {station['id']}, Lokalizacja: {station_location}")
            if stop_flag:
                break

    def get_location_from_coordinates(coords):
        """
            Pobiera lokalizację na podstawie współrzędnych geograficznych.

            Args:
                coords (tuple): Tuple zawierający współrzędne (latitude, longitude).

            Returns:
                str: Lokalizacja na podstawie współrzędnych geograficznych.
                     Jeśli lokalizacja jest znana, zwraca adres.
                     W przeciwnym razie zwraca "Nieznana lokalizacja".
            """
        geolocator = Nominatim(user_agent="air_quality_app")
        location_data = geolocator.reverse(coords)
        if location_data:
            return location_data.address
        else:
            return "Nieznana lokalizacja"

    def get_sensor_list():
        """
            Pobiera listę czujników dla określonej stacji i wypisuje ich identyfikatory oraz nazwy parametrów.

            Zwraca:
                None
            """
        station_id = station_entry.get()
        url = f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}"
        sensor_data = download_data(url)
        sensors = conv_data_to_json(sensor_data)

        if sensors:
            print("Lista sensorów:")
            for sensor in sensors:
                print(f"ID: {sensor['id']}")
                print(f"Nazwa parametru: {sensor['param']['paramName']}")
        else:
            print("Brak dostępnych sensorów dla podanej stacji pomiarowej.")

    def get_measurement():
        """
           Pobiera dane pomiarowe dla określonego czujnika i daty, wypisuje te dane,
                generuje wartości ekstremalne, zapisuje dane pomiarowe do bazy danych i weryfikuje zapisane dane.

           Zwraca:
               None
           """
        sensor_id = sensor_entry.get()
        start_date_str = start_date_entry.get()
        start_date = dt.strptime(start_date_str, '%Y-%m-%d')
        measure_data = download_data(URL_MEASURE_DATA, sensor_id)
        measure = conv_data_to_json(measure_data)
        print("Dane pomiarowe:")
        for measurement in measure['values']:
            measurement_date = dt.strptime(measurement['date'], '%Y-%m-%d %H:%M:%S')
            if measurement_date.date() == start_date.date():
                print(f"Data: {measurement['date']}, Value: {measurement['value']}")
        # Dodano przyciski do generowania wartości ekstremalnych
        generate_extremes_button = tk.Button(frame_measurement_analysis, text="Generuj wartości ekstremalne",
                                             command=lambda: generate_extremes(measure['values']))
        generate_extremes_button.pack(side=tk.LEFT)

        # Zapisz dane pomiarowe do bazy danych
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()

        measurements = []
        for measurement in measure['values']:
            measurement_date = dt.strptime(measurement['date'], '%Y-%m-%d %H:%M:%S')
            if measurement_date.date() == start_date.date() and measurement['value'] is not None:
                measurements.append((int(sensor_id), float(measurement['value']), measurement['date']))

        c.executemany('INSERT INTO measurement_data (sensor_id, value, date) VALUES (?, ?, ?)', measurements)
        conn.commit()

        # Dodaj ten kawałek kodu, aby sprawdzić czy dane zostały zapisane poprawnie
        c.execute('SELECT * FROM measurement_data')
        rows = c.fetchall()
        for row in rows:
            print(row)

        conn.close()

    def generate_extremes(values):
        """
            Generuje wartości ekstremalne na podstawie listy pomiarów.

            Args:
                values (list): Lista wartości pomiarowych.

            Zwraca:
                None
            """
        value_list = [float(measurement['value']) for measurement in values if measurement['value'] is not None]
        if value_list:
            max_value = max(value_list)
            min_value = min(value_list)
            print(f"Największa wartość: {max_value}")
            print(f"Najmniejsza wartość: {min_value}")
        else:
            print("Brak dostępnych danych pomiarowych.")

    def generate_plot():
        """
            Generuje wykres danych pomiarowych dla określonego czujnika, rozpoczynając od podanej daty.

            Zwraca:
                None
            """
        sensor_id = sensor_entry.get()
        start_date = start_date_entry.get()
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        measure_data = download_data(URL_MEASURE_DATA, sensor_id)
        measure = conv_data_to_json(measure_data)

        dates = []
        values = []

        for measurement in measure['values']:
            measurement_date = dt.strptime(measurement['date'], '%Y-%m-%d %H:%M:%S')
            if measurement_date >= start_date:
                if measurement['value'] is not None:
                    dates.append(measurement_date)
                    values.append(float(measurement['value']))

        plt.plot(dates, values)
        plt.xlabel('Data')
        plt.ylabel('Wartość')
        plt.title('Wykres danych pomiarowych')

        # Wyznaczanie linii trendu
        if len(dates) >= 2:
            x = np.array([(date - dates[0]).days for date in dates])
            y = np.array(values)
            coeffs = np.polyfit(x, y, 1)
            trendline = np.poly1d(coeffs)
            plt.plot(dates, trendline(x), color='red', linestyle='--', label='Linia trendu')

        plt.legend()
        plt.show()

    def check_index():
        """
            Sprawdza wskaźnik jakości powietrza dla określonej stacji i wypisuje odpowiednie informacje.

            Returns:
                None
            """
        station_id = station_entry.get()
        index_data = download_data(URL_AIR_QUALITY_INDEX, station_id)
        air_quality_index = conv_data_to_json(index_data)

        if air_quality_index:
            print("Wskaźnik jakości powietrza:")
            print(f"Data: {air_quality_index['stCalcDate']}")
            print(f"Indeks CAQI: {air_quality_index['stIndexLevel']['indexLevelName']}")
            print(f"Jakość powietrza: {air_quality_index['stIndexLevel']['indexLevelName']}")
        else:
            print("Brak danych o wskaźniku jakości powietrza dla tej stacji.")

    def find_nearest_station():
        """
           Wyszukuje najbliższą stację na podstawie lokalizacji użytkownika i zakresu odległości.

           Returns:
               None
           """
        user_location = location_entry.get()
        distance_range = float(distance_entry.get())

        def get_coordinates(location):
            """
                Pobiera współrzędne geograficzne dla podanej lokalizacji.

                Args:
                    location (str): Lokalizacja do przetworzenia.

                Returns:
                    tuple: Para wartości (szerokość geograficzna, długość geograficzna) lub None, jeśli nie można znaleźć współrzędnych.
                """
            geolocator = Nominatim(user_agent="air_quality_app")
            location_data = geolocator.geocode(location)

            if location_data:
                latitude = location_data.latitude
                longitude = location_data.longitude
                return latitude, longitude
            else:
                print("Nie można znaleźć współrzędnych dla podanej lokalizacji.")
                return None

        def calculate_distance(coords1, coords2):
            """
                Oblicza odległość między dwoma parami współrzędnych geograficznych.

                Args:
                    coords1 (tuple): Pierwsza para współrzędnych (szerokość geograficzna, długość geograficzna).
                    coords2 (tuple): Druga para współrzędnych (szerokość geograficzna, długość geograficzna).

                Returns:
                    float: Obliczona odległość w kilometrach.
                """
            return geodesic(coords1, coords2).kilometers

        all_station_data = download_data(URL_STATION)
        all_station = conv_data_to_json(all_station_data)

        user_coords = get_coordinates(user_location)

        if user_coords:
            stations_within_range = []

            for station in all_station:
                station_coords = (station['gegrLat'], station['gegrLon'])
                station_distance = calculate_distance(user_coords, station_coords)

                if station_distance <= distance_range:
                    stations_within_range.append(station)

            if stations_within_range:
                print(f"Liczba stacji w odległości {distance_range} km: {len(stations_within_range)}")
                print("Stacje pomiarowe w określonym zakresie:")
                for station in stations_within_range:
                    print(f"ID: {station['id']}")
                    print(f"Nazwa: {station['stationName']}")
                    print(f"Odległość: {calculate_distance(user_coords, (station['gegrLat'], station['gegrLon']))} km")
            else:
                print("Brak stacji pomiarowych w określonym zakresie.")
        else:
            print("Nie można znaleźć stacji pomiarowej dla podanej lokalizacji.")

    root = tk.Tk()

    frame_station_sensor = tk.Frame(root)
    frame_station_sensor.pack()

    station_list_button = tk.Button(frame_station_sensor, text="Generuj listę ID stacji", command=generate_station_list)
    station_list_button.pack(side=tk.LEFT)

    # Dodano przycisk "Stop" do zatrzymania pobierania danych
    stop_button = tk.Button(frame_station_sensor, text="Stop", command=lambda: stop_download())
    stop_button.pack(side=tk.LEFT)

    station_label = tk.Label(frame_station_sensor, text="ID stacji:")
    station_label.pack(side=tk.LEFT)

    station_entry = tk.Entry(frame_station_sensor)
    station_entry.pack(side=tk.LEFT)

    sensor_list_button = tk.Button(frame_station_sensor, text="Generuj listę sensorów", command=get_sensor_list)
    sensor_list_button.pack(side=tk.LEFT)

    frame_measurement_analysis = tk.Frame(root)
    frame_measurement_analysis.pack()

    sensor_label = tk.Label(frame_measurement_analysis, text="ID sensora:")
    sensor_label.pack(side=tk.LEFT)

    sensor_entry = tk.Entry(frame_measurement_analysis)
    sensor_entry.pack(side=tk.LEFT)

    start_date_label = tk.Label(frame_measurement_analysis, text="Data początkowa (RRRR-MM-DD):")
    start_date_label.pack(side=tk.LEFT)

    start_date_entry = tk.Entry(frame_measurement_analysis)
    start_date_entry.pack(side=tk.LEFT)

    get_measurement_button = tk.Button(frame_measurement_analysis, text="Pobierz dane pomiarowe",
                                       command=get_measurement)
    get_measurement_button.pack(side=tk.LEFT)

    generate_plot_button = tk.Button(frame_measurement_analysis, text="Generuj wykres", command=generate_plot)
    generate_plot_button.pack(side=tk.LEFT)

    check_index_button = tk.Button(frame_measurement_analysis, text="Sprawdź wskaźnik jakości powietrza",
                                   command=check_index)
    check_index_button.pack(side=tk.LEFT)

    frame_nearest_station = tk.Frame(root)
    frame_nearest_station.pack()

    location_label = tk.Label(frame_nearest_station, text="Lokalizacja:")
    location_label.pack(side=tk.LEFT)

    location_entry = tk.Entry(frame_nearest_station)
    location_entry.pack(side=tk.LEFT)

    distance_label = tk.Label(frame_nearest_station, text="Odległość (w km):")
    distance_label.pack(side=tk.LEFT)

    distance_entry = tk.Entry(frame_nearest_station)
    distance_entry.pack(side=tk.LEFT)

    find_station_button = tk.Button(frame_nearest_station, text="Znajdź najbliższą stację",
                                    command=find_nearest_station)
    find_station_button.pack(side=tk.LEFT)

    generate_map_button = tk.Button(frame_nearest_station, text="Generuj mapę stacji", command=generate_station_map)
    generate_map_button.pack(side=tk.LEFT)


    def stop_download():
        global stop_flag  # Ustawienie flagi zatrzymania na True
        stop_flag = True

    root.mainloop()


if __name__ == "__main__":
    get_measurement_data()