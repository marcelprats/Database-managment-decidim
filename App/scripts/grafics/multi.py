import json
import os
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from tkinter import messagebox

# Obtén la ruta del archivo de configuración
config_file = "config.json"

# Comprueba si el archivo de configuración existe
if os.path.isfile(config_file):
    # Carga la configuración desde el archivo
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    exit()

# Directorio de los documentos con la relación ID-Título de las actividades
id_directory = os.path.join(config["jsons_descarregats"], "Desc")

# Directorio de los documentos con la información de usuarios y actividad
info_directory = config["jsons_descarregats"]

# Ruta del archivo JSON de configuraciones para GRÁFICOS
graph_config_file = os.path.join(config["jsons"], "grafics", "grconfig.json")

titol = "Generar gràfic"

# Cargar las configuraciones existentes desde el archivo JSON para GRÁFICOS
if os.path.isfile(graph_config_file):
    with open(graph_config_file, "r") as f:
        graph_configurations = json.load(f)
else:
    graph_configurations = {}

# Obtener la lista de archivos del directorio de ID
id_files = [os.path.join(id_directory, file) for file in os.listdir(id_directory) if file.endswith(".json")]

# Crear la lista de opciones con ID y título de las actividades
options = []
for file in id_files:
    with open(file, "r") as f:
        data = json.load(f)
        options.extend([(doc["ID"], doc["Title"]) for doc in data])

# Función para mostrar un mensaje de que no hay datos descargados
def mostrar_mensaje_sin_datos():
    messagebox.showinfo("Generar gràfics", "No hi ha dades descarregades.\nDescarrega els arxius primer.")

# Verificar si la lista de opciones está vacía
if not options:
    # Mostrar mensaje de actualización de datos
    mostrar_mensaje_sin_datos()
    
    # Salir del programa
    exit()

# Definir el diseño de la primera ventana
layout = [
    [sg.Text("Selecciona les activitats per generar el gràfic:")],
    [sg.Button("Seleccionar totes", key='-SELECT_ALL-'), sg.Button("Deseleccionar totes", key='-DESELECT_ALL-')],
    [sg.Listbox(options, size=(40, 10), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='-DOCUMENTS-')],
    [sg.Radio("Usuaris", "RADIO1", key='-USERS-', enable_events=True),
     sg.Radio("Respostes formulari", "RADIO1", key='-REGISTRATION_FORM-', enable_events=True)],
    [sg.Button("Siguiente", key='-SIGUIENTE-')],
]

# Definir la lista de tipos de gráfico
chart_types = ['Gràfic de barres', 'Gràfic de dispersió', 'Gràfic de línia', 'Gràfic circular']

# Crear la ventana de la primera interfaz
window = sg.Window(titol, layout)
# Bucle principal de la primera ventana
while True:

    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Tancar':
        window.close()
        break

    if event == '-SELECT_ALL-':
        window['-DOCUMENTS-'].update(set_to_index=list(range(len(options))))

    if event == '-DESELECT_ALL-':
        window['-DOCUMENTS-'].update(set_to_index=[])

    if event == '-SIGUIENTE-':
        selected_documents = values['-DOCUMENTS-']
        selected_option = None

        if values['-USERS-']:
            selected_option = 'users'
        elif values['-REGISTRATION_FORM-']:
            selected_option = 'registration_form'
     
        if not selected_documents:
            sg.popup("Selecciona una activitat", title=titol)
            continue
     
        if not selected_option:
            sg.popup("Selecciona Usuaris o Registre d'activitats", title=titol)
            continue

        if selected_option == 'users':

            email_counts = {}
            total_emails = 0
            for doc in selected_documents:
                doc_id = doc[0]
                file_path = os.path.join(info_directory, f"{doc_id}.json")
                with open(file_path, "r") as f:
                    data = json.load(f)
                    user_data_list = [data] if isinstance(data, dict) else data
                    for user_data in user_data_list:
                        user = user_data.get("user")
                        if user:
                            email = user.get("email")
                            if email:
                                email_counts[email] = email_counts.get(email, 0) + 1

            count_limit_layout = [
                [sg.Text("Número de correus a mostrar:")],
                [sg.Text("Utilitzar tots els correus"), sg.Checkbox("", key='-ALL_EMAILS-', enable_events=True, default=True)],
                [sg.Text("Introdueix número de correus a utilitzar:"), sg.Input(default_text="15", key='-COUNT_LIMIT-', disabled=True, size=(3, 1))],
                [sg.Text("Tipus de gràfic:"), sg.Combo(['Gràfic de barres', 'Gràfic de dispersió', 'Gràfic de línia', 'Gràfic circular'], default_value='Gràfic de barres', key='-CHART_TYPE-')],
                [sg.Checkbox("Afegir llegenda", key='-llegenda-')],
                [sg.Button("Aceptar", key='-ACCEPT_COUNT_LIMIT-')]
            ]

            count_limit_window = sg.Window("Seleccionar número de correus i tipus de gràfic", count_limit_layout)

            while True:
                count_limit_event, count_limit_values = count_limit_window.read()

                if count_limit_event == sg.WINDOW_CLOSED:
                    count_limit_window.close()
                    break                    
                plt.clf()
                if count_limit_event == '-ALL_EMAILS-':
                    if count_limit_values['-ALL_EMAILS-']:
                        count_limit_window['-COUNT_LIMIT-'].update(disabled=True)
                    else:
                        count_limit_window['-COUNT_LIMIT-'].update(disabled=False)

                if count_limit_event == '-ACCEPT_COUNT_LIMIT-':
                    count_limit = int(count_limit_values['-COUNT_LIMIT-'])
                    chart_type = count_limit_values['-CHART_TYPE-']
                    add_legend = count_limit_values['-llegenda-']  # Obtener el valor de la casilla de verificación
                    sorted_emails = sorted(email_counts.items(), key=lambda x: x[1], reverse=True)[:count_limit] if not count_limit_values['-ALL_EMAILS-'] else sorted(email_counts.items(), key=lambda x: x[1], reverse=True)
                    x = [email[0] for email in sorted_emails]
                    y = [email[1] for email in sorted_emails]
                    # Crear el gráfico en la posición (0.1, 0.1) dentro de la figura
                    ax = plt.axes([0.1, 0.1, 0.6, 0.7])  # Reducir el ancho para dejar espacio a la derecha

                    if chart_type == 'Gràfic de barres':
                        plt.xlabel("Correu electrònic")
                        plt.ylabel("Freqüència")
                        
                        if add_legend:
                            plt.bar(x, y, color=plt.cm.Paired(range(len(x))))
                            handles = [plt.Line2D([0], [0], marker='o', color='w', label=f'{label}', markersize=10, markerfacecolor=color)
                                    for label, color in zip(x, plt.cm.Paired(range(len(x))))]
                            legend = plt.legend(handles=handles, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                            frame = legend.get_frame()
                            frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                            plt.xticks([])
                        else:
                            plt.bar(x, y, color= plt.cm.Paired(range(len(x))))
                            plt.legend().set_visible(False)  # Ocultar la leyenda si no está activada
                            
                        plt.xticks(rotation=90)  # Ajustar la inclinación de los xticks

                    elif chart_type == 'Gràfic de dispersió':
                        plt.xlabel("Correu electrònic")
                        plt.ylabel("Freqüència")
                        
                        if add_legend:
                            plt.scatter(x, y, color=plt.cm.Paired(range(len(x))))
                            handles = [plt.Line2D([0], [0], marker='o', color='w', label=f'{label}', markersize=10, markerfacecolor=color)
                                    for label, color in zip(x, plt.cm.Paired(range(len(x))))]
                            legend = plt.legend(handles=handles, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                            frame = legend.get_frame()
                            frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                            plt.xticks([])
                        else:
                            plt.scatter(x, y, color= plt.cm.Paired(range(len(x))))
                            plt.legend().set_visible(False)  # Ocultar la leyenda si no está activada
                            
                        plt.xticks(rotation=90)  # Ajustar la inclinación de los xticks
                        
                        
                    elif chart_type == 'Gràfic de línia':
                        plt.xlabel("Correu electrònic")
                        plt.ylabel("Freqüència")

                        if add_legend:
                            plt.plot(x, y, color=plt.cm.Paired(range(len(x))))
                            handles = [plt.Line2D([0], [0], marker='o', color='w', label=f'{label}', markersize=10, markerfacecolor=color)
                                    for label, color in zip(x, plt.cm.Paired(range(len(x))))]
                            legend = plt.legend(handles=handles, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                            frame = legend.get_frame()
                            frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                            plt.xticks([])
                        else:
                            plt.plot(x, y, color= plt.cm.Paired(range(len(x))))
                            plt.legend().set_visible(False)  # Ocultar la leyenda si no está activada
                            
                        plt.xticks(rotation=90)  # Ajustar la inclinación de los xticks
        


                    elif chart_type == 'Gràfic circular':
                        total_emails = max(1, sum(email_counts.values()))
                        plt.xlabel("")
                        plt.ylabel("")
                        percentages = [count / total_emails * 100 for count in y]
                    
                        if add_legend:
                            # Agregar la leyenda al gráfico circular
                            handles = [plt.Line2D([0], [0], marker='o', color='w', label=f'{label}', markersize=10, markerfacecolor=color)
                                    for label, color in zip(x, plt.cm.Paired(range(len(x))))]
                            legend = plt.legend(handles=handles, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                            frame = legend.get_frame()
                            frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                            wedges, texts, autotexts = plt.pie(y, labels=[''] * len(x), autopct='%1.1f%%', colors=plt.cm.Paired(range(len(x))))
                        else:
                            plt.legend().set_visible(False)  # Ocultar la leyenda si no está activada
                            wedges, texts, autotexts = plt.pie(y, labels=x, autopct='%1.1f%%', colors=plt.cm.Paired(range(len(x))))
                    
                    # Mostramos título y subtítulo siempre, independientemente de add_legend
                    if count_limit_values['-ALL_EMAILS-']:
                        name = f"{len(email_counts)}"
                    else:
                        name = f"{count_limit}"

                    plt.suptitle(f"{chart_type} de {name} correus electrònics", fontsize=12, fontweight='bold')
                    activity_id = [doc[0] for doc in selected_documents]
                    plt.title(f"Activitats seleccionades: {len(activity_id)}", fontsize=9, loc='center', x=0.5, y=1.02)
                    plt.xticks(rotation=90)  # Ajustar la inclinación de los xticks

                    plt.show()


          
        if selected_option == 'registration_form':
            selected_documents = values['-DOCUMENTS-']

            if not selected_documents:
                sg.popup("Seleccionar almenys una activitat", title=titol)
                continue

            # Obtener las variables disponibles
            available_variables = set()
            for doc in selected_documents:
                doc_id = doc[0]
                file_path = os.path.join(info_directory, f"{doc_id}.json")
                with open(file_path, "r") as f:
                    data = json.load(f)
                    user_data_list = [data] if isinstance(data, dict) else data
                    for user_data in user_data_list:
                        answers = user_data.get("registration_form_answers")
                        if answers:
                            available_variables.update(answers.keys())

            variable_layout = [
                [sg.Text("Selecciona la informació pel gràfic:"),sg.Button("Deseleccionar", key='-DESELECCIONAR-')],
                [sg.Listbox(sorted(available_variables), size=(40, 5), select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, key='-VARIABLE-', enable_events=True)],
                [sg.Text("Escull una configuració:"), sg.Combo(sorted(list(graph_configurations.keys())), default_value='', key='-PREDEFINED_OPTION-', enable_events=True),sg.Button("Editar configuració", key='-EDIT_CONFIGURATION-')],
                [sg.Text("O crea una personalitzada:"), sg.Button("Crear configuració", key='-CUSTOM_CONFIGURATION-')],
                [sg.Button("Generar gràfic", key='-GENERATE_GRAPH-')],
            ]

            variable_window = sg.Window("Seleccionar la configuració", variable_layout)

            while True:
                var_event, var_values = variable_window.read()

                if var_event == sg.WINDOW_CLOSED:
                    break

                if var_event == '-DESELECCIONAR-':
                    variable_window['-VARIABLE-'].update(set_to_index=[])
                
                if var_event == '-GENERATE_GRAPH-':
                    selected_variable = var_values['-VARIABLE-'][0] if var_values['-VARIABLE-'] else None
                    selected_option = var_values['-PREDEFINED_OPTION-']

                    if not selected_variable:
                        sg.popup("Selecciona la informació a utilitzar.", title=titol)
                        continue

                    variable_counts = {}
                    for doc in selected_documents:
                        doc_id = doc[0]
                        file_path = os.path.join(info_directory, f"{doc_id}.json")
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            user_data_list = [data] if isinstance(data, dict) else data
                            for user_data in user_data_list:
                                answers = user_data.get("registration_form_answers")
                                if answers and selected_variable in answers:
                                    values = answers[selected_variable]
                                    if isinstance(values, list):
                                        for value in values:
                                            variable_counts[value] = variable_counts.get(value, 0) + 1
                                    else:
                                        variable_counts[values] = variable_counts.get(values, 0) + 1
      
                    if variable_counts:
                        # Generar el gráfico de la variable seleccionada
                        x = list(variable_counts.keys())
                        y = list(variable_counts.values())

                        # Obtener los datos de la configuración seleccionada o la predeterminada
                        selected_option = var_values['-PREDEFINED_OPTION-']
                        if selected_option and selected_option in graph_configurations:
                            configuration_data = graph_configurations[selected_option]
                        
                            # Crear una nueva figura para el gráfico
                            plt.figure(figsize=[int(size) for size in configuration_data["size"].split('x')])

                            # Configurar el estilo del gráfico y colores
                            colors = plt.cm.Paired(range(len(x)))

                            # Mostrar el título centrado en la parte superior
                            plt.suptitle(configuration_data["title"], fontsize=16, fontweight='bold')

                            # Crear el gráfico en la posición (0.1, 0.1) dentro de la figura
                            ax = plt.axes([0.1, 0.1, 0.6, 0.7])  # Reducir el ancho para dejar espacio a la derecha

                            if configuration_data["chart_type"] == 'Gràfic de barres':
                                bars = ax.bar(x, y, color=colors)
                                # Agregar el valor de la suma encima de cada barra
                                for bar, value in zip(bars, y):
                                    ax.annotate(str(value), (bar.get_x() + bar.get_width() / 2, value),
                                                ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')
                                    
                                if configuration_data["legend"]:
                                    # Crear la leyenda basada en el objeto BarContainer y las etiquetas
                                    legend = ax.legend(bars, x, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                                    frame = legend.get_frame()
                                    frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                                    ax.set_xticks([])  # Eliminar las etiquetas del eje x si la leyenda está activada
                                else:
                                    ax.set_xticks(range(len(x)))  # Establecer ubicaciones de las etiquetas en el eje x
                                    ax.set_xticklabels(x,rotation=90)  # Establecer las etiquetas en el eje x

        
                            elif configuration_data["chart_type"] == 'Gràfic de dispersió':
                                scatter = ax.scatter(x, y, color=colors, s=100)                                # Agregar el valor de la suma en el centro de cada punto
                                for point_x, point_y in zip(x, y):
                                    ax.annotate(str(point_y), (point_x, point_y),
                                                ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')
           
                                if configuration_data["legend"]:
                                    handles = [plt.Line2D([0], [0], marker='o', color='w', label=f'{label}', markersize=10, markerfacecolor=color)
                                            for label, value, color in zip(x, y, colors)]
                                    legend = ax.legend(handles=handles, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                                    frame = legend.get_frame()
                                    frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                                    ax.set_xticks([])  # Eliminar las etiquetas del eje x si la leyenda está activada
                                else:
                                    ax.set_xticks(range(len(x)))  # Establecer ubicaciones de las etiquetas en el eje x
                                    ax.set_xticklabels(x,rotation=90)  # Establecer las etiquetas en el eje x
                            
                            elif configuration_data["chart_type"] == 'Gràfic de línia':
                                ax.plot(x, y, color=colors[0], marker='o', linestyle='-', linewidth=2)
                                
                                if configuration_data["legend"]:
                                    handles = [plt.Line2D([0], [0], marker='o', color='w', label=f'{label}', markersize=10, markerfacecolor=color)
                                            for label, color in zip(x, colors)]
                                    legend = ax.legend(handles=handles, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                                    frame = legend.get_frame()
                                    frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                                    ax.set_xticks([])  # Eliminar las etiquetas del eje x si la leyenda está activada
                                else:
                                    ax.set_xticks(range(len(x)))  # Establecer ubicaciones de las etiquetas en el eje x
                                    ax.set_xticklabels(x, rotation=90)  # Establecer las etiquetas en el eje x
                                
                                # Agregar el valor de cada punto encima de la línea
                                for point_x, point_y in zip(x, y):
                                    ax.annotate(str(point_y), (point_x, point_y),
                                                ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

                            elif configuration_data["chart_type"] == 'Gràfic circular':
                                wedges, texts, autotexts = ax.pie(y, labels=None, autopct='%1.1f%%', colors=colors)
                                
                                if configuration_data["legend"]:
                                    handles = [plt.Line2D([0], [0], marker='o', color='w', label=f'{label}', markersize=10, markerfacecolor=color)
                                            for label, color in zip(x, colors)]
                                    legend = ax.legend(handles=handles, title='Llegenda', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                                    frame = legend.get_frame()
                                    frame.set_facecolor('0.95')  # Cambiar el color de fondo de la leyenda
                                else:
                                    ax.legend().set_visible(False)  # Ocultar la leyenda si no está activada
                                    ax.pie(y, labels=x, autopct='%1.1f%%', colors=colors)  # Volver a mostrar las etiquetas en el gráfico circular

                            if configuration_data["show_title"]:
                                plt.suptitle(configuration_data["title"], fontsize=16, fontweight='bold')
                            else:
                                plt.suptitle("")  # Título en blanco si show_title es False

                            if configuration_data["show_subtitle"]:
                                plt.title(selected_variable, fontsize=14, fontweight='normal')
                            else:
                                plt.title("")  # Subtítulo en blanco si show_subtitle es False

                            # Agregar el total de respuestas debajo del título centrado
                            total_responses = sum(y)

                            if configuration_data["show_total"]:
                                plt.text(0.5, 0.88, f"Número de respostes: {total_responses}", ha='center', fontsize=12, transform=plt.gcf().transFigure)
                            else:
                                plt.text(0.5, 0.88,"",ha='center', fontsize=12, transform=plt.gcf().transFigure)  # En blanco si show_total es False

                            # Ajustar los márgenes y mostrar el gráfico
                            plt.tight_layout()
                            plt.show()
                        else:
                            sg.popup("Selecciona una configuració existent o crean una personalizada.", title=titol)
                            continue
                    else:
                        sg.popup("L'activitat no conté dades per generar el gràfic.", title="Dades insuficients")
                        continue

                if var_event == '-CUSTOM_CONFIGURATION-':
                    chart_types = ['Gràfic de barres', 'Gràfic de dispersió', 'Gràfic de línia', 'Gràfic circular']

                    custom_layout = [
                        [sg.Text("Nom de la configuració:"), sg.Input(key='-NAME-')],
                        [sg.Text("Títol del gràfic:"), sg.Input(key='-TITLE-'), sg.Checkbox("Mostrar", default=True, key='-SHOW_TITLE-')],
                        [sg.Checkbox("Mostrar nom de l'activitat", default=True, key='-SHOW_SUBTITLE-'),sg.Checkbox("Mostrar número de respostes", default=True, key='-SHOW_TOTAL-')],
                        [sg.Text("Mida (ample x alçada):"), sg.Input(default_text="6x4", key='-SIZE-')],
                        [sg.Text("Tipus de gràfic:"), sg.Combo(chart_types, default_value='', key='-CHART_TYPE-', enable_events=True)],
                        [sg.Checkbox("Afegir llegenda", key='-LEGEND-')],
                        [sg.Button("Guardar", key='-SAVE_CUSTOM-')]
                    ]

                    custom_window = sg.Window("Crear configuració personalitzada", custom_layout)                  

                    while True:
                        custom_event, custom_values = custom_window.read()

                        if custom_event == sg.WINDOW_CLOSED:
                            custom_window.close()
                            break
                        
                        if custom_event == '-SAVE_CUSTOM-':
                            custom_name = custom_values['-NAME-']
                            custom_title = custom_values['-TITLE-']
                            show_title = custom_values['-SHOW_TITLE-']
                            subtitle = ""
                            show_subtitle = custom_values['-SHOW_SUBTITLE-']
                            show_total = custom_values['-SHOW_TOTAL-']
                            size = custom_values['-SIZE-']
                            chart_type = custom_values['-CHART_TYPE-']
                            legend = custom_values['-LEGEND-']

                            if not custom_name or not custom_title or not size or not chart_type:
                                sg.popup("Per crear una configuració personalitzada, el nom, el títol, la mida i el tipus de gràfic son obligatoris", title="Canódrom")
                            else:
                                graph_configurations[custom_name] = {
                                    "title": custom_title,
                                    "show_title": show_title,
                                    "subtitle": subtitle,
                                    "show_subtitle": show_subtitle,
                                    "show_total": show_total,
                                    "size": size,
                                    "chart_type": chart_type,
                                    "legend": legend
                                }

                                with open(graph_config_file, "w") as f:
                                    json.dump(graph_configurations, f, indent=4)

                                sg.popup(f"Configuració personalitzada '{custom_name}' guardada amb èxit", title=titol)
                                # Actualizar la lista de opciones sin el nombre eliminado
                                variable_window['-PREDEFINED_OPTION-'].update(values=sorted(list(graph_configurations.keys())))
                                variable_window['-PREDEFINED_OPTION-'].update(value=custom_name)
                            custom_window.close()

                if var_event == '-EDIT_CONFIGURATION-':
                    selected_option = var_values['-PREDEFINED_OPTION-']

                    if not selected_option:
                        sg.popup("Selecciona una configuració predefinida per editar.", title="Configuració no seleccionada")
                        continue

                    if selected_option not in graph_configurations:
                        sg.popup("La configuració seleccionada no existeix.", title="Configuració no trobada")
                        continue

                    configuration_data = graph_configurations[selected_option]

                    # Crear la ventana de edición de configuración
                    edit_layout = [
                        [sg.Text("Nom de la configuració:"), sg.Input(default_text=selected_option, key='-NAME-')],
                        [sg.Text("Títol del gràfic:"), sg.Input(default_text=configuration_data.get('title', ''), key='-TITLE-'), sg.Checkbox("Mostrar", default=configuration_data.get('show_title', False), key='-SHOW_TITLE-')],
                        [sg.Checkbox("Mostrar nom de la informació seleccionada",  default=configuration_data.get('show_subtitle', False), key='-SHOW_SUBTITLE-'),sg.Checkbox("Mostrar número de respostes",  default=configuration_data.get('show_total', False), key='-SHOW_TOTAL-')],
                        [sg.Text("Mida (ample x alçada):"), sg.Input(default_text=configuration_data.get('size', ''), key='-SIZE-')],
                        [sg.Text("Tipus de gràfic:"), sg.Combo(chart_types, default_value=configuration_data.get('chart_type', ''), key='-CHART_TYPE-', enable_events=True)],
                        [sg.Checkbox("Afegir llegenda", default=configuration_data.get('legend', False), key='-LEGEND-')],
                        [sg.Button("Guardar canvis", key='-SAVE_CHANGES-'), sg.Button("Eliminar configuració", key='-DELETE_CONFIGURATION-', button_color=('white', 'red'))]
                    ]

                    edit_window = sg.Window("Editar configuració", edit_layout)

                    while True:
                        edit_event, edit_values = edit_window.read()

                        if edit_event == sg.WINDOW_CLOSED:
                            edit_window.close()
                            break

                        if edit_event == '-SAVE_CHANGES-':
                            configuration_name = edit_values['-NAME-']
                            title = edit_values['-TITLE-']
                            show_title = edit_values['-SHOW_TITLE-']
                            subtitle = ""
                            show_subtitle = edit_values['-SHOW_SUBTITLE-']
                            show_total = edit_values['-SHOW_TOTAL-']
                            size = edit_values['-SIZE-']
                            chart_type = edit_values['-CHART_TYPE-']
                            legend = edit_values['-LEGEND-']

                            if not title or not size or not chart_type:
                                sg.popup("Per crear una configuració personalitzada, el títol, la mida i el tipus de gràfic son obligatoris", title="Canódrom")
                            else:
                                # Eliminar la configuración anterior si el nombre ha cambiado
                                if selected_option != configuration_name and selected_option in graph_configurations:
                                    del graph_configurations[selected_option]

                                graph_configurations[configuration_name] = {
                                    "title": title,
                                    "show_title": show_title,
                                    "subtitle": subtitle,
                                    "show_subtitle": show_subtitle,
                                    "show_total": show_total,
                                    "size": size,
                                    "chart_type": chart_type,
                                    "legend": legend
                                }

                                with open(graph_config_file, "w") as f:
                                    json.dump(graph_configurations, f, indent=4)

                                sg.popup(f"Configuració '{configuration_name}' actualitzada amb èxit", title="Canódrom")

                                # Actualizar la lista de opciones con los nombres de las configuraciones
                                variable_window['-PREDEFINED_OPTION-'].update(values=sorted(list(graph_configurations.keys())))
                                variable_window['-PREDEFINED_OPTION-'].update(value=configuration_name)

                            edit_window.close()

                        if edit_event == '-DELETE_CONFIGURATION-':
                            confirm_delete = sg.popup_yes_no(f"Estàs segur que vols eliminar la configuració '{selected_option}'?", title="Eliminar configuració")

                            if confirm_delete == 'Yes':
                                del graph_configurations[selected_option]
                                with open(graph_config_file, "w") as f:
                                    json.dump(graph_configurations, f, indent=4)
                                sg.popup(f"Configuració '{selected_option}' eliminada amb èxit", title="Canódrom")

                                # Actualizar la lista de opciones sin el nombre eliminado
                                variable_window['-PREDEFINED_OPTION-'].update(values=sorted(list(graph_configurations.keys())))
                            else:
                                continue
                            edit_window.close()

                if var_event == '-PREDEFINED_OPTION-':
                    selected_option = var_values['-PREDEFINED_OPTION-']

                    if selected_option and selected_option in graph_configurations:
                        configuration_data = graph_configurations[selected_option]

                        title = configuration_data.get('title', '')
                        show_title = configuration_data.get('show_title', False)
                        subtitle = configuration_data.get('subtitle', '')
                        show_subtitle = configuration_data.get('show_subtitle', False)
                        size = configuration_data.get('size', '')
                        chart_type = configuration_data.get('chart_type', '')
                        legend = configuration_data.get('legend', False)
                        space =  "                         "

                        if show_title is True:
                            show_title = "Mostrar"
                        else:
                            show_title = "Ocultar"

                        if legend is True:
                            legend = "Mostrar"
                        else:
                            legend = "Ocultar"


                        # Crear el diseño de la ventana con la información en dos columnas
                        layout = [
                            [sg.Column([[sg.Text(f'{space}{selected_option}', font=('Arial', 12, 'bold'), justification='center')]], element_justification='center')],
                            [sg.Column([[sg.Text('Títol:', font=('Arial', 11, 'bold'))],
                                        [sg.Text("Mostrar titol:", font=('Arial', 11, 'bold'))],
                                        [sg.Text('Mida:', font=('Arial', 11, 'bold'))],
                                        [sg.Text('Tipus de gràfic:', font=('Arial', 11, 'bold'))],
                                        [sg.Text('Llegenda:', font=('Arial', 11, 'bold'))]], element_justification='right'),
                            sg.Column([[sg.Text(title, font=('Arial', 11))],
                                    [sg.Text(str(show_title), font=('Arial', 11))],
                                    [sg.Text(size, font=('Arial', 11))],
                                    [sg.Text(chart_type, font=('Arial', 11))],
                                    [sg.Text(str(legend), font=('Arial', 11))]], element_justification='left')],
                            [sg.Button('Tancar')]
                        ]

                        # Crear la ventana
                        window = sg.Window('Informació de la configuració', layout)

                        # Bucle principal de la ventana
                        while True:
                            event, values = window.read()

                            if event == sg.WINDOW_CLOSED or event == 'Tancar':
                                window.close()
                                break


window.close()


