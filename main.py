import requests
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic



URL_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
URL_PLACE = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/"
URL_DANEPOMIAROWE = "https://api.gios.gov.pl/pjp-api/rest/data/getData"

def download_data(url, id=-1):
    headers = {'User-Agent': 'Mozilla/5.0'}

    if (id == -1):
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


allStations = download_data(URL_STATION)
print(allStations)
conv_data_to_json(allStations)
allStationsJson = conv_data_to_json(allStations)
print(allStationsJson)

for station in allStationsJson:
    print(station)

dataFromUser = input('Podaj id stacji: ')
id = download_data(URL_PLACE , dataFromUser)
conv_data_to_json(id)
print(conv_data_to_json(id))


#
def conv_data_to_json(response):
    try:
        data = response.json()
        return data
    except json.decoder.JSONDecodeError:
        print('Niepoprawny format danych JSON')
        exit()


dataFromUser = input('Podaj id stanowiska: ')
url_data = f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{dataFromUser}"
data = download_data(url_data)
data_json = conv_data_to_json(data)
print(data_json)

for measurement in data_json['values']:
    date = measurement['date']
    value = measurement['value']
    print(f"Data: {date}, Value: {value}")


#index

import requests

def get_air_quality_index(station_id):
    url = f"https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/{station_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Nie udało się pobrać danych. Kod odpowiedzi: {response.status_code}")
        return None

station_id = input("Podaj identyfikator stacji pomiarowej: ")
index_data = get_air_quality_index(station_id)

if index_data:
    print(index_data)

###################################################

# #lokalizacja

from geopy.geocoders import Nominatim


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


# Pobranie lokalizacji od użytkownika
user_location = input("Podaj swoją lokalizację: ")

# Pobranie zakresu od użytkownika
distance_range = float(input("Podaj zakres (w km): "))

# Pobranie współrzędnych użytkownika
user_coords = get_coordinates(user_location)

if user_coords:
    closest_station = None
    closest_distance = None

    # Iteracja przez wszystkie stacje pomiarowe
    for station in allStationsJson:
        station_coords = (station['gegrLat'], station['gegrLon'])
        station_distance = calculate_distance(user_coords, station_coords)

        # Sprawdzenie, czy odległość mieści się w zakresie
        if station_distance <= distance_range:
            # Aktualizacja najbliższej stacji, jeśli jest bliższa od poprzedniej
            if closest_distance is None or station_distance < closest_distance:
                closest_station = station
                closest_distance = station_distance

    if closest_station:
        print("Najbliższa stacja pomiarowa:")
        print(f"ID: {closest_station['id']}")
        print(f"Nazwa: {closest_station['stationName']}")
        print(f"Odległość: {closest_distance} km")
    else:
        print("Nie znaleziono stacji pomiarowej w podanym zakresie odległości.")


#######################################################
# Funkcja do pobierania danych z wybranej stacji
def get_station_data(station_id):
    url = f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}"
    response = download_data(url)
    data_json = conv_data_to_json(response)

    if data_json:
        return data_json
    else:
        print("Nie udało się pobrać danych dla wybranej stacji.")
        return None

# Pobranie ID wybranej stacji od użytkownika
selected_station_id = input("Podaj ID wybranej stacji: ")

# Pobranie danych dla wybranej stacji
selected_station_data = get_station_data(selected_station_id)

if selected_station_data:
    print("Parametry dla wybranej stacji:")
    for sensor in selected_station_data:
        parameter_name = sensor['param']['paramName']
        print(f"- {parameter_name}")
else:
    exit()


# Funkcja do pobierania danych pomiarowych dla wybranej stacji
def get_measurement_data(station_id):
    url = f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{station_id}"
    response = download_data(url)
    data_json = conv_data_to_json(response)

    if data_json:
        return data_json['values']
    else:
        print("Nie udało się pobrać danych pomiarowych dla wybranej stacji.")
        return None


