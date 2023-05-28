# Air-Quality
Powyższy kod jest skryptem Pythona służącym do pobierania danych dotyczących jakości powietrza z serwisu GIOŚ (Główny Inspektorat Ochrony Środowiska) oraz analizy tych danych. Oto krótki opis poszczególnych elementów kodu:

Aplikacja używa bibliotek takich jak tkinter, requests, json, geopy, numpy, sqlite3 oraz matplotlib. Aby uruchomić aplikację, należy wywołać funkcję generate_station_map().

## Funkcje

### redirect_stdout_to_text_widget(widget)
Funkcja redirect_stdout_to_text_widget(widget) przekierowuje wyjście standardowe do widżetu tekstowego w interfejsie użytkownika.

### create_table()
Funkcja create_table() tworzy tabelę o nazwie 'measurement_data' w bazie danych 'air_quality.db'. Tabela zawiera kolumny: station_id (INTEGER), sensor_id (INTEGER), date (TEXT), value (REAL).

### download_data(url, id="-1")
Funkcja download_data(url, id="-1") pobiera dane z podanego adresu URL. 

#### Parametry:
- url (str): Adres URL, z którego mają być pobrane dane.
- id (str, opcjonalny): ID stacji/sensora. Domyślnie "-1".
Funkcja zwraca obiekt odpowiedzi HTTP.

### generate_station_map()
Funkcja generate_station_map() generuje mapę lokalizacji stacji pomiarowych. Wykorzystuje moduł Basemap z biblioteki matplotlib.

### conv_data_to_json(response)
Funkcja conv_data_to_json(response) konwertuje dane z formatu JSON na słownik. Parametry:
- response (Response): Obiekt odpowiedzi HTTP.
Funkcja zwraca przekonwertowane dane w postaci słownika.

### get_measurement_data()
Funkcja get_measurement_data() to główna funkcja do pobierania danych pomiarowych. Wyświetla interfejs użytkownika i obsługuje różne akcje użytkownika.

## Inne funkcje
Ponadto, w kodzie są zdefiniowane inne funkcje pomocnicze, takie jak:

- generate_station_list(): generuje listę stacji, pobiera ich dane i wypisuje ich identyfikatory oraz lokalizacje,
- get_location_from_coordinates(coords): pobiera lokalizację na podstawie współrzędnych geograficznych,
- get_sensor_list(): pobiera listę czujników dla określonej stacji i wypisuje ich identyfikatory oraz nazwy parametrów,
- get_measurement(): pobiera dane pomiarowe dla określonego czujnika i daty, wypisuje te dane, generuje wartości ekstremalne, zapisuje dane pomiarowe do bazy danych i weryfikuje zapisane dane,
- generate_extremes(values): generuje wartości ekstremalne na podstawie listy pomiarów,
- generate_plot(): generuje wykres danych pomiarowych dla określonego czujnika, rozpoczynając od podanej daty,
- check_index(): sprawdza wskaźnik jakości powietrza dla okreś.
- 