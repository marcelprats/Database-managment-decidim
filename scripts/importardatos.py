import requests
import json
import datetime
import os
import PySimpleGUI as sg
from bs4 import BeautifulSoup

# Obtén la ruta del archivo de configuración
config_file = "config.json"

# Comprueba si el archivo de configuración existe
if os.path.isfile(config_file):
    # Carga la configuración desde el archivo
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    sg.popup("El archivo de configuración no existe.")
    config = {}

# Define las credenciales de inicio de sesión
username = config.get("correo")
password = config.get("contrasena")

# Verifica si las credenciales están configuradas
if not username or not password:
    sg.popup("Las credenciales de inicio de sesión no están configuradas.")
else:
    # Define la cabecera de la solicitud POST para iniciar sesión
    login_url = 'https://comunitat.canodrom.barcelona/users/sign_in'
    login_payload = {
        'user[email]': username,
        'user[password]': password
    }
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Realiza la solicitud POST para iniciar sesión
    session = requests.Session()
    login_response = session.post(login_url, data=login_payload, headers=login_headers)

    # Verifica si la autenticación ha sido exitosa
    if login_response.status_code == 200:
        # Obtiene el directorio de destino
        id_directory = os.path.join(config.get("jsons_descarregats"), "ID")

        # Crea el directorio si no existe
        if not os.path.exists(id_directory):
            os.makedirs(id_directory)

        # Obtiene la ruta completa de los archivos JSON
        id_path_2023 = os.path.join(id_directory, "info_2023.json")
        id_path = os.path.join(id_directory, "info.json")

        # Comprueba la existencia de los archivos
        if os.path.isfile(id_path) and os.path.isfile(id_path_2023):
            # Obtiene la fecha de la última descarga
            fecha_descarga_anterior = datetime.datetime.fromtimestamp(os.path.getmtime(id_path)).strftime(
                "%d/%m/%Y" + " a les " + "%H:%M:%S"
            )

            # Muestra la ventana emergente para actualizar los datos
            layout = [
                [
                    sg.Text(
                        f"Les dades ja existeixen, vols actualitzar-les?\n\n Descarregades anteriorment el {fecha_descarga_anterior}?"
                    )
                ],
                [sg.Button("Sobreescriure", key='-OVERWRITE-'), sg.Button("Cancel·lar", key='-CANCEL-')]
            ]

            window = sg.Window("Actualitzar dades", layout)

            while True:
                event, _ = window.read()

                if event == sg.WINDOW_CLOSED or event == '-CANCEL-':
                    break

                if event == '-OVERWRITE-':
                    # Realiza la solicitud GET después de iniciar sesión
                    url = config.get("webadmin_canodrom")
                    response = session.get(url, headers=login_headers)

                    # Extrae los datos de la tabla si existe
                    soup = BeautifulSoup(response.content, 'html.parser')
                    table = soup.find('table', class_='table-list')
                    if table:
                        rows = table.find('tbody').find_all('tr')

                        # Filtra las filas para el año 2023 en el campo "Start date"
                        filtered_rows = []
                        for row in rows:
                            start_date = row.find_all('td')[2].text.strip()
                            if '2023' in start_date:
                                filtered_rows.append(row)

                        # Extrae los ID y los títulos de las filas filtradas (2023)
                        data_2023 = []
                        for row in filtered_rows:
                            data_2023.append({
                                'ID': row.find('td').text.strip(),
                                'Title': row.find_all('td')[1].text.strip()
                            })

                        # Extrae los ID y los títulos de todas las filas
                        data = []
                        for row in rows:
                            data.append({
                                'ID': row.find('td').text.strip(),
                                'Title': row.find_all('td')[1].text.strip()
                            })

                        # Guarda los datos filtrados para el año 2023 en un archivo JSON
                        with open(id_path_2023, 'w') as file:
                            json.dump(data_2023, file, indent=4)

                        # Guarda los datos completos en un archivo JSON
                        with open(id_path, 'w') as file:
                            json.dump(data, file, indent=4)

                        sg.popup("Les dades s'han actualizat correctament.")
                    else:
                        sg.popup("No se ha encontrado la tabla en la página.")
                    break

            window.close()
        else:
            # Muestra la ventana emergente para descargar los datos
            layout = [
                [sg.Text("No s'han trobat cap registre de dades.\n Vols descargarregar-les?")],
                [sg.Button("Descargar", key='-DOWNLOAD-'), sg.Button("Cancelar", key='-CANCEL-')]
            ]

            window = sg.Window("Descargar datos", layout)

            while True:
                event, _ = window.read()

                if event == sg.WINDOW_CLOSED or event == '-CANCEL-':
                    break

                if event == '-DOWNLOAD-':
                    # Realiza la solicitud GET después de iniciar sesión
                    url = config.get("webadmin_canodrom")
                    response = session.get(url, headers=login_headers)

                    # Extrae los datos de la tabla si existe
                    soup = BeautifulSoup(response.content, 'html.parser')
                    table = soup.find('table', class_='table-list')
                    if table:
                        rows = table.find('tbody').find_all('tr')

                        # Filtra las filas para el año 2023 en el campo "Start date"
                        filtered_rows = []
                        for row in rows:
                            start_date = row.find_all('td')[2].text.strip()
                            if '2023' in start_date:
                                filtered_rows.append(row)

                        # Extrae los ID y los títulos de las filas filtradas (2023)
                        data_2023 = []
                        for row in filtered_rows:
                            data_2023.append({
                                'ID': row.find('td').text.strip(),
                                'Title': row.find_all('td')[1].text.strip()
                            })

                        # Extrae los ID y los títulos de todas las filas
                        data = []
                        for row in rows:
                            data.append({
                                'ID': row.find('td').text.strip(),
                                'Title': row.find_all('td')[1].text.strip()
                            })

                        # Guarda los datos filtrados para el año 2023 en un archivo JSON
                        with open(id_path_2023, 'w') as file:
                            json.dump(data_2023, file, indent=4)

                        # Guarda los datos completos en un archivo JSON
                        with open(id_path, 'w') as file:
                            json.dump(data, file, indent=4)

                        print("Les dades s'han descarregat correctament, ja pots descarregar els documents.")
                    else:
                        sg.popup("No se ha encontrado la tabla en la página.")
                    break

            window.close()
    else:
        sg.popup("Error en iniciar sesión. Verifica las credenciales.")
