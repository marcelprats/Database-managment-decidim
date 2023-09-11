import tkinter as tk
from tkinter import font
import os
import subprocess
from subprocess import call

# Executar les comandes sudo apt install python3-pip i pip install -r requirements.txt
subprocess.check_call(["pip", "install", "-r", "requirements.txt"])

class Interfície:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Canòdrom")

        # Obtindre l'amplada i l'alçada de la pantalla
        amplada_pantalla = self.root.winfo_screenwidth()
        altura_pantalla = self.root.winfo_screenheight()

        # Calcular les dimensions de la finestra
        amplada_finestra = int(amplada_pantalla * 0.5)
        altura_finestra = int(altura_pantalla * 0.5)

        # Establir la mida i la posició de la finestra
        posicion_x = int((amplada_pantalla - amplada_finestra) / 2)
        posicion_y = int((altura_pantalla - altura_finestra) / 2)
        self.root.geometry(f"{amplada_finestra}x{altura_finestra}+{posicion_x}+{posicion_y}")

        # Noms dels scripts i les seves rutes
        noms_scripts = {
            "Configuraciovjson.py": "Inici de sessió",
            "Interfazvjson.py": "Gestió dades",
        }

        # Directori de la carpeta "2p"
        dospasos = self.buscar_carpeta("2p")

        if dospasos:
            # Crear el títol gran i bonic
            titulo_font = font.Font(family="Arial", size=18, weight="bold")
            titulo = tk.Label(self.root, text="Benvingut a l'aplicació de Gestió de dades del Canòdrom\n", font=titulo_font)
            titulo.pack(pady=20)

            normal_font = font.Font(family="Arial", size=12)
            titulo = tk.Label(self.root, text="Si es la primera vegada que accedeixes a l'aplicació hauràs d'iniciar sessió per poder accedir a la gestió de dades\n\n", font=normal_font)
            titulo.pack(pady=5)


            # Crear un marc per contenir els botons
            marco_botones = tk.Frame(self.root)
            marco_botones.pack(pady=5)

            # Crear botó per a cada script
            for script, nom_script in noms_scripts.items():
                ruta_script = os.path.join(dospasos, script)
                boton = tk.Button(marco_botones, text=nom_script, command=lambda ruta=ruta_script: self.ejecutar_script(ruta))
                boton.config(width=16, height=3)
                boton.pack()
                       
        else:
            print("No s'ha trobat la carpeta amb els scripts.")

        # Crear finestra de resultat
        self.resultado = tk.StringVar()
        self.etiqueta_resultado = tk.Label(self.root, textvariable=self.resultado, width=300, height=10)
        self.etiqueta_resultado.pack()

    def buscar_carpeta(self, nombre_carpeta):
        directorio_actual = os.getcwd()

        for root, dirs, files in os.walk(directorio_actual):
            if nombre_carpeta in dirs:
                ruta_carpeta = os.path.join(root, nombre_carpeta)
                return ruta_carpeta

        return None

    def ejecutar_script(self, script):
        try:
            proceso = subprocess.Popen(['python3', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            salida, error = proceso.communicate()
            if proceso.returncode == 0:
                self.resultado.set(salida.decode())
            else:
                self.resultado.set(f"Error en executar l'script: {error.decode()}")
        except Exception as e:
            self.resultado.set(f"Error en executar l'script: {str(e)}")

    def executar(self):
        # Executar el bucle principal de la interfície gràfica
        self.root.mainloop()
    
    def actualitzar_noms_scripts(self, noms_scripts):
        self.noms_scripts = noms_scripts


# Crear la instància de la interfície i executar-la
interfície = Interfície()
interfície.executar()