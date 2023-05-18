import tkinter as tk
import requests
import json
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

URL_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
URL_MEASURE_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/"
URL_MEASURE_DATA = "https://api.gios.gov.pl/pjp-api/rest/data/getData/"
URL_AIR_QUALITY_INDEX = "https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/"


def download_data(url, id="-1"):
    headers = {'User-Agent': 'Mozilla/5.0'}

    if id == "-1":
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(f'{url}{id}', headers=headers)

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
        exit()


def get_measurement_data():
    station_id = input("Podaj ID stacji: ")
    measure_data = download_data(URL_MEASURE_DATA, station_id)
    measure = conv_data_to_json(measure_data)
    print("Dane pomiarowe:")
    for measurement in measure['values']:
        print(f"Data: {measurement['date']}, Value: {measurement['value']}")


def check_air_quality_index():
    station_id = input("Podaj ID stacji: ")
    air_quality_index_data = download_data(URL_AIR_QUALITY_INDEX, station_id)
    air_quality_index = conv_data_to_json(air_quality_index_data)

    if 'stIndexLevel' in air_quality_index and 'calcDate' in air_quality_index['stIndexLevel']:
        print("Indeks jakości powietrza:")
        print(f"Wartość: {air_quality_index['stIndexLevel']['indexLevelName']}")
        print(f"Data: {air_quality_index['stIndexLevel']['calcDate']}")
    else:
        print("Nieprawidłowe dane indeksu jakości powietrza.")


def find_nearest_station():
    user_location = input("Podaj swoją lokalizację: ")
    distance_range = float(input("Podaj zakres (w km): "))

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
            print("Nie znaleziono stacji pomiarowych w podanym zakresie odległości.")


def main():
    root = tk.Tk()

    frame = tk.Frame(root)
    frame.pack()

    measurement_data_button = tk.Button(frame, text="Pobierz dane pomiarowe", command=get_measurement_data)
    measurement_data_button.pack(side=tk.LEFT)

    air_quality_index_button = tk.Button(frame, text="Sprawdź indeks jakości powietrza", command=check_air_quality_index)
    air_quality_index_button.pack(side=tk.LEFT)

    nearest_station_button = tk.Button(frame, text="Znajdź najbliższą stację pomiarową", command=find_nearest_station)
    nearest_station_button.pack(side=tk.LEFT)

    root.mainloop()


if __name__ == '__main__':
    main()
