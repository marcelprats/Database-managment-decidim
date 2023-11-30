import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Obtén la ruta del archivo de configuración
config_file = "config.json"

# Comprueba si el archivo de configuración existe
if os.path.isfile(config_file):
    # Carga la configuración desde el archivo
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    tk.messagebox.showerror("Error", "El archivo de configuración no existe.")
    config = {}

# Ruta del archivo JSON
archivo_json = os.path.join(config.get("jsons_descarregats", ""), "Desc", "descarregues.json")

# Ruta del directorio de documentos
directorio_documentos = config.get("jsons_descarregats", "")

# Cargar los datos del archivo JSON
with open(archivo_json, "r") as f:
    datos = json.load(f)

# Crear una lista de tuplas con la información de cada registro
registros = []
documentos_a_eliminar = []
for registro in datos:
    id_valor = registro["ID"]
    title_valor = registro["Title"]
    documento_json = os.path.join(directorio_documentos, f"{id_valor}.json")
    if os.path.isfile(documento_json) and os.stat(documento_json).st_size > 0:
        with open(documento_json, "r") as f:
            contenido = f.read()
        count_code = contenido.count("code")

        # Cortar el título si es muy largo
        if len(title_valor) > 45:
            title_valor = title_valor[:42] + "..."

        if count_code == 0:
            registros.append((0, id_valor, title_valor))
            documentos_a_eliminar.append(documento_json)
        else:
            registros.append((count_code, id_valor, title_valor))


# Función para mostrar un mensaje de que no hay datos descargados
def mostrar_mensaje_sin_datos():
    messagebox.showinfo("Activitats descarregades", "No hi ha activitats a visualitzar")

# Función para mostrar una previsualización del contenido del documento
def mostrar_previsualizacion(id_valor, title_valor, documento_json):
    with open(documento_json, "r") as f:
        contenido = json.load(f)

    # Crear una nueva ventana para mostrar la previsualización en tabla
    titulo_actividad = f"{id_valor} - {title_valor}"
    ventana_previsualizacion = tk.Toplevel()
    ventana_previsualizacion.title(titulo_actividad)
    ventana_previsualizacion.geometry("1000x400")

    # Crear un objeto Treeview (tabla) para mostrar los datos
    tabla_previsualizacion = ttk.Treeview(ventana_previsualizacion, columns=list(contenido[0]["registration_form_answers"].keys()), show="headings")
    tabla_previsualizacion.pack(fill="both", expand=True)

    # Excluir las columnas "Answer ID", "Answered on" e "IP Hash"
    tabla_previsualizacion["displaycolumns"] = list(contenido[0]["registration_form_answers"].keys())[3:]

    # Configurar los encabezados para "registration_form_answers"
    for campo in contenido[0]["registration_form_answers"].keys():
        tabla_previsualizacion.heading(campo, text=campo, command=lambda col=tabla_previsualizacion, col_index=campo: sort_column(tabla_previsualizacion, col_index, False))
        tabla_previsualizacion.column(campo, anchor=tk.CENTER, width=120)

    # Agregar una barra de desplazamiento horizontal a la tabla
    scrollbar_x = ttk.Scrollbar(ventana_previsualizacion, orient=tk.HORIZONTAL, command=tabla_previsualizacion.xview)
    tabla_previsualizacion.configure(xscrollcommand=scrollbar_x.set)
    scrollbar_x.pack(fill=tk.X, side=tk.BOTTOM)

    # Mostrar los datos en la tabla
    for registro in contenido:
        user_info = registro["user"]
        registration_info = registro["registration_form_answers"]

        # Crear una lista con los valores de "registration_form_answers" en el orden correcto
        valores_registro = [str(registration_info[campo]) for campo in contenido[0]["registration_form_answers"].keys()]

        # Insertar una fila en la tabla con los valores correspondientes
        tabla_previsualizacion.insert("", "end", values=valores_registro)

# Función para ordenar la tabla por columna
def sort_column(tree, col, reverse):
    datos = [(tree.set(child, col), child) for child in tree.get_children('')]
    datos.sort(reverse=reverse)

    for index, (val, child) in enumerate(datos):
        tree.move(child, '', index)
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))


# Mostrar la tabla de registros o el mensaje de datos no descargados
if registros:
    # Crear la ventana principal solo si hay registros
    window = tk.Tk()
    window.title("Activitats descarregades")

    # Crear un marco para el recuadro superior invisible
    marco_recuadro = tk.Label(window, text=f"Activitats descarregades: {len(registros)}", font=("bold"))
    marco_recuadro.pack(padx=5, pady=10)

    # Crear un marco para el recuadro superior invisible
    marco_recuadro2 = tk.Label(window, text=f"Aqui es mostren totes les activitats descarregades\n\nApretant el nom pots previsualitzar la informació de cada activitat")
    marco_recuadro2.pack(padx=5, pady=10)

    # Crear un marco para contener los registros
    marco_registros = tk.Frame(window)
    marco_registros.pack(padx=10, pady=10)

    # Encabezados de columna
    encabezados = ["Inscripcions", "ID", "Nom de l'activitat"]
    for i, encabezado in enumerate(encabezados):
        etiqueta_encabezado = tk.Label(marco_registros, text=encabezado, font=("Arial", 12, "bold"), bg="gray", fg="white", padx=10, pady=5)
        etiqueta_encabezado.grid(row=0, column=i, sticky="nsew")

    # Configuración de la paginación
    registros_por_pagina = 20
    total_registros = len(registros)
    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
    pagina_actual = 1

    def mostrar_registros(pagina):
        # Borrar los registros actuales
        for widget in marco_registros.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

        # Calcular el rango de registros a mostrar
        inicio = (pagina - 1) * registros_por_pagina
        fin = inicio + registros_por_pagina

        # Mostrar los registros en la tabla
        for i, registro in enumerate(registros[inicio:fin], start=1):
            count_code, id_valor, title_valor = registro
            fondo = "red" if count_code == 0 else "green"

            etiqueta_count = tk.Label(marco_registros, text=count_code, bg=fondo, fg="white", padx=10, pady=5)
            etiqueta_count.grid(row=i, column=0, sticky="nsew")

            etiqueta_id = tk.Label(marco_registros, text=id_valor, bg=fondo, fg="white", padx=10, pady=5)
            etiqueta_id.grid(row=i, column=1, sticky="nsew")

            etiqueta_titulo = tk.Label(marco_registros, text=title_valor, bg=fondo, fg="white", padx=10, pady=5)
            etiqueta_titulo.grid(row=i, column=2, sticky="nsew")

            # Agregar un evento de clic para mostrar la previsualización
            documento_json = os.path.join(directorio_documentos, f"{id_valor}.json")
            etiqueta_titulo.bind("<Button-1>", lambda event, id_valor=id_valor, title_valor=title_valor, documento_json=documento_json: mostrar_previsualizacion(id_valor, title_valor, documento_json))

    # Mostrar la primera página de registros
    mostrar_registros(pagina_actual)

    # Crear un marco para contener la información de paginación
    marco_paginacion = tk.Frame(window)
    marco_paginacion.pack(pady=10)

    # Crear una etiqueta para mostrar la página actual y el total de páginas
    etiqueta_pagina = tk.Label(marco_paginacion, text=f"{pagina_actual}/{total_paginas}")
    etiqueta_pagina.pack(side=tk.LEFT, padx=5)

    # Funciones de paginación
    def ir_a_pagina(pagina):
        global pagina_actual
        pagina_actual = pagina
        mostrar_registros(pagina_actual)
        etiqueta_pagina.config(text=f"{pagina_actual}/{total_paginas}")

    def pagina_anterior():
        if pagina_actual > 1:
            ir_a_pagina(pagina_actual - 1)
        else:
            ir_a_pagina(total_paginas)

    def pagina_siguiente():
        if pagina_actual < total_paginas:
            ir_a_pagina(pagina_actual + 1)
        else:
            ir_a_pagina(1)

    # Crear botones de paginación
    boton_anterior = tk.Button(marco_paginacion, text="Anterior", command=pagina_anterior)
    boton_anterior.pack(side=tk.LEFT, padx=5)

    boton_siguiente = tk.Button(marco_paginacion, text="Següent", command=pagina_siguiente)
    boton_siguiente.pack(side=tk.LEFT, padx=5)

    # Función para eliminar los documentos con count 0
    def eliminar_documentos():
        if not documentos_a_eliminar:
            messagebox.showinfo("Activitats descarregades", "No hi ha activitats a eliminar")
        else:
            ids_documentos_a_eliminar = [os.path.splitext(os.path.basename(documento))[0] for documento in documentos_a_eliminar]
            ids_a_eliminar = [registro["ID"] for registro in datos if registro["ID"] in ids_documentos_a_eliminar]

            for documento in documentos_a_eliminar:
                os.remove(documento)

            datos_actualizados = [registro for registro in datos if registro["ID"] not in ids_a_eliminar]

            with open(archivo_json, "w") as f:
                json.dump(datos_actualizados, f, indent=4)

            num_act = len(documentos_a_eliminar)
            if num_act == 1:
                pre = "S'ha"
                fin = ""
            else:
                pre = "S'han"
                fin = "s"

            messagebox.showinfo("Activitats descarregades", f"{pre} eliminat {num_act} activitat{fin}")
            cerrar_ventana()

    # Función para cerrar la ventana
    def cerrar_ventana():
        window.destroy()

    # Crear un marco para contener los botones
    marco_botones = tk.Frame(window)
    marco_botones.pack(pady=10)

    # Crear un botón para eliminar los documentos
    boton_eliminar = tk.Button(marco_botones, text="Eliminar activitats sense respostes", command=eliminar_documentos)
    boton_eliminar.grid(row=0, column=0, padx=5)

    # Crear un botón de cierre
    boton_cerrar = tk.Button(marco_botones, text="Tancar", command=cerrar_ventana)
    boton_cerrar.grid(row=0, column=1, padx=5)

    # Asociar la función de cambio de página a las flechas del teclado
    window.bind("<Left>", lambda event: pagina_anterior())
    window.bind("<Right>", lambda event: pagina_siguiente())

    # Ejecutar el bucle principal de la ventana
    window.mainloop()
else:
    mostrar_mensaje_sin_datos()
