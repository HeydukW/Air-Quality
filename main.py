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

