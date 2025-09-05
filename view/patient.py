#view/patient.py
"""Dashboard e layout per i pazienti"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date

# DASHBOARD PRINCIPALE

# MODIFICHE PER view/patient.py
# Sostituisci la funzione get_patient_dashboard con questa versione aggiornata:

def get_patient_dashboard(username):
    """Dashboard per i pazienti"""
    return dbc.Container([
        # Header con logo fisso
        html.Img(
            src="/assets/health.png",
            style={
                "position": "fixed", "top": "20px", "right": "20px",
                "width": "150px", "height": "auto", "z-index": "1000"
            }
        ),
        
        # Link logout fisso
        dcc.Link("Logout", href="/logout", 
               style={
                   "position": "fixed", "top": "20px", "left": "20px",
                   "color": "white", "text-decoration": "none", "font-weight": "600",
                   "font-size": "16px", "background": "rgba(16, 185, 129, 1)",
                   "padding": "10px 20px", "border-radius": "25px",
                   "backdrop-filter": "blur(10px)", "border": "1px solid rgba(255, 255, 255, 0.2)",
                   "z-index": "1000"
               }),
        
        # Titolo di benvenuto
        dbc.Row([
            dbc.Col([
                html.H2(f"Benvenuto/a {username}", 
                       className="gradient-title text-center",
                       style={
                           "margin-top": "20px", "margin-bottom": "30px",
                           "color": "white", "text-shadow": "2px 2px 4px rgba(0,0,0,0.3)"
                       })
            ], width=12)
        ]),
        
        # Card principale con pulsanti
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        className="d-flex align-items-center",
                        children=[
                            html.Div([
                                html.Img(src="/assets/patient.png", 
                                       style={"width": "40px", "height": "40px", "margin-right": "10px"}),
                                html.H4("Area Paziente", className="mb-0 patient-title", 
                                      style={"display": "inline-block"})
                            ], className="d-flex align-items-center"),
                            
                            # Campanellina in alto a dx nell'header
                            dbc.Button(
                                html.Img(src="/assets/bell_ring.png",
                                         style={"width": "32px", "height": "32px"}),
                                id="bell-button",
                                color="success",
                                className="rounded-circle p-2 shadow-sm ms-auto",
                                n_clicks=0,
                            ),
                        ],
                    ),
                    
                    dbc.CardBody([
                        html.P("Benvenuto nella tua area personale. Qui puoi gestire i tuoi dati sanitari.", 
                               className="card-text mb-4"),
                        
                        # Alert invito assunzioni (render via callback)
                        html.Div(id="meds-alert-container", className="mb-3"),
                        
                        # Griglia pulsanti
                        _create_patient_buttons_grid(),
                        
                        # Area per messaggi/feedback
                        html.Div(id="patient-feedback", className="mt-3"),
                        
                        # Modal per gli alert
                        dbc.Modal(
                            id="alerts-modal",
                            is_open=False,
                            children=[
                                dbc.ModalHeader(dbc.ModalTitle("I tuoi promemoria")),
                                dbc.ModalBody(id="alerts-modal-body"),
                                dbc.ModalFooter(
                                    dbc.Button("Chiudi", id="alerts-modal-close", color="secondary")
                                )
                            ]
                        ),
                        dcc.Store(id="alerts-refresh", data={"ts": 0}),
                    ])
                ]),
                
                # Area per contenuto dinamico
                html.Div(id="patient-content", className="mt-3", children=get_patient_welcome_content())
                
            ], width=8)
        ], justify="center", className="mt-4")
    ], fluid=True, className="main-container")



def get_patient_welcome_content():
    """Restituisce il contenuto di benvenuto per la dashboard medico"""
    return [
        dbc.Alert([
            html.H4([
                html.Img(src="/assets/pc.gif", style={"width": "50px", "height": "50px", "marginRight": "8px"}),
                "Benvenuto/a nella Dashboard Paziente!"
            ], className="alert-heading"),
            html.P("Seleziona una delle opzioni sopra per iniziare a gestire i tuoi dati."),
            html.Hr(),
            html.P("🔹 Registra i tuoi livelli di glicemia, le tue assunzioni farmacologiche o i tuoi sintomi / trattamenti"),
            html.P("🔹 Visualizza i tuoi dati (anche chi è il tuo medico di riferimento)"),
            html.P("🔹 Visualizza le terapie che ti sono state assegnate"),
            html.P("🔹 Analizza i tuoi andamenti glicemici e le statistiche")
        ], color="light", className="mb-4")
    ]

def _create_patient_buttons_grid():
    """Crea la griglia dei pulsanti del dashboard paziente"""
    buttons = [
        ("btn-registra-glicemia", "/assets/glicemia.png", "Registra Glicemia", "btn-primary"),
        ("btn-andamento-glicemico", "/assets/grafico.png", "Andamento Glicemico", "btn-success"),
        ("btn-miei-dati", "/assets/dati.png", "I Miei Dati", "btn-success"),
        ("btn-nuova-assunzione", "/assets/farmaco.png", "Nuova Assunzione", "btn-success"),
        ("btn-sintomi-trattamenti", "/assets/sintomi.png", "Sintomi e Trattamenti", "btn-success"),
        ("btn-terapie", "/assets/terapia.png", "Le mie terapie", "btn-success"),
        ("btn-messaggi", "/assets/messaggi.png", "Contatta il tuo medico di base", "btn-success")
    ]
    
    rows = []
    for i in range(0, 6, 2):
        cols = []
        for j in range(2):
            if i + j < len(buttons):
                btn_id, icon, text, css_class = buttons[i + j]
                cols.append(
                    dbc.Col([
                        dbc.Button([
                            html.Img(src=icon, 
                                   style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                            text
                        ], id=btn_id, className=f"{css_class} w-100", size="lg")
                    ], width=12, md=6, className="mb-3")
                )
            else:
                cols.append(dbc.Col([], width=12, md=6, className="mb-3"))
        
        rows.append(dbc.Row(cols))

        # Ultima riga con il bottone centrato
    if len(buttons) > 6:
        btn_id, icon, text, css_class = buttons[6]
        rows.append(
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        html.Img(src=icon, 
                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                        text
                    ], id=btn_id, className=f"{css_class} w-100", size="lg")
                ], width=12, md=6, className="mb-3")
            ], justify="center")
        )
    
    return html.Div(rows)

def get_glicemia_form():
    """Form per registrare nuova misurazione glicemia"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Registrazione Glicemia", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            # Valore e data
            dbc.Row([
                dbc.Col([
                    dbc.Label("Valore glicemia (mg/dL) *", className="form-label"),
                    dbc.Input(id="input-valore-glicemia", type="number", 
                            min=0, max=600, step=1, placeholder="es. 120", className="form-control")
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Data misurazione *", className="form-label"),
                    dbc.Input(id="input-data-glicemia", type="date",
                            value=date.today().strftime('%Y-%m-%d'),
                            max=date.today().strftime('%Y-%m-%d'),
                            style={"cursor": "pointer"}, className="form-control")
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Ora e momento
            dbc.Row([
                dbc.Col([
                    dbc.Label("Ora misurazione *", className="form-label"),
                    dbc.Input(id="input-ora-glicemia", type="time",
                            value=datetime.now().strftime("%H:%M"), className="form-control")
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Momento rispetto ai pasti *", className="form-label"),
                    dbc.Select(id="select-momento-pasto", 
                             options=[
                                 {"label": "A digiuno", "value": "digiuno"},
                                 {"label": "Prima del pasto", "value": "prima_pasto"},
                                 {"label": "Dopo il pasto", "value": "dopo_pasto"}
                             ], placeholder="Seleziona...", className="form-control")
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Campo condizionale due ore dopo pasto
            html.Div(id="due-ore-pasto-container", children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Sono passate almeno due ore dopo l'ultimo pasto? *", 
                                className="form-label text-info"),
                        dbc.RadioItems(id="radio-due-ore-pasto",
                                     options=[{"label": "Sì", "value": True}, {"label": "No", "value": False}],
                                     inline=True, className="mt-2",
                                     input_style={"margin-right": "8px", "transform": "scale(1.3)", 
                                                "accent-color": "#0d6efd", "border": "2px solid #000000"},
                                     labelStyle={"margin-right": "25px", "font-weight": "500"})
                    ], width=12)
                ], className="mb-3")
            ], style={"display": "none"}),
            
            # Note
            dbc.Row([
                dbc.Col([
                    dbc.Label("Note (opzionale)", className="form-label"),
                    dbc.Textarea(id="textarea-note-glicemia", 
                               placeholder="Eventuali note o osservazioni...",
                               rows=3, className="form-control")
                ], width=12)
            ], className="mb-3"),
            
            # Pulsanti
            _create_form_buttons("btn-salva-glicemia", "btn-annulla-glicemia", 
                               "Salva Misurazione", "Annulla")
        ])
    ], className="mt-3")

def get_nuova_assunzione_form():
    """Form per registrare una nuova assunzione di farmaci"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Registrazione Assunzione Farmaci", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            # Nome farmaco e dosaggio
            dbc.Row([
                dbc.Col([
                    dbc.Label("Nome del farmaco *", className="form-label"),
                    dbc.Input(id="input-nome-farmaco", type="text", 
                            placeholder="es. Metformina", className="form-control")
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Dosaggio *", className="form-label"),
                    dbc.Input(id="input-dosaggio-farmaco", type="text", 
                            placeholder="es. 500mg, 1 compressa...", className="form-control")
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Data e ora
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data assunzione *", className="form-label"),
                    dbc.Input(id="input-data-assunzione", type="date",
                            value=date.today().strftime('%Y-%m-%d'),
                            max=date.today().strftime('%Y-%m-%d'), className="form-control")
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Ora assunzione *", className="form-label"),
                    dbc.Input(id="input-ora-assunzione", type="time",
                            value=datetime.now().strftime("%H:%M"), className="form-control")
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Note
            dbc.Row([
                dbc.Col([
                    dbc.Label("Note (opzionale)", className="form-label"),
                    dbc.Textarea(id="textarea-note-assunzione", 
                               placeholder="Eventuali note sull'assunzione...",
                               rows=3, className="form-control")
                ], width=12)
            ], className="mb-3"),
            
            # Pulsanti
            _create_form_buttons("btn-salva-assunzione", "btn-annulla-assunzione", 
                               "Salva Assunzione", "Annulla")
        ])
    ], className="mt-3")

def get_sintomi_trattamenti_form():
    """Form per registrare sintomi, patologie e trattamenti"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Registrazione Sintomi e Trattamenti", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            # Tipo e descrizione
            dbc.Row([
                dbc.Col([
                    dbc.Label("Tipo *", className="form-label"),
                    dbc.Select(id="select-tipo-sintomo",
                             options=[
                                 {"label": "Sintomo", "value": "sintomo"},
                                 {"label": "Patologia", "value": "patologia"},
                                 {"label": "Trattamento", "value": "trattamento"}
                             ], placeholder="Seleziona il tipo...", className="form-control")
                ], width=12, md=4),
                
                dbc.Col([
                    dbc.Label("Descrizione *", className="form-label"),
                    dbc.Input(id="input-descrizione-sintomo", type="text",
                            placeholder="es. Mal di testa, Ipertensione, Fisioterapia...",
                            className="form-control")
                ], width=12, md=8)
            ], className="mb-3"),
            
            # Date inizio e fine
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data inizio *", className="form-label"),
                    dbc.Input(id="input-data-inizio-sintomo", type="date",
                            value=date.today().strftime('%Y-%m-%d'),
                            max=date.today().strftime('%Y-%m-%d'), className="form-control")
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Data fine (se applicabile)", className="form-label"),
                    dbc.Input(id="input-data-fine-sintomo", type="date",
                            max=date.today().strftime('%Y-%m-%d'), className="form-control"),
                    dbc.FormText("Lascia vuoto se ancora in corso", className="text-muted")
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Campo condizionale per frequenza (solo sintomi)
            html.Div(id="campi-sintomi-container", children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Frequenza", className="form-label text-info"),
                        dbc.Select(id="select-frequenza-sintomo",
                                 options=[
                                     {"label": "Occasionale", "value": "occasionale"},
                                     {"label": "Frequente", "value": "frequente"},
                                     {"label": "Continuo", "value": "continuo"}
                                 ], placeholder="Seleziona frequenza...", className="form-control")
                    ], width=12, md=6)
                ], className="mb-3")
            ], style={"display": "none"}),
            
            # Note
            dbc.Row([
                dbc.Col([
                    dbc.Label("Note (opzionale)", className="form-label"),
                    dbc.Textarea(id="textarea-note-sintomo", 
                               placeholder="Eventuali note aggiuntive...",
                               rows=3, className="form-control")
                ], width=12)
            ], className="mb-3"),
            
            # Pulsanti
            _create_form_buttons("btn-salva-sintomo", "btn-annulla-sintomo", 
                               "Salva Registrazione", "Annulla")
        ])
    ], className="mt-3")


def get_miei_dati_view():
    """Vista per visualizzare i dati personali del paziente - sola lettura"""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5("I Miei Dati Personali", className="mb-0 text-success", 
                       style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            html.P("Qui puoi visualizzare tutti i tuoi dati personali e clinici.", 
                   className="card-text mb-4"),
            html.Div(id="miei-dati-content"),
            _create_back_button("btn-torna-menu-paziente")
        ])
    ], className="mt-3")


def get_patient_personal_data_display(paziente):
    """Visualizza tutti i dati personali del paziente corrente"""
    # Informazioni anagrafiche
    general_info = {
        "Nome Completo": f"{paziente.name} {paziente.surname}",
        "Username": paziente.username,
        "Data di Nascita": paziente.birth_date.strftime('%d/%m/%Y') if paziente.birth_date else None,
        "Età": f"{paziente.eta} anni" if paziente.eta else None,
        "Codice Fiscale": paziente.codice_fiscale
    }
    
    # Dati clinici
    clinical_info = {
        "Fattori di Rischio": paziente.fattori_rischio,
        "Pregresse Patologie": paziente.pregresse_patologie,
        "Comorbidità": paziente.comorbidita,
        "Medico di riferimento": f"{paziente.medico_riferimento.name} {paziente.medico_riferimento.surname}" if paziente.medico_riferimento else "Non assegnato",
    }
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                create_patient_info_section_readonly("Informazioni Anagrafiche", general_info),
                create_patient_info_section_readonly("Dati Clinici", clinical_info)
            ], className="mb-4")
        ])
    ], className="mt-3", style={"border-left": "4px solid #28a745"})


def create_patient_info_section_readonly(title, info_dict, col_width=6):
    """Crea sezione informazioni paziente in sola lettura"""
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
        html.H6(title, className="text-success mb-3"),
        html.P(info_elements, className="card-text")
    ], width=12, md=col_width)

def get_andamento_glicemico_view():
    """Card con 3 grafici: giorno-settimana, media settimanale, media mensile"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Andamento glicemico — settimanale e mensile",
                   className="patient-title mb-0", style={"fontWeight": "400"})
        ]),
        dbc.CardBody([
            # Grafico A - Media giornaliera settimana corrente
            html.H6("A) Media giornaliera (Lun→Dom, settimana corrente)", className="form-label"),
            dcc.Graph(id="patient-week-dow", config={"displayModeBar": False}),
            html.Hr(),

            # Grafico B - Media settimana per settimana
            html.H6("B) Media settimana per settimana", className="form-label"),
            html.Div([
                html.Label("Finestra settimane", className="form-label"),
                dcc.Dropdown(id="weeks-window",
                           options=[
                               {"label": "Ultime 4 settimane", "value": 4},
                               {"label": "Ultime 8 settimane", "value": 8},
                           ],
                           value=8, clearable=False, style={"maxWidth": "320px"})
            ], className="mb-3"),
            dcc.Graph(id="patient-weekly-avg", config={"displayModeBar": False}),
            html.Hr(),

            # Grafico C - Media mese per mese
            html.H6("C) Media mese per mese (Gen→Dic)", className="form-label"),
            dcc.Graph(id="patient-monthly-avg", config={"displayModeBar": False}),
            
            html.Div("Scala 0—300 mg/dL", className="mt-2 text-muted"),
            
            _create_back_button("btn-torna-menu-grafici")
        ])
    ], className="mb-4", style={"backgroundColor": "white", "backdropFilter": "none"})

def get_mie_terapie_view():
    """Vista per visualizzare tutte le terapie del paziente - sola lettura"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Le Mie Terapie", className="mb-0 text-success")
        ]),
        dbc.CardBody([
            html.P("Qui puoi visualizzare tutte le terapie che ti sono state prescritte.", 
                   className="card-text mb-4"),
            html.Div(id="mie-terapie-content"),
            _create_back_button("btn-torna-menu-terapie-paziente")
        ])
    ], className="mt-3")


def get_patient_therapies_display(terapie):
    """Visualizza tutte le terapie del paziente raggruppate per status"""
    if not terapie:
        return dbc.Alert([
            html.H5("Nessuna terapia trovata", className="alert-heading"),
            html.P("Non hai ancora terapie prescritte."),
            html.P("Le terapie assegnate dal tuo medico appariranno qui.", className="text-muted")
        ], color="info", className="mt-3")
    
    # Raggruppa terapie per status
    oggi = datetime.now().date()
    terapie_attive, terapie_programmate, terapie_completate = _group_therapies_by_status(terapie, oggi)
    
    sections = []
    
    # Sezione terapie attive
    if terapie_attive:
        sections.extend([
            _create_therapy_section_header("play-circle", "success", 
                                         f"Terapie in corso ({len(terapie_attive)})"),
            html.Div([create_terapia_card_patient(t) for t in terapie_attive]),
            html.Hr() if (terapie_programmate or terapie_completate) else html.Div()
        ])
    
    # Sezione terapie programmate
    if terapie_programmate:
        sections.extend([
            _create_therapy_section_header("clock", "info", 
                                         f"Terapie programmate ({len(terapie_programmate)})"),
            html.Div([create_terapia_card_patient(t) for t in terapie_programmate]),
            html.Hr() if terapie_completate else html.Div()
        ])
    
    # Sezione terapie completate
    if terapie_completate:
        sections.extend([
            _create_therapy_section_header("check-circle", "secondary", 
                                         f"Terapie completate ({len(terapie_completate)})"),
            html.Div([create_terapia_card_patient(t) for t in terapie_completate])
        ])
    
    return html.Div([
        dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            html.Strong("Informazioni: "),
            f"Hai un totale di {len(terapie)} terapie prescritte. "
            f"Segui sempre le indicazioni del tuo medico per dosaggi e orari."
        ], color="info", className="mb-4"),
        *sections
    ])


def create_terapia_card_patient(terapia):
    """Crea card per terapia del paziente - solo visualizzazione"""
    # Gestione date
    data_inizio_str = _format_date_safe(terapia.data_inizio) or "Non specificata"
    data_fine_str = _format_date_safe(terapia.data_fine) or "Continuativa"
    modificata_info = f" (Modificata da: {terapia.modificata})" if terapia.modificata else ""
    
    # Determina status terapia
    oggi = datetime.now().date()
    is_active, status_info = _get_therapy_status(terapia, oggi)
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5(f"{terapia.nome_farmaco}", className="card-title text-primary mb-2"),
                        html.Span([
                            html.I(className=f"fas fa-{status_info['icon']} me-1"),
                            status_info["text"]
                        ], className=f"badge bg-{status_info['color']} mb-3")
                    ]),
                    
                    # Informazioni principali
                    html.P([
                        html.Strong("Dosaggio: "), terapia.dosaggio_per_assunzione, html.Br(),
                        html.Strong("Assunzioni al giorno: "), str(terapia.assunzioni_giornaliere), html.Br(),
                        html.Strong("Dal: "), data_inizio_str, 
                        html.Strong(" al: ") if terapia.data_fine else html.Strong(" - "), data_fine_str, html.Br(),
                        html.Strong("Prescritto da: "), terapia.medico_nome, modificata_info
                    ], className="card-text"),
                    
                    # Indicazioni se presenti
                    html.Div([
                        html.Strong("Indicazioni: ", className="text-info"),
                        html.Span(get_indicazioni_display_patient(terapia.indicazioni) 
                                if terapia.indicazioni else "Nessuna indicazione specifica")
                    ], className="mb-2") if terapia.indicazioni else html.Div(),
                    
                    # Note se presenti
                    html.Div([
                        html.Strong("Note: ", className="text-muted"),
                        html.Span(terapia.note if terapia.note else "Nessuna nota")
                    ], className="small text-muted") if terapia.note else html.Div(),
                    
                ], width=12)
            ])
        ])
    ], className="mb-3", style={
        "border-left": f"4px solid {'#28a745' if is_active else '#6c757d'}"
    })

def get_success_message(valore, data_ora, momento_pasto, due_ore_pasto=None):
    """Messaggio di successo dopo salvataggio glicemia"""
    children = [
        html.H5("Misurazione salvata con successo!", className="alert-heading"),
        html.P(f"Glicemia: {valore} mg/dL"),
        html.P(f"Data e ora: {data_ora.strftime('%d/%m/%Y alle %H:%M')}"),
        html.P(f"Momento: {get_momento_display(momento_pasto)}")
    ]
    
    if momento_pasto == "dopo_pasto" and due_ore_pasto is not None:
        due_ore_text = "Sì" if due_ore_pasto else "No"
        children.append(html.P(f"Due ore dopo il pasto: {due_ore_text}"))
    
    children.extend([
        html.Hr(),
        dbc.Button("Registra nuova misurazione", id="btn-nuova-misurazione", 
                 color="primary", size="sm")
    ])
    
    return dbc.Alert(children, color="success", dismissable=True)


def get_assunzione_success_message(nome_farmaco, dosaggio, data_ora):
    """Messaggio di successo dopo salvataggio assunzione"""
    return dbc.Alert([
        html.H5("Assunzione salvata con successo!", className="alert-heading"),
        html.P(f"Farmaco: {nome_farmaco}"),
        html.P(f"Dosaggio: {dosaggio}"),
        html.P(f"Data e ora: {data_ora.strftime('%d/%m/%Y alle %H:%M')}"),
        html.Hr(),
        dbc.Button("Registra nuova assunzione", id="btn-nuova-assunzione-bis", 
                 color="primary", size="sm")
    ], color="success", dismissable=True)


def get_sintomi_success_message(tipo, descrizione, data_inizio, data_fine=None):
    """Messaggio di successo dopo salvataggio sintomo/trattamento"""
    children = [
        html.H5("Registrazione salvata con successo!", className="alert-heading"),
        html.P(f"Tipo: {get_tipo_display(tipo)}"),
        html.P(f"Descrizione: {descrizione}"),
        html.P(f"Data inizio: {data_inizio.strftime('%d/%m/%Y')}")
    ]
    
    if data_fine:
        children.append(html.P(f"Data fine: {data_fine.strftime('%d/%m/%Y')}"))
    else:
        children.append(html.P("Stato: In corso"))
    
    children.extend([
        html.Hr(),
        dbc.Button("Registra nuovo elemento", id="btn-nuovo-sintomo", 
                 color="primary", size="sm")
    ])
    
    return dbc.Alert(children, color="success", dismissable=True)


def get_error_message(message):
    """Messaggio di errore generico"""
    return dbc.Alert(message, color="danger", dismissable=True)

# Utility functions

def get_momento_display(momento_pasto):
    """Converte il codice momento in testo leggibile"""
    mapping = {
        "digiuno": "A digiuno",
        "prima_pasto": "Prima del pasto",
        "dopo_pasto": "Dopo il pasto"
    }
    return mapping.get(momento_pasto, momento_pasto)


def get_tipo_display(tipo):
    """Converte il tipo in testo leggibile"""
    mapping = {
        "sintomo": "Sintomo",
        "patologia": "Patologia", 
        "trattamento": "Trattamento"
    }
    return mapping.get(tipo, tipo)


def get_indicazioni_display_patient(indicazioni):
    """Converte il codice indicazioni in testo leggibile per il paziente"""
    mapping = {
        "prima_pasti": "Prima dei pasti",
        "dopo_pasti": "Dopo i pasti", 
        "lontano_pasti": "Lontano dai pasti",
        "mattino": "Al mattino",
        "sera": "Alla sera",
        "secondo_necessita": "Secondo necessità"
    }
    return mapping.get(indicazioni, indicazioni)


# funzioni helper private

def _create_form_buttons(save_id, cancel_id, save_text, cancel_text):
    """Crea i pulsanti standard per i form"""
    return html.Div([
        dbc.Button(save_text, id=save_id, color="success", size="lg", className="me-2"),
        dbc.Button(cancel_text, id=cancel_id, color="secondary", size="lg")
    ], className="d-grid gap-2 d-md-flex justify-content-md-end")


def _create_back_button(btn_id, text="Torna al Menu"):
    """Crea pulsante di ritorno al menu"""
    return html.Div([
        dbc.Button([
            html.I(className="fas fa-arrow-left me-2"),
            text
        ], id=btn_id, color="info", size="lg", className="btn-info")
    ], className="d-grid gap-2 d-md-flex justify-content-md-end mt-3")


def _create_therapy_section_header(icon, color, text):
    """Crea header per sezione terapie"""
    return html.H6([
        html.I(className=f"fas fa-{icon} text-{color} me-2"),
        text
    ], className=f"text-{color} mb-3")


def _format_date_safe(date_obj):
    """Formatta date in modo sicuro"""
    if not date_obj:
        return None
    try:
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime('%d/%m/%Y')
    except:
        pass
    return None


def _group_therapies_by_status(terapie, oggi):
    """Raggruppa terapie per status"""
    terapie_attive = []
    terapie_programmate = []
    terapie_completate = []
    
    for terapia in terapie:
        # Converti datetime in date per il confronto
        data_inizio = terapia.data_inizio.date() if isinstance(terapia.data_inizio, datetime) else terapia.data_inizio
        data_fine = None
        if terapia.data_fine:
            data_fine = terapia.data_fine.date() if isinstance(terapia.data_fine, datetime) else terapia.data_fine
        
        if data_fine and data_fine < oggi:
            terapie_completate.append(terapia)
        elif data_inizio and data_inizio > oggi:
            terapie_programmate.append(terapia)
        else:
            terapie_attive.append(terapia)
    
    return terapie_attive, terapie_programmate, terapie_completate


def _get_therapy_status(terapia, oggi):
    """Determina lo status di una terapia"""
    is_active = True
    status_info = {"text": "In corso", "color": "success", "icon": "play-circle"}
    
    try:
        if terapia.data_fine:
            # Converti in date se necessario
            if hasattr(terapia.data_fine, 'date'):
                data_fine_compare = terapia.data_fine.date()
            else:
                data_fine_compare = terapia.data_fine
            
            if data_fine_compare < oggi:
                is_active = False
                status_info = {"text": "Completata", "color": "secondary", "icon": "check-circle"}
        
        if terapia.data_inizio:
            # Converti in date se necessario
            if hasattr(terapia.data_inizio, 'date'):
                data_inizio_compare = terapia.data_inizio.date()
            else:
                data_inizio_compare = terapia.data_inizio
            
            if data_inizio_compare > oggi:
                status_info = {"text": "Programmata", "color": "info", "icon": "clock"}
    except:
        # Se c'è un errore nel confronto date, mantieni lo status predefinito
        pass
    
    return is_active, status_info
# Aggiungi anche questa funzione per l'alert delle assunzioni (se non c'è già):
def get_medication_alert():
    """Alert 'danger' che invita a completare le assunzioni"""
    return dbc.Alert([
        html.Span([
            html.Img(src="/assets/bell_ring.png", style={"width": "18px", "height": "18px"})
        ], className="alert-icon me-2"),
        html.Div([
            html.Strong("Promemoria assunzioni giornaliere. "),
            "Non hai ancora registrato assunzioni di farmaci per oggi. ",
            "Ricorda di registrare le tue assunzioni usando il pulsante ", 
            html.Em("Nuova Assunzione"), " qui sotto."
        ], style={"display": "inline"})
    ], color="danger", className="d-flex align-items-center alert-medication")

def get_contact_doctor_view():
    """Vista per contattare il medico di base"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Contatta il tuo Medico di Base", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            html.Div(id="doctor-contact-info"),
            _create_back_button("btn-torna-menu-messaggi")
        ])
    ], className="mt-3")


def get_doctor_contact_display(medico):
    """Visualizza le informazioni di contatto del medico"""
    if not medico:
        return dbc.Alert([
            html.H5("Medico non assegnato", className="alert-heading"),
            html.P("Non hai ancora un medico di riferimento assegnato."),
            html.P("Contatta gli amministartori per l'assegnazione di un medico di base.", className="text-muted")
        ], color="warning", className="mt-3")
    
    medico_nome_completo = f"Dr. {medico.name} {medico.surname}"
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Img(src="/assets/doctor.png", 
                        style={"width": "60px", "height": "60px", "margin-right": "15px"}),
                html.Div([
                    html.H4(medico_nome_completo, className="text-primary mb-2"),
                    html.P("Il tuo medico di base", className="text-muted mb-0")
                ], style={"display": "inline-block", "vertical-align": "top"})
            ], className="d-flex align-items-center mb-4"),
            
            dbc.Alert([
                html.H6("Informazioni di contatto:", className="alert-heading mb-3"),
                html.Div([
                    html.Strong("Email: "),
                    html.Span(medico.email, className="me-3"),
                    html.A([
                        html.Img(src="/assets/gmail.png", 
                                style={"width": "32px", "height": "32px", "margin-right": "8px"}),
                        "Invia Email"
                    ], 
                    href=f"https://mail.google.com/mail/?view=cm&fs=1&to={medico.email}&su=Richiesta%20assistenza%20medica&body=Gentile%20{medico_nome_completo},%0D%0A%0D%0AHo%20bisogno%20della%20sua%20assistenza%20per%20quanto%20riguarda:%0D%0A%0D%0A[Descrivi%20qui%20il%20tuo%20problema%20o%20domanda]%0D%0A%0D%0ADistinti%20saluti", 
                    target="_blank",
                    className="btn btn-outline-primary btn-sm d-inline-flex align-items-center text-decoration-none")
                ], className="d-flex align-items-center mb-2"),
                html.P("Clicca sul bottone Gmail per intergire con il tuo medico di riferimento", 
                       className="text-muted small")
            ], color="info", className="mb-3"),
        ])
    ], className="mt-3", style={"border-left": "4px solid #0d6efd"})