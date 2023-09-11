import requests
import subprocess
import json
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
    print("El documento " + config_file + " no existe")
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
    url = config["webadmin_canodrom"]
    response = session.get(url, headers=login_headers)

    # Obtener el directorio de destino
    id_directory = os.path.join(config["jsons_descarregats"], "Desc")

    # Obtener la ruta completa del archivo JSON
    id_path = os.path.join(config["jsons_descarregats"], "ID", "info_2023.json")

    # Cargar los datos existentes del archivo JSON si existe
    if os.path.exists(id_path):
        with open(id_path, 'r') as file:
            data = json.load(file)
    else:
        data = []

    # Crear la lista de opciones para seleccionar los documentos
    options = [(item['ID'], item['Title']) for item in data]

    # Verificar si la lista de opciones está vacía
    if not options:        
        # Preguntar si desea actualizar los datos
        response = sg.popup_yes_no("No hi ha documents d'activitats disponibles.\nActualitza les dades abans de continuar.\nVols actualitzar les dades a la data actual?", title="Descàrrega d'activitats")
        
        if response == 'Yes':
            # Ejecutar el script de actualización de datos
            subprocess.check_call(["python3", config["id"]])
        
        # Salir del programa
        exit()

    # Definir el diseño de la interfaz
    layout = [
        [sg.Text("Selecciona les activitats a descarregar:")],
        [sg.Listbox(options, size=(40, 10), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='-DOCUMENTS-')],
        [sg.Button("Descarregar", key='-DOWNLOAD-')]
    ]

    # Crear la ventana de la interfaz
    window = sg.Window("Descarregar activitats", layout)

    # Bucle principal de la interfaz
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == '-DOWNLOAD-':
            # Obtener los documentos seleccionados
            selected_documents = values['-DOCUMENTS-']

            # Variable para contar el número de documentos descargados
            downloaded_count = 0

            # Descargar los documentos seleccionados
            for document_id, document_title in selected_documents:
                export_url = f"https://comunitat.canodrom.barcelona/admin/assemblies/comunitat/components/1651/manage/meetings/{document_id}/registrations/export.JSON?locale=en"
                export_response = session.get(export_url, headers=login_headers)

                if export_response.status_code == 200:
                    # Obtener el directorio de destino
                    output_directory = config["jsons_descarregats"]

                    # Generar el nombre de archivo basado en el título del documento
                    file_name = f"{document_id}.json"

                    # Obtener la ruta completa del archivo
                    file_path = os.path.join(output_directory, file_name)

                    # Guardar el archivo JSON
                    with open(file_path, 'w') as file:
                        file.write(export_response.text)

                    downloaded_count += 1

                    # Agregar el documento descargado al archivo "descarregues.json"
                    descarregues_path = os.path.join(id_directory, "descarregues.json")
                    if os.path.exists(descarregues_path):
                        with open(descarregues_path, 'r') as file:
                            descarregues_data = json.load(file)
                    else:
                        descarregues_data = []

                    descarregues_data.append({
                        "ID": str(document_id),
                        "Title": str(document_title)
                    })

                    # Eliminar duplicados en la lista de descargas
                    descarregues_data = list({item['ID']: item for item in descarregues_data}.values())

                    # Guardar los documentos descargados en el archivo "descarregues.json"
                    with open(descarregues_path, 'w') as file:
                        json.dump(descarregues_data, file, indent=4)

                else:
                    print(f"No s'ha pogut descarregar l'arxiu JSON pel document {document_title}")

            # Deseleccionar los documentos descargados
            for index, item in enumerate(options):
                if item in selected_documents:
                    window['-DOCUMENTS-'].Widget.selection_clear(index)

            # Mostrar el cuadro de diálogo para preguntar si desea descargar más documentos
            response = sg.popup_yes_no(f"S'han descargat {downloaded_count} documents. Vols descarregar mes documents?", title=f"{downloaded_count} documents descarregats")
            print(f"S'han descarregat {downloaded_count} documents")

            if response == 'No':
                break

    window.close()

else:
    print("Error al iniciar sessió. Verifica les credencials.")
