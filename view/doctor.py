# view/doctor.py
"""Dashboard e layout per i medici"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date

def create_header_with_logo_and_logout(username):
    """Crea header con logo e logout"""
    return [
        html.Img(
            src="/assets/health.png",
            style={
                "position": "fixed", "top": "20px", "right": "20px",
                "width": "150px", "height": "auto", "z-index": "1000"
            }
        ),
        dcc.Link("Logout", 
            href="/logout", 
            style={
                "position": "fixed", "top": "20px", "left": "20px",
                "color": "white", "text-decoration": "none", "font-weight": "600",
                "font-size": "16px", "background": "rgba(16, 185, 129, 1)",
                "padding": "10px 20px", "border-radius": "25px",
                "backdrop-filter": "blur(10px)", "border": "1px solid rgba(255, 255, 255, 0.2)",
                "z-index": "1000"
            }
        ),
        dbc.Row([
            dbc.Col([
                html.H2(f"Benvenuto/a Dr. {username}", 
                    className="gradient-title text-center",
                    style={
                        "margin-top": "20px", "margin-bottom": "30px",
                        "color": "white", "text-shadow": "2px 2px 4px rgba(0,0,0,0.3)"
                    })
            ], width=12)
        ])
    ]

def create_dashboard_button(icon, text, btn_id, color="primary"):
    """Crea un bottone del dashboard"""
    return dbc.Button(
        [
            html.Img(src=f"/assets/{icon}.png", 
                style={"width": "35px", "height": "35px", "margin-right": "8px"}),
            text
        ],
        id=btn_id,
        className=f"btn-{color} w-100",
        size="lg"
    )

def create_back_to_menu_button(text="Torna al Menu Principale", color="info"):
    """Crea bottone per tornare al menu"""
    return dbc.Button(
        text,
        id="btn-torna-menu-principale" if "Principale" in text else "btn-torna-menu-terapie",
        color=color,
        size="sm" if color != "info" else "lg",
        className="btn-info" if color == "info" else ""
    )

def create_patient_selector(pazienti, dropdown_id, label="Seleziona Paziente *"):
    """Crea selector per pazienti"""
    pazienti_options = [
        {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
        for p in pazienti
    ]
    
    return dbc.Row([
        dbc.Col([
            dbc.Label(label, className="form-label"),
            dbc.Select(
                id=dropdown_id,
                options=pazienti_options,
                placeholder="Seleziona il paziente...",
                className="form-control"
            )
        ], width=12)
    ], className="mb-3")

def create_no_patients_alert():
    """Crea alert per nessun paziente"""
    return dbc.Alert([
        html.H5("Nessun paziente trovato", className="alert-heading"),
        html.P("Non hai ancora pazienti assegnati. Contatta l'amministratore per associare pazienti al tuo profilo."),
        html.Hr(),
        create_back_to_menu_button("Torna al Menu Terapie", "warning")
    ], color="warning")

def create_form_input(input_id, label, placeholder="", input_type="text", value="", width=12, md=None, **kwargs):
    """Crea input form generico"""
    input_kwargs = {k: v for k, v in kwargs.items() if k not in ['width', 'md']}
    
    return dbc.Col([
        dbc.Label(label, className="form-label"),
        dbc.Input(
            id=input_id,
            type=input_type,
            placeholder=placeholder,
            value=value,
            className="form-control",
            **input_kwargs
        )
    ], width=width, md=md)

def create_textarea(textarea_id, label, placeholder="", value="", rows=3, help_text=""):
    """Crea textarea generico"""
    elements = [
        dbc.Label(label, className="form-label"),
        dbc.Textarea(
            id=textarea_id,
            placeholder=placeholder,
            value=value,
            rows=rows,
            className="form-control"
        )
    ]
    
    if help_text:
        elements.append(dbc.FormText(help_text, className="text-muted"))
    
    return dbc.Row([dbc.Col(elements, width=12)], className="mb-3")

def create_success_alert(title, content, buttons):
    """Crea alert di successo generico"""
    return dbc.Alert(
        [
            html.H5(title, className="alert-heading"),
            *content,
            html.Hr(),
            *buttons
        ], 
        color="success", 
        dismissable=True
    )

def get_doctor_dashboard(username):
    """Dashboard per i medici"""
    header_elements = create_header_with_logo_and_logout(username)
    
    return dbc.Container([
        *header_elements,
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.Img(src="/assets/doctor.png", 
                                style={"width": "40px", "height": "40px", "margin-right": "10px"}),
                            html.H4("Area Medico", className="mb-0 doctor-title", style={"display": "inline-block"})
                        ])
                    ]),
                    dbc.CardBody([
                        html.P("Benvenuto nella tua area professionale. Qui puoi gestire i tuoi pazienti e le terapie.", 
                            className="card-text mb-4"),
                        
                        # Bottoni dashboard
                        dbc.Row([
                            dbc.Col([create_dashboard_button("terapia", "Gestisci Terapie", "btn-gestisci-terapie")], 
                                width=12, md=6, className="mb-3"),
                            dbc.Col([create_dashboard_button("dati", "Dati Pazienti", "btn-dati-paziente", "success")], 
                                width=12, md=6, className="mb-3")
                        ]),
                        
                        dbc.Row([
                            dbc.Col([create_dashboard_button("segui", "Segui un nuovo paziente", "btn-segui-pazienti", "success")], 
                                width=12, md=6, className="mb-3"),
                            dbc.Col([create_dashboard_button("grafico", "Andamenti glicemici", "btn-statistiche", "success")], 
                                width=12, md=6, className="mb-3")
                        ]),
                        
                        html.Div(id="doctor-feedback", className="mt-3")
                    ])
                ]),
                
                html.Div(id="doctor-content", className="mt-3", children=get_doctor_welcome_content())
                
            ], width=8)
        ], justify="center", className="mt-4")
    ], fluid=True, className="main-container")

def get_doctor_welcome_content():
    """Restituisce il contenuto di benvenuto per la dashboard medico"""
    return [
        dbc.Alert([
            html.H4([
                html.Img(src="/assets/valigia.gif", style={"width": "50px", "height": "50px", "marginRight": "8px"}),
                "Benvenuto/a nella Dashboard Medico!"
            ], className="alert-heading"),
            html.P("Seleziona una delle opzioni sopra per iniziare a gestire i tuoi pazienti."),
            html.Hr(),
            html.P("🔹 Gestisci le terapie farmacologiche dei tuoi pazienti (assegnando una terapia seguirai in automatico un paziente)"),
            html.P("🔹 Visualizza i dati clinici e modifica quelli dei tuoi pazienti"),
            html.P("🔹 Inizia a seguire nuovi pazienti o diventa medico di riferimento"),
            html.P("🔹 Analizza gli andamenti glicemici e le statistiche")
        ], color="light", className="mb-4")
    ]

def get_terapie_menu():
    """Menu delle opzioni per gestire le terapie"""
    menu_items = [
        ("Assegna Nuova Terapia", "btn-assegna-terapia", "primary", "Assegna una nuova terapia farmacologica a un paziente"),
        ("Modifica Terapia", "btn-modifica-terapia", "success", "Modifica una terapia esistente"),
        ("Elimina Terapia", "btn-elimina-terapia", "red", "Rimuovi una terapia non piÃ¹ necessaria")
    ]
    
    menu_buttons = []
    for title, btn_id, color, description in menu_items:
        menu_buttons.extend([
            dbc.Row([
                dbc.Col([
                    dbc.Button(title, id=btn_id, className=f"btn-{color} w-100 mb-3", size="lg"),
                    html.Small(description, className="text-muted d-block text-center")
                ], width=12, className="mb-4")
            ])
        ])
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Gestione Terapie", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            html.P("Seleziona l'azione che desideri eseguire:", className="card-text mb-4"),
            *menu_buttons,
            html.Hr(),
            create_back_to_menu_button()
        ])
    ], className="mt-3")

def get_assegna_terapia_form(pazienti):
    """Form per assegnare una terapia a un paziente"""
    if not pazienti:
        return dbc.Card([
            dbc.CardHeader([html.H5("Assegnazione Terapia", className="mb-0 text-primary")]),
            dbc.CardBody([create_no_patients_alert()])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([html.H5("Assegnazione Nuova Terapia", className="mb-0 text-primary")]),
        dbc.CardBody([
            create_patient_selector(pazienti, "select-paziente-terapia"),
            
            # Nome farmaco e dosaggio
            dbc.Row([
                create_form_input("input-nome-farmaco-terapia", "Nome del farmaco *", 
                    "es. Metformina, Insulina...", width=12, md=6),
                create_form_input("input-dosaggio-terapia", "Dosaggio per assunzione *", 
                    "es. 500mg, 1 compressa, 10 UI...", width=12, md=6)
            ], className="mb-3"),
            
            # Assunzioni e indicazioni
            dbc.Row([
                create_form_input("input-assunzioni-giornaliere", "Numero di assunzioni giornaliere *", 
                    "es. 2", "number", min=1, max=10, step=1, width=12, md=6),
                dbc.Col([
                    dbc.Label("Indicazioni", className="form-label"),
                    dbc.Select(
                        id="select-indicazioni-terapia",
                        options=[
                            {"label": "Prima dei pasti", "value": "prima_pasti"},
                            {"label": "Dopo i pasti", "value": "dopo_pasti"},
                            {"label": "Lontano dai pasti", "value": "lontano_pasti"},
                            {"label": "Al mattino", "value": "mattino"},
                            {"label": "Alla sera", "value": "sera"},
                            {"label": "Secondo necessitÃ ", "value": "secondo_necessita"}
                        ],
                        placeholder="Seleziona indicazioni...",
                        className="form-control"
                    )
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Date
            dbc.Row([
                create_form_input("input-data-inizio-terapia", "Data inizio terapia *", 
                    "", "date", date.today().strftime('%Y-%m-%d'), width=12, md=6),
                create_form_input("input-data-fine-terapia", "Data fine terapia (se applicabile)", 
                    "", "date", width=12, md=6)
            ], className="mb-3"),
            
            create_textarea("textarea-indicazioni-terapia", "Indicazioni aggiuntive", 
                "es. Assumere con abbondante acqua, non assumere se glicemia < 80 mg/dL..."),
            
            create_textarea("textarea-note-terapia", "Note (opzionale)", 
                "Eventuali note aggiuntive per il paziente...", rows=2),
            
            # Pulsanti
            html.Div([
                dbc.Button("Assegna Terapia", id="btn-salva-terapia", color="success", size="lg", className="me-2"),
                create_back_to_menu_button("Torna al Menu Terapie", "info")
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_modifica_terapia_form(pazienti):
    """Form per modificare una terapia esistente"""
    if not pazienti:
        return dbc.Card([
            dbc.CardHeader([html.H5("Modifica Terapia", className="mb-0 text-primary")]),
            dbc.CardBody([create_no_patients_alert()])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([html.H5("Modifica Terapia Esistente", className="mb-0 text-primary")]),
        dbc.CardBody([
            create_patient_selector(pazienti, "select-paziente-modifica"),
            dbc.FormText("Seleziona un paziente per visualizzare le sue terapie attive", className="text-muted mb-3"),
            
            html.Div(id="terapie-paziente-list", className="mt-3"),
            
            html.Div([create_back_to_menu_button("Torna al Menu Terapie", "info")], 
                className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_elimina_terapia_form(pazienti):
    """Form per eliminare una terapia esistente"""
    if not pazienti:
        return dbc.Card([
            dbc.CardHeader([html.H5("Elimina Terapia", className="mb-0 text-primary")]),
            dbc.CardBody([create_no_patients_alert()])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([html.H5("Elimina Terapia", className="mb-0 text-primary")]),
        dbc.CardBody([
            dbc.Alert([
                html.Strong("âš ï¸ Attenzione: "),
                "L'eliminazione di una terapia Ã¨ un'azione irreversibile. Assicurati di voler procedere."
            ], color="warning", className="mb-4"),
            
            create_patient_selector(pazienti, "select-paziente-elimina"),
            dbc.FormText("Seleziona un paziente per visualizzare le sue terapie attive", className="text-muted mb-3"),
            
            html.Div(id="terapie-paziente-elimina-list", className="mt-3"),
            
            html.Div([create_back_to_menu_button("Torna al Menu Terapie", "info")], 
                className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def create_terapia_info_display(terapia):
    """Crea display info terapia"""
    data_inizio_str = terapia.data_inizio.strftime('%d/%m/%Y') if terapia.data_inizio else "Non specificata"
    data_fine_str = terapia.data_fine.strftime('%d/%m/%Y') if terapia.data_fine else "Continuativa"
    modificata_info = f" (Modificata da: {terapia.modificata})" if terapia.modificata else ""
    
    return html.P([
        html.Strong("Dosaggio: "), terapia.dosaggio_per_assunzione, html.Br(),
        html.Strong("Assunzioni giornaliere: "), str(terapia.assunzioni_giornaliere), html.Br(),
        html.Strong("Dal: "), data_inizio_str, 
        html.Strong(" al: ") if terapia.data_fine else html.Strong(" - "), data_fine_str, html.Br(),
        html.Strong("Prescritto da: "), terapia.medico_nome, modificata_info
    ], className="card-text small")

def create_terapia_card(terapia, button_config, border_color="#28a745"):
    """Crea card generica per terapia"""
    composite_key = f"{terapia.medico_nome}|{terapia.paziente.username}|{terapia.nome_farmaco}|{terapia.data_inizio.strftime('%Y-%m-%d') if terapia.data_inizio else 'None'}"
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(f"{terapia.nome_farmaco}", className="card-title text-primary"),
                    create_terapia_info_display(terapia),
                    
                    # Indicazioni e note se presenti
                    html.P([html.Strong("Indicazioni: "), terapia.indicazioni or "Nessuna indicazione specifica"], 
                        className="card-text small text-muted") if terapia.indicazioni else html.Div(),
                    html.P([html.Strong("Note: "), terapia.note or "Nessuna nota"], 
                        className="card-text small text-muted") if terapia.note else html.Div(),
                ], width=8),
                
                dbc.Col([
                    dbc.Button(
                        [html.I(className=f"fas fa-{button_config['icon']} me-1"), button_config['text']],
                        id={'type': button_config['id_type'], 'index': composite_key},
                        className=button_config.get('className', 'w-100'),
                        color=button_config.get('color', 'primary'),
                        size="sm"
                    )
                ], width=4, className="d-flex align-items-center")
            ])
        ])
    ], className="mb-2", style={"border-left": f"4px solid {border_color}"})

def get_terapie_list_for_edit(terapie, paziente):
    """Lista delle terapie del paziente per la modifica"""
    button_config = {
        'icon': 'edit',
        'text': 'Modifica',
        'id_type': 'btn-modifica-terapia-specifica',
        'className': 'btn-modify-medical w-100'
    }
    
    terapie_cards = [create_terapia_card(t, button_config) for t in terapie]
    
    return html.Div([
        html.Hr(),
        html.H6(f"Terapie di {paziente.name} {paziente.surname}:", className="text-primary mb-3"),
        html.Div(terapie_cards)
    ])

def get_terapie_list_for_delete(terapie, paziente):
    """Lista delle terapie del paziente per l'eliminazione"""
    button_config = {
        'icon': 'trash',
        'text': 'Elimina',
        'id_type': 'btn-elimina-terapia-specifica',
        'color': 'danger'
    }
    
    terapie_cards = [create_terapia_card(t, button_config, "#dc3545") for t in terapie]
    
    return html.Div([
        html.Hr(),
        dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Strong("Attenzione: "),
            "Stai per eliminare una terapia. Questa azione è¨ irreversibile!"
        ], color="warning", className="mb-3"),
        html.H6(f"Terapie di {paziente.name} {paziente.surname}:", className="text-danger mb-3"),
        html.P("Seleziona la terapia da eliminare:", className="text-muted mb-3"),
        html.Div(terapie_cards)
    ])

def create_terapia_success_buttons(btn1_config, btn2_config=None):
    """Crea bottoni per messaggi di successo terapie"""
    buttons = []
    if btn2_config:
        buttons.append(
            dbc.Row([
                dbc.Col([
                    dbc.Button(btn1_config['text'], id=btn1_config['id'], 
                        color=btn1_config['color'], size="sm", className="w-100")
                ], width=6),
                dbc.Col([
                    dbc.Button(btn2_config['text'], id=btn2_config['id'], 
                        color=btn2_config['color'], size="lg", className="btn-info w-100")
                ], width=6)
            ], className="g-3")
        )
    else:
        buttons.append(
            dbc.Row([
                dbc.Col([
                    dbc.Button(btn1_config['text'], id=btn1_config['id'], 
                        color=btn1_config['color'], size="lg", className="w-100")
                ], width=12)
            ])
        )
    
    return buttons

def get_terapia_success_message(paziente_nome, nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine=None):
    """Messaggio di successo dopo assegnazione terapia"""
    content = [
        html.P(f"Paziente: {paziente_nome}"),
        html.P(f"Farmaco: {nome_farmaco}"),
        html.P(f"Dosaggio: {dosaggio}"),
        html.P(f"Assunzioni giornaliere: {assunzioni_giornaliere}"),
        html.P(f"Data inizio: {data_inizio.strftime('%d/%m/%Y')}"),
        html.P(f"Data fine: {data_fine.strftime('%d/%m/%Y')}" if data_fine else "Durata: Terapia continuativa")
    ]
    
    btn1 = {'text': "Assegna nuova terapia", 'id': "btn-nuova-terapia", 'color': "primary"}
    btn2 = {'text': "Torna al Menu Terapie", 'id': "btn-torna-menu-terapie", 'color': "info"}
    
    return create_success_alert("Terapia assegnata con successo!", content, 
        create_terapia_success_buttons(btn1, btn2))

def get_terapia_modify_success_message(paziente_nome, nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine=None):
    """Messaggio di successo dopo modifica terapia"""
    content = [
        html.P(f"Paziente: {paziente_nome}"),
        html.P(f"Farmaco: {nome_farmaco}"),
        html.P(f"Dosaggio: {dosaggio}"),
        html.P(f"Assunzioni giornaliere: {assunzioni_giornaliere}"),
        html.P(f"Data inizio: {data_inizio.strftime('%d/%m/%Y')}"),
        html.P(f"Data fine: {data_fine.strftime('%d/%m/%Y')}" if data_fine else "Durata: Terapia continuativa")
    ]
    
    btn1 = {'text': "Modifica altra terapia", 'id': "btn-modifica-altra-terapia", 'color': "primary"}
    btn2 = {'text': "Torna al Menu Terapie", 'id': "btn-torna-menu-terapie", 'color': "info"}
    
    return create_success_alert("Terapia modificata con successo!", content, 
        create_terapia_success_buttons(btn1, btn2))

def get_terapia_delete_success_message(paziente_nome, nome_farmaco, dosaggio):
    """Messaggio di successo dopo eliminazione terapia"""
    content = [
        html.I(className="fas fa-check-circle fa-2x text-success mb-3"),
        html.P("Ãˆ stata eliminata la seguente terapia:"),
        html.Ul([
            html.Li(f"Paziente: {paziente_nome}"),
            html.Li(f"Farmaco: {nome_farmaco}"),
            html.Li(f"Dosaggio: {dosaggio}")
        ]),
        html.P("La terapia Ã¨ stata rimossa definitivamente dal sistema.", className="text-muted")
    ]
    
    btn1 = {'text': "Elimina altra terapia", 'id': "btn-elimina-altra-terapia", 'color': "danger"}
    btn2 = {'text': "Torna al Menu Terapie", 'id': "btn-torna-menu-terapie", 'color': "info"}
    
    return create_success_alert("Terapia eliminata con successo!", content, 
        create_terapia_success_buttons(btn1, btn2))

def get_error_message(message):
    """Messaggio di errore generico"""
    return dbc.Alert(message, color="danger", dismissable=True)

def get_edit_terapia_form(terapia, pazienti):
    """Form per modificare una terapia esistente con dati precompilati"""
    composite_key = f"{terapia.medico_nome}|{terapia.paziente.username}|{terapia.nome_farmaco}|{terapia.data_inizio.strftime('%Y-%m-%d') if terapia.data_inizio else 'None'}"
    
    return dbc.Card([
        dbc.CardHeader([html.H5("Modifica Terapia", className="mb-0 text-primary")]),
        dbc.CardBody([
            html.Div(composite_key, id="hidden-terapia-key", style={"display": "none"}),
            dbc.Alert([
                html.Strong("Stai modificando: "),
                f"{terapia.nome_farmaco} per {terapia.paziente.name} {terapia.paziente.surname}"
            ], color="info", className="mb-4"),
            
            create_patient_selector(pazienti, "select-paziente-terapia-edit"),
            
            # Form fields precompilati (mantengo la logica originale ma piÃ¹ compatta)
            dbc.Row([
                create_form_input("input-nome-farmaco-terapia-edit", "Nome del farmaco *", 
                    value=terapia.nome_farmaco, width=12, md=6),
                create_form_input("input-dosaggio-terapia-edit", "Dosaggio per assunzione *", 
                    value=terapia.dosaggio_per_assunzione, width=12, md=6)
            ], className="mb-3"),
            
            # Altri campi seguono lo stesso pattern...
            html.Div([
                dbc.Button("Salva Modifiche", id="btn-salva-modifiche-terapia", 
                    color="success", size="lg", className="me-2"),
                create_back_to_menu_button("Torna al Menu Terapie", "info")
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_andamento_glicemico_medico_view():
    return dbc.Card([
        dbc.CardHeader(
            html.H5("Andamento glicemico — settimanale e mensile", 
                className="doctor-title mb-0", style={"fontWeight": "400"})
        ),
        dbc.CardBody([
            html.Div([
                html.Label("Seleziona paziente", className="form-label"),
                dcc.Dropdown(
                    id="doctor-patient-selector",
                    options=[],
                    placeholder="Cognome Nome (username)",
                    clearable=False,
                    style={"maxWidth": "520px"},
                    className="form-control"
                )
            ], className="mb-4"),

            html.H6("A) Media giornaliera (Lun→Dom, settimana corrente)", className="form-label"),
            dcc.Graph(id="doctor-week-dow", config={"displayModeBar": False}),
            html.Hr(),

            html.H6("B) Media settimana per settimana", className="form-label"),
            html.Div([
                html.Label("Finestra settimane", className="form-label"),
                dcc.Dropdown(
                    id="weeks-window-medico",
                    options=[
                        {"label": "Ultime 4 settimane", "value": 4},
                        {"label": "Ultime 8 settimane", "value": 8}
                    ],
                    value=8,
                    clearable=False,
                    style={"maxWidth": "320px"},
                    className="form-control"
                )
            ], className="mb-3"),
            dcc.Graph(id="doctor-weekly-avg", config={"displayModeBar": False}),
            html.Hr(),

            html.H6("C) Media mese per mese (Gen→Dic)", className="form-label"),
            dcc.Graph(id="doctor-monthly-avg", config={"displayModeBar": False}),

            html.Div("Scala 0—300 mg/dL", className="mt-2 text-muted")
        ])
    ], className="mb-4", style={"backgroundColor": "white", "backdropFilter": "none"})

# Funzioni per gestione dati pazienti

def get_dati_pazienti_menu(pazienti):
    """Menu per selezionare il paziente di cui visualizzare i dati"""
    if not pazienti:
        return dbc.Card([
            dbc.CardHeader([html.H5("Dati Pazienti", className="mb-0 text-primary")]),
            dbc.CardBody([create_no_patients_alert()])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([html.H5("Dati Pazienti", className="mb-0 text-primary")]),
        dbc.CardBody([
            html.P("Seleziona il paziente di cui vuoi visualizzare o modificare i dati clinici:", 
                className="card-text mb-4"),
            create_patient_selector(pazienti, "select-paziente-dati"),
            dbc.FormText("Seleziona un paziente per visualizzare i suoi dati clinici", 
                className="text-muted mb-3"),
            html.Div(id="dati-paziente-display", className="mt-3")
        ])
    ], className="mt-3")

def create_patient_info_section(paziente, title, info_dict, css_class=""):
    """Crea sezione informazioni paziente"""
    info_elements = []
    for label, value in info_dict.items():
        display_value = value if value else "Non specificato"
        css_class = "text-muted" if not value else ""
        info_elements.extend([
            html.Strong(f"{label}: "), 
            html.Span(display_value, className=css_class), 
            html.Br()
        ])
    
    return dbc.Col([
        html.H6(title, className="text-secondary mb-3"),
        html.P(info_elements, className="card-text")
    ], width=12, md=6)

def get_patient_data_display(paziente, can_modify=True):
    """Visualizza i dati clinici del paziente con opzione di modifica"""
    general_info = {
        "Nome Completo": f"{paziente.name} {paziente.surname}",
        "Username": paziente.username,
        "Data di Nascita": paziente.birth_date.strftime('%d/%m/%Y') if paziente.birth_date else None,
        "EtÃ ": f"{paziente.eta} anni" if paziente.eta else None,
        "Codice Fiscale": paziente.codice_fiscale
    }
    
    clinical_info = {
        "Fattori di Rischio": paziente.fattori_rischio,
        "Pregresse Patologie": paziente.pregresse_patologie,
        "Comorbidità ": paziente.comorbidita,
        "Medico di riferimento": f"{paziente.medico_riferimento.name} ({paziente.medico_riferimento.username})" if paziente.medico_riferimento and paziente.medico_riferimento.name and paziente.medico_riferimento.username else "Non assegnato"
    }
    
    action_buttons = [
        ("Modifica Dati Clinici", "btn-modifica-dati-paziente", "primary", "edit", not can_modify),
        ("Seleziona Altro Paziente", "btn-altro-paziente", "primary", "user-plus", False),
        ("Torna al Menu", "btn-torna-menu-principale", "info", "arrow-left", False)
    ]
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.Img(src="/assets/patient.png", style={"width": "30px", "height": "30px", "margin-right": "8px"}),
                html.H6(f"Dati Clinici - {paziente.name} {paziente.surname}", 
                    className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            dbc.Row([
                create_patient_info_section(paziente, "Informazioni Generali", general_info),
                create_patient_info_section(paziente, "Dati Clinici", clinical_info)
            ], className="mb-4"),
            
            # Info ultima modifica
            html.Div([
                html.Hr(),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Ultima modifica effettuata da: "),
                    html.Span(paziente.info_aggiornate, className="fw-bold")
                ], color="info", className="mb-3")
            ]) if paziente.info_aggiornate else html.Div(),
            
            # Alert accesso limitato
            html.Div([
                html.Hr() if paziente.info_aggiornate else html.Div(),
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    html.Strong("Accesso limitato: "),
                    "Non sei autorizzato a modificare i dati clinici di questo paziente."
                ], color="warning", className="mb-3")
            ]) if not can_modify else html.Div(),
            
            # Bottoni azioni
            html.Hr() if (not paziente.info_aggiornate and can_modify) else html.Div(),
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        html.I(className=f"fas fa-{icon} me-2"), text
                    ], id=btn_id, color=color, size="lg", className="w-100", disabled=disabled)
                ], width=12, md=4)
                for text, btn_id, color, icon, disabled in action_buttons
            ], className="g-3")
        ])
    ], className="mt-3")

def get_edit_patient_data_form(paziente):
    """Form per modificare i dati clinici del paziente"""
    form_fields = [
        ("textarea-fattori-rischio", "Fattori di Rischio", 
         "es. Diabete familiare, ipertensione, obesitÃ , fumo...", 
         paziente.fattori_rischio, "Elenca i principali fattori di rischio del paziente"),
        ("textarea-pregresse-patologie", "Pregresse Patologie", 
         "es. Infarto del miocardio 2020, bypass coronarico 2018...", 
         paziente.pregresse_patologie, "Elenca le principali patologie pregresse del paziente"),
        ("textarea-comorbidita", "ComorbiditÃ ", 
         "es. Insufficienza renale cronica, BPCO, depressione...", 
         paziente.comorbidita, "Elenca le comorbiditÃ  attuali del paziente")
    ]
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-user-edit fa-lg me-2"),
                html.H5(f"Modifica Dati Clinici - {paziente.name} {paziente.surname}", 
                    className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            html.Div(paziente.username, id="hidden-patient-username", style={"display": "none"}),
            
            dbc.Alert([
                html.Strong("Stai modificando i dati clinici di: "),
                f"{paziente.name} {paziente.surname} ({paziente.username})"
            ], color="info", className="mb-4"),
            
            # Form fields
            *[create_textarea(field_id, label, placeholder, 
                value if value else '', 3, help_text) 
              for field_id, label, placeholder, value, help_text in form_fields],
            
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                html.Strong("Nota: "),
                "I campi possono essere lasciati vuoti se non applicabili. Le modifiche saranno salvate immediatamente."
            ], color="info", className="mb-4"),
            
            html.Div([
                dbc.Button([html.I(className="fas fa-save me-2"), "Salva Modifiche"],
                    id="btn-salva-dati-paziente", color="primary", size="lg", className="me-2"),
                dbc.Button([html.I(className="fas fa-times me-2"), "Annulla"],
                    id="btn-annulla-modifica-dati", color="secondary", size="lg")
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_patient_data_update_success_message(paziente_nome):
    """Messaggio di successo dopo aggiornamento dati paziente"""
    content = [
        html.I(className="fas fa-check-circle fa-2x text-success mb-3"),
        html.P(f"I dati clinici di {paziente_nome} sono stati aggiornati correttamente."),
        html.P("Le modifiche sono state salvate nel sistema.", className="text-muted")
    ]
    
    buttons = [
        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-eye me-2"), "Visualizza Dati Aggiornati"], 
                    id="btn-visualizza-dati-aggiornati", color="primary", size="sm", className="w-100")
            ], width=6),
            dbc.Col([
                dbc.Button([html.I(className="fas fa-users me-2"), "Gestisci Altri Pazienti"], 
                    id="btn-gestisci-altri-pazienti", color="primary", size="sm", className="w-100")
            ], width=6)
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-arrow-left me-2"), "Torna al Menu Principale"], 
                    id="btn-torna-menu-principale", color="info", size="lg", className="btn-info w-100")
            ], width=12)
        ])
    ]
    
    return create_success_alert("Dati clinici aggiornati con successo!", content, buttons)

# Funzioni per gestione seguimento pazienti

def create_patient_follow_card(paziente, action_type="follow"):
    """Crea card per paziente da seguire/smettere di seguire"""
    if action_type == "unfollow":
        button_config = {
            'text': "Smetti di seguire",
            'id_type': 'btn-smetti-seguire-paziente',
            'color': 'outline-danger',
            'icon': 'user-times'
        }
        border_color = "#28a745"
    else:
        button_config = {
            'text': "Inizia a seguire",
            'id_type': 'btn-inizia-seguire-paziente',
            'color': 'success',
            'icon': 'user-plus'
        }
        border_color = "#007bff"
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(f"{paziente.name} {paziente.surname}", className="mb-1"),
                    html.Small(f"Username: {paziente.username}", className="text-muted")
                ], width=8),
                dbc.Col([
                    dbc.Button([
                        html.I(className=f"fas fa-{button_config['icon']} me-1"),
                        button_config['text']
                    ], id={'type': button_config['id_type'], 'index': paziente.username},
                    color=button_config['color'], size="sm", className="w-100")
                ], width=4, className="d-flex align-items-center")
            ])
        ])
    ], className="mb-2", style={"border-left": f"4px solid {border_color}"})

def get_segui_paziente_form(tutti_pazienti, pazienti_seguiti):
    """Form per seguire un nuovo paziente"""
    pazienti_non_seguiti = [p for p in tutti_pazienti if p not in pazienti_seguiti]
    
    if not tutti_pazienti:
        return dbc.Card([
            dbc.CardHeader([html.H5("Gestione Pazienti", className="mb-0 text-primary")]),
            dbc.CardBody([
                dbc.Alert([
                    html.H5("Nessun paziente disponibile", className="alert-heading"),
                    html.P("Non ci sono pazienti disponibili nel sistema."),
                    html.Hr(),
                    create_back_to_menu_button()
                ], color="info")
            ])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5("Gestione Pazienti", className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            # Sezione pazienti seguiti
            html.Div([
                html.H6("Pazienti che segui attualmente:", className="text-secondary mb-3"),
                
                # Se ci sono pazienti seguiti, mostra dropdown per smettere di seguire
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Select(
                                id="select-paziente-da-smettere",
                                options=[
                                    {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
                                    for p in pazienti_seguiti
                                ],
                                placeholder="Seleziona paziente da rimuovere...",
                                className="form-control"
                            )
                        ], width=8),
                        dbc.Col([
                            dbc.Button(
                                [html.I(className="fas fa-user-times me-1"), "Smetti di seguire"],
                                id="btn-smetti-seguire",
                                color="outline-danger",
                                size="sm",
                                className="w-100"
                            )
                        ], width=4)
                    ], className="mb-3")
                ] if pazienti_seguiti else [
                    html.P("Non segui ancora nessun paziente.", className="text-muted mb-3")
                ]),
                
                html.Hr(className="my-4") if pazienti_seguiti else html.Div()
            ]),
            
            # Sezione aggiungi nuovo paziente
            html.Div([
                html.H6("Aggiungi nuovo paziente:", className="text-secondary mb-3"),
                
                html.Div([
                    create_patient_selector(pazienti_non_seguiti, "select-nuovo-paziente", 
                        "Seleziona Nuovo Paziente"),
                    
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        html.Strong("Nota: "),
                        "Seguendo un paziente potrai gestire le sue terapie e modificare i suoi dati clinici."
                    ], color="info", className="mb-4"),
                    
                    # Bottoni per seguire il paziente
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([html.I(className="fas fa-user-plus me-1"), "Inizia a Seguire"],
                                id="btn-conferma-segui-paziente", color="success", size="lg", 
                                className="w-100")
                        ], width=6),
                        dbc.Col([
                            dbc.Button([html.I(className="fas fa-user-md me-1"), "Segui come medico di riferimento"],
                                id="btn-segui-come-medico-riferimento", color="success", size="lg", 
                                className="w-100")
                        ], width=6)
                    ], className="mb-3")
                ] if pazienti_non_seguiti else [
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        "Stai già  seguendo tutti i pazienti disponibili nel sistema."
                    ], color="info", className="mb-3")
                ])
            ]),
            
            html.Hr(),
            html.Div([
                create_back_to_menu_button()
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def create_patient_action_success_message(paziente_nome, paziente_username, action_type="follow", is_medico_riferimento=False):
    """Messaggio di successo per azioni sui pazienti"""
    if action_type == "unfollow":
        title = "Paziente rimosso con successo!"
        main_text = f"Non segui più: {paziente_nome} ({paziente_username})"
        sub_text = "Non potrai più gestire le sue terapie o modificare i suoi dati clinici."
        icon_class = "fas fa-check-circle fa-2x text-warning mb-3"
        color = "warning"
        btn1_config = ("Gestisci Altri Pazienti", "btn-gestisci-altri-pazienti", "primary", "users")
    elif is_medico_riferimento:
        title = "Medico di riferimento assegnato con successo!"
        main_text = f"Sei ora il medico di riferimento di: {paziente_nome} ({paziente_username})"
        sub_text = "Hai accesso completo alla gestione clinica di questo paziente e sarai indicato come suo medico di riferimento."
        icon_class = "fas fa-user-md fa-2x text-primary mb-3"
        color = "primary"
        btn1_config = ("Segui Altro Paziente", "btn-segui-altro-paziente", "primary", "user-plus")
    else:
        title = "Paziente aggiunto con successo!"
        main_text = f"Ora stai seguendo: {paziente_nome} ({paziente_username})"
        sub_text = "Puoi ora gestire le sue terapie e visualizzare i suoi dati clinici."
        icon_class = "fas fa-check-circle fa-2x text-success mb-3"
        color = "success"
        btn1_config = ("Segui Altro Paziente", "btn-segui-altro-paziente", "primary", "user-plus")
    
    content = [
        html.I(className=icon_class),
        html.P(main_text, className="fw-bold"),
        html.P(sub_text, className="text-muted")
    ]
    
    buttons = [
        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className=f"fas fa-{btn1_config[3]} me-2"), btn1_config[0]], 
                    id=btn1_config[1], color=btn1_config[2], size="lg", className="w-100")
            ], width=12, md=6),
            dbc.Col([
                dbc.Button([html.I(className="fas fa-arrow-left me-2"), "Torna al Menu Principale"], 
                    id="btn-torna-menu-principale", color="info", size="lg", className="btn-info w-100")
            ], width=12, md=6)
        ], className="g-3")
    ]
    
    return dbc.Alert(content + [html.Hr()] + buttons, color=color, dismissable=True)

def get_smetti_seguire_success_message(paziente_nome, paziente_username):
    return create_patient_action_success_message(paziente_nome, paziente_username, "unfollow")

def get_segui_paziente_success_message(paziente_nome, paziente_username):
    return create_patient_action_success_message(paziente_nome, paziente_username, "follow")

def get_segui_come_medico_riferimento_success_message(paziente_nome, paziente_username):
    """Messaggio di successo specifico per il medico di riferimento"""
    return create_patient_action_success_message(paziente_nome, paziente_username, "follow", is_medico_riferimento=True)

def get_paziente_gia_seguito_message(paziente_nome):
    """Messaggio quando si tenta di seguire un paziente giÃ  seguito"""
    content = [
        html.I(className="fas fa-info-circle fa-2x text-info mb-3"),
        html.P(f"Stai giÃ  seguendo il paziente: {paziente_nome}"),
        html.P("Non Ã¨ necessario aggiungerlo nuovamente.", className="text-muted")
    ]
    
    buttons = [
        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-user-plus me-2"), "Segui Altro Paziente"], 
                    id="btn-segui-altro-paziente", color="success", size="sm", className="w-100")
            ], width=6),
            dbc.Col([
                dbc.Button([html.I(className="fas fa-arrow-left me-2"), "Torna al Menu"], 
                    id="btn-torna-menu-principale", color="info", size="lg", className="btn-info w-100")
            ], width=6)
        ], className="g-3")
    ]
    
    return dbc.Alert(content + [html.Hr()] + buttons, color="info", dismissable=True)

# Utility functions

def get_indicazioni_display(indicazioni):
    """Converte il codice indicazioni in testo leggibile"""
    mapping = {
        "prima_pasti": "Prima dei pasti",
        "dopo_pasti": "Dopo i pasti", 
        "lontano_pasti": "Lontano dai pasti",
        "mattino": "Al mattino",
        "sera": "Alla sera",
        "secondo_necessita": "Secondo necessitÃ "
    }
    return mapping.get(indicazioni, indicazioni)