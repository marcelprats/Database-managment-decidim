import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import shutil
import json
from PIL import ImageTk, Image

# Obtén la ruta del archivo de configuración
config_file = "config.json"

# Comprueba si el archivo de configuración existe
if os.path.isfile(config_file):
    # Carga la configuración desde el archivo
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    print("Hola!\n Abans d'entrar a la Gestió de Dades\nhas d'iniciar sessió")
    # Salir del programa si el archivo de configuración no existe
    exit()


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        text_label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        text_label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class Interfaz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Canódrom")

        # Obtener el ancho y la altura de la pantalla
        ancho_pantalla = self.root.winfo_screenwidth()
        altura_pantalla = self.root.winfo_screenheight()

        # Calcular las dimensiones de la ventana
        ancho_ventana = int(ancho_pantalla * 0.5)
        altura_ventana = int(altura_pantalla * 0.5)

        # Establecer el tamaño y la posición de la ventana
        posicion_x = int((ancho_pantalla - ancho_ventana) / 2)
        posicion_y = int((altura_pantalla - altura_ventana) / 2)
        self.root.geometry(f"{ancho_ventana}x{altura_ventana}+{posicion_x}+{posicion_y}")

        # Directorios de scripts
        Descargarcsvs = config["descargarjson"]
        Grafics = config["grafics"]
        self.directorios_scripts = [
            Descargarcsvs,
            Grafics
        ]

        # Nombres de los botones
        nombres_botones = [
            "Descarregar activitats",
            "Crear gràfics"
        ]

        # Nombres de los scripts
        nombres_scripts = {
            "Danyactual.py": "Descarregar totes les de l'any actual",
            "Panyactual.py": "Seleccionar activitats de l'any actual",
            "Ptots.py": "Seleccionar de les úĺtimes 100 activitats",
            "combinarjson.py": "Combinar Jsons",
            "eliminarduplicats.py": "Eliminar duplicados",
            "multi.py": "Generar gràfics de més d'una activitat",
            "una.py": "Generar gràfics d'una activitat",
        }

        # Crear un marco para el recuadro superior invisible
        marco_recuadro = tk.Label(text=f"Gestió de dades del Canòdrom", font=('Arial', 18, 'bold'))
        marco_recuadro.pack(padx=5, pady=10)

        # Crear un marco para el recuadro superior invisible
        marco_recuadro2 = tk.Label(text=f"Si no tens molt clar cap a on anar fes un cop d'ull al resum", font=('Arial'))
        marco_recuadro2.pack(padx=5, pady=10)

        # Crear un marco para contener los botones
        marco_botones = tk.Frame(self.root)
        marco_botones.pack(pady=10)

        # Cargar las imágenes de los iconos
        config_png = config.get("png")
        ajuda_icon_path = config_png + "/ajuda.png"
        documentos_icon_path = config_png + "/documentos.png"
        actualizar_icon_path = config_png + "/actualizar.png"
        descargar_icon_path = config_png + "/descargar.png"
        grafics_icon_path = config_png + "/grafics.png"
        logos = (45, 45)

        ajuda_icon_path = Image.open(ajuda_icon_path)
        ajuda_icon_path = ajuda_icon_path.resize(logos)  # Ajustar el tamaño del icono si es necesario
        self.ajuda_icon_photo = ImageTk.PhotoImage(ajuda_icon_path)

        documentos_icon_path = Image.open(documentos_icon_path)
        documentos_icon_path = documentos_icon_path.resize(logos)  # Ajustar el tamaño del icono si es necesario
        self.documentos_icon_photo = ImageTk.PhotoImage(documentos_icon_path)

        actualizar_icon_path = Image.open(actualizar_icon_path)
        actualizar_icon_path = actualizar_icon_path.resize(logos)  # Ajustar el tamaño del icono si es necesario
        self.actualizar_icon_photo = ImageTk.PhotoImage(actualizar_icon_path)

        descargar_icon_image = Image.open(descargar_icon_path)
        descargar_icon_image = descargar_icon_image.resize(logos)  # Ajustar el tamaño del icono si es necesario
        self.descargar_icon_photo = ImageTk.PhotoImage(descargar_icon_image)

        grafics_icon_image = Image.open(grafics_icon_path)
        grafics_icon_image = grafics_icon_image.resize(logos)  # Ajustar el tamaño del icono si es necesario
        self.grafics_icon_photo = ImageTk.PhotoImage(grafics_icon_image)

        # Botón para importar jsons con el icono de descargar
        boton_inicio = tk.Button(marco_botones, image=self.ajuda_icon_photo, command=self.mostrar_resumen)
        boton_inicio.pack(side=tk.LEFT, padx=10)
        ToolTip(boton_inicio, "Resum")
 
        # Botón para importar jsons con el icono de descargar
        boton_actualizar = tk.Button(marco_botones, image=self.actualizar_icon_photo, command=self.ejecutar_script_importar_datos)
        boton_actualizar.pack(side=tk.LEFT, padx=10)
        ToolTip(boton_actualizar, "Actualitzar dades a\ndata actual")
 
        # Crear botones para cada carpeta de scripts
        for i, directorio in enumerate(self.directorios_scripts):
            nombre_boton = nombres_botones[i] if i < len(nombres_botones) else f"Carpeta {i+1}"
            if nombre_boton == "Descarregar activitats":
                boton = tk.Button(marco_botones, image=self.descargar_icon_photo, command=lambda dir=directorio: self.actualizar_botones(dir))
            elif nombre_boton == "Crear gràfics":
                boton = tk.Button(marco_botones, image=self.grafics_icon_photo, command=lambda dir=directorio: self.actualizar_botones(dir))
            else:
                boton = tk.Button(marco_botones, text=nombre_boton, command=lambda dir=directorio: self.actualizar_botones(dir))

            boton.pack(side=tk.LEFT, padx=10)
            ToolTip(boton, nombre_boton)

        # Botón para importar jsons con el icono de descargar
        boton_importar = tk.Button(marco_botones, image=self.documentos_icon_photo, command=self.ejecutar_script_mostrar_descargas)
        boton_importar.pack(side=tk.LEFT, padx=10)
        ToolTip(boton_importar, "Mostrar documents\n descarregats")
 
        # Actualizar los nombres de los scripts
        self.actualizar_nombres_scripts(nombres_scripts)
 
        # Crear ventana de resultado
        self.resultado = tk.StringVar()
        self.etiqueta_resultado = tk.Label(self.root, textvariable=self.resultado, width=300, height=10)
        self.etiqueta_resultado.pack()

    def mostrar_resumen(self):
        # Datos para la tabla de resumen
        resumen_datos = [
            {
                "imagen": self.actualizar_icon_photo,
                "accion": "Actualitzar dades a data actual",
                "descripcion": "L'aplicació actualitza la llista d'activitats disponibles\nper descarregar a travès de les dades del Canòdrom."
            },
            {
                "imagen": self.descargar_icon_photo,
                "accion": "Descarregar activitats",
                "descripcion": "Mostra diferents maneres de descarregar les dades\nde les activitats sobre les quals es crearan gràfics"
            },
            {
                "imagen": self.grafics_icon_photo,
                "accion": "Crear gràfics",
                "descripcion": "Generar gràfics a partir de les dades de les activitats\n descarregades, pots crear grafics d'una o més d'una activitat"
            },
            {
                "imagen": self.documentos_icon_photo,
                "accion": "Mostrar documents descarregats",
                "descripcion": "Mostra la llista de les activitats descarregades"
            },
        ]

        # Crear la ventana emergente para mostrar el resumen
        ventana_resumen = tk.Toplevel()
        ventana_resumen.title("Resum")

        # Texto explicativo encima de la tabla
        texto_explicativo = tk.Label(ventana_resumen, text="Un petit resum de com funciona:", font=('Arial', 12, 'bold'))
        texto_explicativo.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        # Crear los elementos de la tabla de resumen
        for i, data in enumerate(resumen_datos):
            imagen_label = tk.Label(ventana_resumen, image=data["imagen"])
            imagen_label.grid(row=i+1, column=0, padx=5, pady=5)

            accion_label = tk.Label(ventana_resumen, text=data["accion"], font=('Arial', 11, 'bold'))
            accion_label.grid(row=i+1, column=1, padx=5, pady=5, sticky='ew')

            descripcion_label = tk.Label(ventana_resumen, text=data["descripcion"], font=('Arial', 11))
            descripcion_label.grid(row=i+1, column=2, padx=5, pady=5, sticky='w')

        # Texto explicativo centrado en el medio de la ventana
        texto_explicativo2 = tk.Label(ventana_resumen, text="IMPORTANT", font=('Arial', 12, 'bold'))
        texto_explicativo2.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        # Texto explicativo centrado en el medio de la ventana
        texto_explicativo3 = tk.Label(ventana_resumen, text="- El primer pas es actualitzar les dades a la data actual.\n- Un cop actualitzades ja hi haurà documents disponibles per descarregar.\n- Una vegada descarregats ja es podràn generar els gràfics. ")
        texto_explicativo3.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

    def actualizar_botones(self, directorio_scripts):
        # Obtener la lista de archivos del directorio de scripts
        archivos = [archivo for archivo in os.listdir(directorio_scripts) if archivo.endswith(".py")]

        # Limpiar los botones existentes
        for boton in self.botones:
            boton.destroy()
        self.botones.clear()

        # Crear un botón para cada script
        for i, script in enumerate(archivos):
            nombre_script = self.nombres_scripts.get(script, script)
            boton = tk.Button(self.root, text=nombre_script, command=lambda script=script: self.ejecutar_script(os.path.join(directorio_scripts, script)))
            boton.config(width=self.boton_width, height=self.boton_height)
            boton.pack()
            self.botones.append(boton)

    def ejecutar_script(self, script):
        try:
            proceso = subprocess.Popen(['python3', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            salida, error = proceso.communicate()
            if proceso.returncode == 0:
                self.resultado.set(salida.decode())
            else:
                self.resultado.set(f"Error al ejecutar el script: {error.decode()}")
        except Exception as e:
            self.resultado.set(f"Error al ejecutar el script: {str(e)}")

    def ejecutar_script_importar_datos(self):
        ruta_script = config["importardatos"]
        try:
            proceso = subprocess.Popen(['python3', ruta_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            salida, error = proceso.communicate()
            if proceso.returncode == 0:
                self.resultado.set(salida.decode())
            else:
                self.resultado.set(f"Error al ejecutar el script: {error.decode()}")
        except Exception as e:
            self.resultado.set(f"Error al ejecutar el script: {str(e)}")

    def ejecutar_script_mostrar_descargas(self):
        ruta_script = config["mostrardescarregues"]
        try:
            proceso = subprocess.Popen(['python3', ruta_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            salida, error = proceso.communicate()
            if proceso.returncode == 0:
                self.resultado.set(salida.decode())
            else:
                self.resultado.set(f"Error al ejecutar el script: {error.decode()}")
        except Exception as e:
            self.resultado.set(f"Error al ejecutar el script: {str(e)}")

    def ejecutar(self):
        self.botones = []
        self.boton_width = 32
        self.boton_height = 3

        # Ejecutar el bucle principal de la interfaz gráfica
        self.root.mainloop()

    def actualizar_nombres_scripts(self, nombres_scripts):
        self.nombres_scripts = nombres_scripts

# Crear la instancia de la interfaz y ejecutarla
interfaz = Interfaz()
interfaz.ejecutar()
