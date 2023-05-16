import tkinter as tk

def get_measurement_data():
    # Kod do pobierania danych pomiarowych
    pass

def check_air_quality_index():
    # Kod do sprawdzania indeksu jakości powietrza
    pass

def find_nearest_station():
    # Kod do znajdowania najbliższej stacji pomiarowej
    pass

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
