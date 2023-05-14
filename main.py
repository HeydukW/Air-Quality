import requests
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic


URL_STATION = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
URL_PLACE = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/"


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

