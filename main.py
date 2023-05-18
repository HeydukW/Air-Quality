import requests
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

URL_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
URL_MEASURE_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/"
URL_MEASURE_DATA = "https://api.gios.gov.pl/pjp-api/rest/data/getData/"
URL_AIR_QUALITY_INDEX = "https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/"


def download_data(url, id="-1"):
    headers = {'User-Agent': 'Mozilla/5.0'}

    if (id == "-1"):
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


all_station_data = download_data(URL_STATION)
all_station = conv_data_to_json(all_station_data)
print(all_station)

station_id_from_user = input('Podaj id stanowsika: ')
selected_station_information_data = download_data(URL_MEASURE_STATION, station_id_from_user)
selected_station_data = conv_data_to_json(selected_station_information_data)
print(selected_station_data)

if selected_station_data:
    print("Parametry dla wybranej stacji:")
    for sensor in selected_station_data:
        print(f"- {sensor['param']['paramName']}")
else:
    exit()

measure_data = download_data(URL_MEASURE_DATA, station_id_from_user)
measure = conv_data_to_json(measure_data)
print(measure)

for measurement in measure['values']:
    print(f"Data: {measurement['date']}, Value: {measurement['value']}")

air_quality_index_data = download_data(URL_MEASURE_DATA, station_id_from_user)
air_quality_index = conv_data_to_json(air_quality_index_data)
print(air_quality_index)


###################################################

# #lokalizacja


# Funkcja do pobierania współrzędnych geograficznych na podstawie podanej lokalizacji
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


# Funkcja do obliczania odległości między dwoma współrzędnymi geograficznymi
def calculate_distance(coords1, coords2):
    return geodesic(coords1, coords2).kilometers


