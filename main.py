import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta
import tkinter as tk
import requests
import json
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import numpy as np

URL_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
URL_MEASURE_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/"
URL_MEASURE_DATA = "https://api.gios.gov.pl/pjp-api/rest/data/getData/"
URL_AIR_QUALITY_INDEX = "https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/"


def download_data(url, id="-1"):
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
        exit()


def conv_data_to_json(response):
    try:
        data = response.json()
        return data
    except json.decoder.JSONDecodeError:
        print('Niepoprawny format danych JSON')
        return None


def get_measurement_data():
    def generate_station_list():
        all_station_data = download_data(URL_STATION)
        all_station = conv_data_to_json(all_station_data)
        print("Lista ID stacji:")
        for station in all_station:
            station_coords = (station['gegrLat'], station['gegrLon'])
            station_location = get_location_from_coordinates(station_coords)
            print(f"ID: {station['id']}, Lokalizacja: {station_location}")

    def get_location_from_coordinates(coords):
        geolocator = Nominatim(user_agent="air_quality_app")
        location_data = geolocator.reverse(coords)
        if location_data:
            return location_data.address
        else:
            return "Nieznana lokalizacja"

    def get_sensor_list():
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

    def generate_extremes(values):
        value_list = [float(measurement['value']) for measurement in values if measurement['value'] is not None]
        if value_list:
            max_value = max(value_list)
            min_value = min(value_list)
            print(f"Największa wartość: {max_value}")
            print(f"Najmniejsza wartość: {min_value}")
        else:
            print("Brak dostępnych danych pomiarowych.")

    def generate_plot():
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
        user_location = location_entry.get()
        distance_range = float(distance_entry.get())

        def get_coordinates(location):
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

    root.mainloop()


if __name__ == "__main__":
    get_measurement_data()

