import tkinter as tk
import tkinter.messagebox as messagebox
import json
import os
import requests
from bs4 import BeautifulSoup

redirect_url = "https://comunitat.canodrom.barcelona/"

def login_successful(username, password, redirect_url):
    login_url = 'https://comunitat.canodrom.barcelona/users/sign_in'

    # Obtener el token CSRF
    session = requests.Session()
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

    # Datos de inicio de sesión
    login_data = {
        'user[email]': username,
        'user[password]': password,
        'authenticity_token': csrf_token
    }

    # Realizar la solicitud de inicio de sesión
    response = session.post(login_url, data=login_data)

    if response.status_code == 200 and response.url == redirect_url:
        mensaje = 'Inici de sessió exitós\nJa pots entrar a la Gestió de Dades'
        creadirectoris()
        return True, csrf_token, mensaje
    else:
        mensaje = "Ha fallat l'inici de sessió\nComproba les credencials i torna-ho a probar\n\n"
        return False, None, mensaje

    print(mensaje)

directorio_principal = os.getcwd()

def creadirectoris():
    config = {
        "directorio_principal": directorio_principal,
        "webadmin_canodrom": "https://comunitat.canodrom.barcelona/admin/assemblies/comunitat/components/1651/manage/meetings?assembly_slug=comunitat&component_id=1651&locale=en&per_page=100",
    }
                
    try:
        # Verificar si el directorio base ya existe
        if not os.path.exists(directorio_principal):
            # Crear el directorio base
            os.makedirs(directorio_principal)
            print(f"S'ha creat el directori {directorio_principal}")
        else:
            pass
        # Directorios anidados
        directorios = [
            "jsons/grafics/",
            "jsons/jsons_descarregats/Desc/",
            "jsons/jsons_descarregats/ID/",
        ]

        # Crear los directorios anidados dentro del directorio base
        for directorio in directorios:
            directorio_path = os.path.join(directorio_principal, directorio)
            os.makedirs(directorio_path, exist_ok=True)
        
        # Ruta del archivo JSON
        ruta_archivo = directorio_principal + "/jsons/jsons_descarregats/Desc/descarregues.json"
        ruta_archivogr = directorio_principal + "/jsons/grafics/grconfig.json"


        # Crear un diccionario vacío
        datas = []
        datasg = {
        "Exemple 1": {
            "title": "Frendy Copper 20/07",
            "show_title": True,
            "subtitle": "",
            "show_subtitle": True,
            "show_total": False,
            "size": "8x6",
            "chart_type": "Gr\u00e0fic de barres",
            "legend": True   
        },
       "Exemple 2": {
            "title": "Gr\u00e0fic Circular",
            "show_title": True,
            "subtitle": "",
            "show_subtitle": False,
            "show_total": False,
            "size": "8x6",
            "chart_type": "Gr\u00e0fic circular",
            "legend": True   
        },
        "Exemple 3": {
            "title": "Gr\u00e0fic de Barres",
            "show_title": False,
            "subtitle": "",
            "show_subtitle": False,
            "show_total": False,
            "size": "8x6",
            "chart_type": "Gr\u00e0fic de barres",
            "legend": True   
        },
}
        
        if not os.path.isfile(ruta_archivo):
            with open(ruta_archivo, "w") as f:
                json.dump(datas, f)
        if not os.path.isfile(ruta_archivogr):
            with open(ruta_archivogr, "w") as f:
                json.dump(datasg, f, indent=4)       

    except OSError as e:
        print(f"Error al crear l'estructura de directoris: {str(e)}")
        


class CanodromApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Inici de sessió")

        # Obtén la ruta del archivo de configuración
        config_file = "config.json"

        # Comprueba si el archivo de configuración existe
        if os.path.isfile(config_file):
            # Carga la configuración desde el archivo
            with open(config_file, "r") as f:
                config = json.load(f)
        else:
            config = {}

        # Variables para almacenar los directorios seleccionados
        self.correo = tk.StringVar()
        self.contrasena = tk.StringVar()

        # Variable para controlar el estado del botón
        self.button_clicked = False

        def save_config():
            if not self.correo.get():
                messagebox.showerror("Error", "Per favor, introdueix un correu abans de guardar la configuració.")
            elif not self.contrasena.get():
                messagebox.showerror("Error", "Per favor, introdueix una contrasenya abans de guardar la configuració.")
            elif not self.button_clicked:
                self.button_clicked = True
                button_save.config(state="disabled")  # Desactivar el botón después de hacer clic
                try:
                    
                    # Intentar iniciar sesión utilizando los datos proporcionados
                    success, token, mensaje = login_successful(self.correo.get(), self.contrasena.get(), redirect_url)
                    
                    if success:
                        print(mensaje)
                        # Asignar el valor de directorio_principal
                        carpetacanodrom = directorio_principal

                        config = {
                            "directorio_principal": carpetacanodrom,
                            "jsons": carpetacanodrom + "/jsons",
                            "jsons_descarregats": carpetacanodrom + "/jsons/jsons_descarregats",
                            "png": carpetacanodrom + "/png",
                            "descargarjson": carpetacanodrom + "/scripts/descargarjson",                            
                            "grafics": carpetacanodrom + "/scripts/grafics",
                            "importardatos":carpetacanodrom + "/scripts/importardatos.py",
                            "id": carpetacanodrom + "/scripts/id.py",
                            "mostrardescarregues": carpetacanodrom + "/scripts/mostrardescarregues.py",
                            "correo": self.correo.get(),
                            "contrasena": self.contrasena.get(),
                            "token": token,
                            "webadmin_canodrom": "https://comunitat.canodrom.barcelona/admin/assemblies/comunitat/components/1651/manage/meetings?assembly_slug=comunitat&component_id=1651&locale=en&per_page=100"                        
                        }

                        with open(config_file, "w") as file:
                            json.dump(config, file, indent=4) 
                        messagebox.showinfo("Inici de sessió", "Compte trobat, dades guardades.")
                        self.root.destroy()  # Cerrar la aplicación después de iniciar sesión exitosamente
                    else:
                        messagebox.showerror("Error", "Dades del correu o contrasenya incorrectes, introdueix-los de nou.")
                        print(mensaje)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar la configuració: {str(e)}")
                finally:
                    self.button_clicked = False
                    button_save.config(state="normal")  # Habilitar el botón nuevamente

        # Texto de instrucción
        instrucciones = tk.Label(self.root, text="Per poder entrar a la Gestió de Dades\n primer has d'iniciar sessió amb el teu\n correu i contrasenya del compte de Canòdrom")
        instrucciones.pack(pady=10)

        # Fila para el correo
        row_correo = tk.Frame(self.root)
        row_correo.pack(pady=10)

        label_correo = tk.Label(row_correo, text="Correu:")
        label_correo.pack(side=tk.LEFT, padx=10)

        entry_correo = tk.Entry(row_correo, textvariable=self.correo)
        entry_correo.pack(side=tk.LEFT, padx=10)

        # Fila para la contraseña
        row_contrasena = tk.Frame(self.root)
        row_contrasena.pack(pady=10)

        label_contrasena = tk.Label(row_contrasena, text="Contrasenya:")
        label_contrasena.pack(side=tk.LEFT, padx=10)

        entry_contrasena = tk.Entry(row_contrasena, textvariable=self.contrasena, show="*")
        entry_contrasena.pack(side=tk.LEFT, padx=10)

        # Botón para guardar la configuración
        button_save = tk.Button(self.root, text="Iniciar sessió", command=save_config)
        button_save.pack(pady=10)

        # Asociar la tecla "Enter" al botón de guardar configuración
        entry_contrasena.bind("<Return>", lambda event: button_save.invoke())

        # Centrar la ventana en la pantalla
        self.root.eval('tk::PlaceWindow . center')

        # Mostrar la ventana
        self.root.mainloop()

# Crear una instancia de la aplicación
app = CanodromApp()
