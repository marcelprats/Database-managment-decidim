import requests
import json
import os
import concurrent.futures
from bs4 import BeautifulSoup
import PySimpleGUI as sg

# Funció per descarregar un archiu JSON
def descarregar_json(meeting_id, export_url, login_headers):
    export_response = session.get(export_url, headers=login_headers)
    if export_response.status_code == 200:
        output_path = os.path.join(output_directory, f'{meeting_id}.json')
        with open(output_path, 'wb') as export_file:
            export_file.write(export_response.content)
        return meeting_id
    else:
        return None


# Obtén la ruta del archivo de configuración
config_file = "config.json"

# Comprueba si el archivo de configuración existe
if os.path.isfile(config_file):
    # Carga la configuración desde el archivo
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    sg.popup_error("Error", "El documento " + config_file + " no existe")
    config = {}

# Definir las credenciales de inicio de sesión
username = config["correo"]
password = config["contrasena"]

# Definir el encabezado de la solicitud POST para iniciar sesión
login_url = 'https://comunitat.canodrom.barcelona/users/sign_in'
login_payload = {
    'user[email]': username,
    'user[password]': password
}
login_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Realizar la solicitud POST para iniciar sesión
session = requests.Session()
login_response = session.post(login_url, data=login_payload, headers=login_headers)

# Verificar si la autenticación fue exitosa
if login_response.status_code == 200:
    # Realizar la solicitud GET después de iniciar sesión
    url = "https://comunitat.canodrom.barcelona/admin/assemblies/comunitat/components/1651/manage/meetings?assembly_slug=comunitat&component_id=1651&locale=en&per_page=100"
    response = session.get(url, headers=login_headers)

    # Extraer los datos de la tabla si existe
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='table-list')
    if table:
        rows = table.find('tbody').find_all('tr')

        # Filtrar las filas por el año 2023 en el campo "Start date"
        filtered_rows = []
        for row in rows:
            start_date = row.find_all('td')[2].text.strip()
            if '2023' in start_date:
                filtered_rows.append(row)

        # Extraer los ID y los títulos de las filas filtradas
        data = []
        for row in filtered_rows:
            data.append({
                'ID': row.find('td').text.strip(),
                'Title': row.find_all('td')[1].text.strip()
            })

        # Directorio de destino para los archivos JSON descargados
        output_directory = config["jsons_descarregats"]

        # Crear la ventana emergente
        layout = [
            [sg.Text(f"S'han trobat {len(data)} activitats,\n Vols descarregar-les?")],
            [sg.Button("Sí"), sg.Button("No")]
        ]
        window = sg.Window("Descarregar activitats", layout)

        # Leer los eventos de la ventana
        event, _ = window.read()

        # Comprobar la respuesta del usuario
        if event == "Sí":
            id_path = os.path.join(output_directory + "/Desc", 'descarregues.json')

            # Guardar los datos en un archivo JSON
            with open(id_path, 'w') as file:
                json.dump(data, file, indent=4)

            # Descargar los archivos JSON en hilos concurrentes
            successful_downloads = []

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for item in data:
                    meeting_id = item['ID']
                    document_title = item['Title']
                    export_url = f"https://comunitat.canodrom.barcelona/admin/assemblies/comunitat/components/1651/manage/meetings/{meeting_id}/registrations/export.JSON?locale=en"
                    future = executor.submit(descarregar_json, meeting_id, export_url, login_headers)
                    futures.append(future)

                # Esperar a que todas las descargas terminen
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        successful_downloads.append(result)

            # Actualizar el mensaje en la ventana emergente con los resultados
            if successful_downloads:
                # Crear una lista de listas con los detalles de los documentos descargados
                details = [[item['ID'], item['Title']] for item in data]

                # Crear el diseño de la ventana emergente con los detalles
                layout_details = [
                    [sg.Text(' ', size=(30, 1)),sg.Text('Detalls de les activitats descarregades', font=('Arial', 14, 'bold'))],
                    [sg.Text('ID', size=(10, 1), font=('Arial', 12, 'bold')), sg.Text(' ', size=(30, 1)), sg.Text('Nom', size=(30, 1), font=('Arial', 12, 'bold'))],
                    [sg.Column([
                        [sg.Text(row[0], font=('Arial', 12)), sg.Text(' ', size=(30, 1)), sg.Text(row[1], font=('Arial', 12))]
                        for row in details
                    ])],
                    [sg.Button('Tancar')]
                ]

                # Crear la ventana emergente con los detalles
                window_details = sg.Window('Activitats descarregades', layout_details)

                # Leer los eventos de la ventana
                event, _ = window_details.read()

                # Cerrar la ventana
                window_details.close()

            else:
                sg.popup("No s'han descarregat activitats.", title="Descàrrega fallida")

            # Imprimir el mensaje en la interfaz
            print("Les activitats s'han descarregat amb èxit")

        else:
            sg.popup("La descàrrega d'activitats ha sigut cancelada.", title="Descàrrega cancelada")
        
        # Cerrar la ventana
        window.close()
        
    else:
        sg.popup_error("Error", "Error al iniciar sessió. Verifica les credencials.")
