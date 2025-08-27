# view/doctor.py
"""Dashboard e layout per i medici"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date

def get_doctor_dashboard(username):
    """Dashboard per i medici"""
    return dbc.Container([
        # Header con logo
        html.Img(
            src="/assets/health.png",
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "width": "150px",
                "height": "auto",
                "z-index": "1000"
            }
        ),
        
        dbc.Row([
            dbc.Col([
                html.H2(f"Benvenuto/a Dr. {username}", 
                       className="gradient-title text-center",
                       style={
                           "margin-top": "20px",
                           "margin-bottom": "30px",
                           "color": "white",
                           "text-shadow": "2px 2px 4px rgba(0,0,0,0.3)"
                       })
            ], width=12)
        ]),
        
        # Link logout in alto a sinistra
        dcc.Link("Logout", 
               href="/logout", 
               style={
                   "position": "fixed",
                   "top": "20px",
                   "left": "20px",
                   "color": "white",
                   "text-decoration": "none",
                   "font-weight": "600",
                   "font-size": "16px",
                   "background": "rgba(16, 185, 129, 1)",
                   "padding": "10px 20px",
                   "border-radius": "25px",
                   "backdrop-filter": "blur(10px)",
                   "border": "1px solid rgba(255, 255, 255, 0.2)",
                   "z-index": "1000"
               }),
        
        # Contenuto principale
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
                        
                        # Prima riga di bottoni
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.Img(src="/assets/terapia.png", 
                                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                                        "Gestisci Terapie"
                                    ],
                                    id="btn-gestisci-terapie",
                                    className="btn-primary w-100",
                                    size="lg"
                                )
                            ], width=12, md=6, className="mb-3"),
                            
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.Img(src="/assets/dati.png", 
                                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                                        "Dati Pazienti"
                                    ],
                                    id="btn-dati-paziente",
                                    className="btn-success w-100",
                                    size="lg"
                                )
                            ], width=12, md=6, className="mb-3")
                        ]),
                        
                        # Seconda riga di bottoni
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.Img(src="/assets/segui.png", 
                                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                                        "Segui un nuovo paziente"
                                    ],
                                    id="btn-segui-pazienti",
                                    className="btn-success w-100",
                                    size="lg"
                                )
                            ], width=12, md=6, className="mb-3"),
                            
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.Img(src="/assets/grafico.png", 
                                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                                        "Andamenti glicemici"
                                    ],
                                    id="btn-statistiche",
                                    className="btn-success w-100",
                                    size="lg"
                                )
                            ], width=12, md=6, className="mb-3")
                        ]),
                        
                        # Area per messaggi/feedback
                        html.Div(id="doctor-feedback", className="mt-3")
                    ])
                ]),
                
                # Area dove appare il form/contenuto
                html.Div(id="doctor-content", className="mt-3")
                
            ], width=8)
        ], justify="center", className="mt-4")
    ], fluid=True, className="main-container")

def get_terapie_menu():
    """Menu delle opzioni per gestire le terapie"""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5("Gestione Terapie", className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            html.P("Seleziona l'azione che desideri eseguire:", className="card-text mb-4"),
            
            # Bottoni del menu terapie
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Assegna Nuova Terapia",
                        id="btn-assegna-terapia",
                        className="btn-primary w-100 mb-3",
                        size="lg"
                    ),
                    html.Small("Assegna una nuova terapia farmacologica a un paziente", 
                             className="text-muted d-block text-center")
                ], width=12, className="mb-4")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Modifica Terapia",
                        id="btn-modifica-terapia",
                        className="btn-success w-100 mb-3",
                        size="lg"
                    ),
                    html.Small("Modifica una terapia esistente", 
                             className="text-muted d-block text-center")
                ], width=12, className="mb-4")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Elimina Terapia",
                        id="btn-elimina-terapia",
                        className="btn-red w-100 mb-3",
                        size="lg"
                    ),
                    html.Small("Rimuovi una terapia non più necessaria", 
                             className="text-muted d-block text-center")
                ], width=12, className="mb-4")
            ]),
            
            # Bottone per tornare indietro
            html.Hr(),
            dbc.Button(
                "Torna al Menu Principale",
                id="btn-torna-menu-principale",
                color="info",
                size="sm",
                className="btn-info"
            )
        ])
    ], className="mt-3")

def get_assegna_terapia_form(pazienti):
    """Form per assegnare una terapia a un paziente"""
    # Prepara le opzioni per il dropdown pazienti
    pazienti_options = [
        {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
        for p in pazienti
    ]
    
    if not pazienti_options:
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Assegnazione Terapia", className="mb-0 text-primary")
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.H5("Nessun paziente trovato", className="alert-heading"),
                    html.P("Non hai ancora pazienti assegnati. Contatta l'amministratore per associare pazienti al tuo profilo."),
                    html.Hr(),
                    dbc.Button(
                        "Torna al Menu Terapie",
                        id="btn-torna-menu-terapie",
                        color="warning",
                        size="sm"
                    )
                ], color="warning")
            ])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Assegnazione Nuova Terapia", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            # Selezione paziente
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona Paziente *", className="form-label"),
                    dbc.Select(
                        id="select-paziente-terapia",
                        options=pazienti_options,
                        placeholder="Seleziona il paziente...",
                        className="form-control"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Nome farmaco e dosaggio
            dbc.Row([
                dbc.Col([
                    dbc.Label("Nome del farmaco *", className="form-label"),
                    dbc.Input(
                        id="input-nome-farmaco-terapia",
                        type="text",
                        placeholder="es. Metformina, Insulina...",
                        className="form-control"
                    )
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Dosaggio per assunzione *", className="form-label"),
                    dbc.Input(
                        id="input-dosaggio-terapia",
                        type="text",
                        placeholder="es. 500mg, 1 compressa, 10 UI...",
                        className="form-control"
                    )
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Assunzioni giornaliere
            dbc.Row([
                dbc.Col([
                    dbc.Label("Numero di assunzioni giornaliere *", className="form-label"),
                    dbc.Input(
                        id="input-assunzioni-giornaliere",
                        type="number",
                        min=1,
                        max=10,
                        step=1,
                        placeholder="es. 2",
                        className="form-control"
                    )
                ], width=12, md=6),
                
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
                            {"label": "Secondo necessità", "value": "secondo_necessita"}
                        ],
                        placeholder="Seleziona indicazioni...",
                        className="form-control"
                    )
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Date inizio e fine
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data inizio terapia *", className="form-label"),
                    dbc.Input(
                        id="input-data-inizio-terapia",
                        type="date",
                        value=date.today().strftime('%Y-%m-%d'),
                        className="form-control"
                    ),
                    dbc.FormText("Lascia la data odierna se deve iniziare oggi", className="text-muted")
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Data fine terapia (se applicabile)", className="form-label"),
                    dbc.Input(
                        id="input-data-fine-terapia",
                        type="date",
                        className="form-control"
                    ),
                    dbc.FormText("Lascia vuoto per terapia continuativa", className="text-muted")
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Indicazioni aggiuntive personalizzate
            dbc.Row([
                dbc.Col([
                    dbc.Label("Indicazioni aggiuntive", className="form-label"),
                    dbc.Textarea(
                        id="textarea-indicazioni-terapia",
                        placeholder="es. Assumere con abbondante acqua, non assumere se glicemia < 80 mg/dL...",
                        rows=3,
                        className="form-control"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Note
            dbc.Row([
                dbc.Col([
                    dbc.Label("Note (opzionale)", className="form-label"),
                    dbc.Textarea(
                        id="textarea-note-terapia",
                        placeholder="Eventuali note aggiuntive per il paziente...",
                        rows=2,
                        className="form-control"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Pulsanti
            html.Div([
                dbc.Button(
                    "Assegna Terapia",
                    id="btn-salva-terapia",
                    color="success",
                    size="lg",
                    className="me-2"
                ),
                dbc.Button(
                    "Torna al Menu Terapie",
                    id="btn-torna-menu-terapie",
                    color="info",
                    size="lg",
                    className="btn-info"
                )
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_modifica_terapia_form(pazienti):
    """Form per modificare una terapia esistente"""
    # Prepara le opzioni per il dropdown pazienti
    pazienti_options = [
        {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
        for p in pazienti
    ]
    
    if not pazienti_options:
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Modifica Terapia", className="mb-0 text-primary")
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.H5("Nessun paziente trovato", className="alert-heading"),
                    html.P("Non hai ancora pazienti assegnati. Contatta l'amministratore per associare pazienti al tuo profilo."),
                    html.Hr(),
                    dbc.Button(
                        "Torna al Menu Terapie",
                        id="btn-torna-menu-terapie",
                        color="warning",
                        size="sm"
                    )
                ], color="warning")
            ])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Modifica Terapia Esistente", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            # Prima step: selezione paziente per vedere le sue terapie
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona Paziente *", className="form-label"),
                    dbc.Select(
                        id="select-paziente-modifica",
                        options=pazienti_options,
                        placeholder="Seleziona il paziente...",
                        className="form-control"
                    ),
                    dbc.FormText("Seleziona un paziente per visualizzare le sue terapie attive", className="text-muted")
                ], width=12)
            ], className="mb-3"),
            
            # Area dove appariranno le terapie del paziente selezionato
            html.Div(id="terapie-paziente-list", className="mt-3"),
            
            # Pulsanti
            html.Div([
                dbc.Button(
                    "Torna al Menu Terapie",
                    id="btn-torna-menu-terapie",
                    color="info",
                    size="lg",
                    className="btn-info w-100"
                )
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_elimina_terapia_form(pazienti):
    """Form per eliminare una terapia esistente"""
    # Prepara le opzioni per il dropdown pazienti
    pazienti_options = [
        {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
        for p in pazienti
    ]
    
    if not pazienti_options:
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Elimina Terapia", className="mb-0 text-primary")
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.H5("Nessun paziente trovato", className="alert-heading"),
                    html.P("Non hai ancora pazienti assegnati. Contatta l'amministratore per associare pazienti al tuo profilo."),
                    html.Hr(),
                    dbc.Button(
                        "Torna al Menu Terapie",
                        id="btn-torna-menu-terapie",
                        color="danger",
                        size="sm"
                    )
                ], color="warning")
            ])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Elimina Terapia", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            dbc.Alert([
                html.Strong("⚠️ Attenzione: "),
                "L'eliminazione di una terapia è un'azione irreversibile. Assicurati di voler procedere."
            ], color="warning", className="mb-4"),
            
            # Prima step: selezione paziente per vedere le sue terapie
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona Paziente *", className="form-label"),
                    dbc.Select(
                        id="select-paziente-elimina",
                        options=pazienti_options,
                        placeholder="Seleziona il paziente...",
                        className="form-control"
                    ),
                    dbc.FormText("Seleziona un paziente per visualizzare le sue terapie attive", className="text-muted")
                ], width=12)
            ], className="mb-3"),
            
            # Area dove appariranno le terapie del paziente selezionato
            html.Div(id="terapie-paziente-elimina-list", className="mt-3"),
            
            # Pulsanti
            html.Div([
                dbc.Button(
                    "Torna al Menu Terapie",
                    id="btn-torna-menu-terapie",
                    color="info",
                    size="lg",
                    className="btn-info w-100"
                )
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_terapia_success_message(paziente_nome, nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine=None):
    """Messaggio di successo dopo assegnazione terapia"""
    children = [
        html.H5("Terapia assegnata con successo!", className="alert-heading"),
        html.P(f"Paziente: {paziente_nome}"),
        html.P(f"Farmaco: {nome_farmaco}"),
        html.P(f"Dosaggio: {dosaggio}"),
        html.P(f"Assunzioni giornaliere: {assunzioni_giornaliere}"),
        html.P(f"Data inizio: {data_inizio.strftime('%d/%m/%Y')}")
    ]
    
    if data_fine:
        children.append(html.P(f"Data fine: {data_fine.strftime('%d/%m/%Y')}"))
    else:
        children.append(html.P("Durata: Terapia continuativa"))
    
    children.extend([
        html.Hr(),
        # Layout con pulsanti separati per migliore spaziatura
        dbc.Row([
            dbc.Col([
                dbc.Button("Assegna nuova terapia", 
                         id="btn-nuova-terapia", 
                         color="primary", 
                         size="sm",
                         className="w-100")
            ], width=6),
            dbc.Col([
                dbc.Button("Torna al Menu Terapie", 
                         id="btn-torna-menu-terapie", 
                         color="info", 
                         size="lg",
                         className="btn-info w-100")
            ], width=6)
        ], className="g-3")  # g-3 aggiunge spaziatura tra le colonne
    ])
    
    return dbc.Alert(children, color="success", dismissable=True)

def get_error_message(message):
    """Messaggio di errore generico"""
    return dbc.Alert(message, color="danger", dismissable=True)

def get_indicazioni_display(indicazioni):
    """Converte il codice indicazioni in testo leggibile"""
    mapping = {
        "prima_pasti": "Prima dei pasti",
        "dopo_pasti": "Dopo i pasti", 
        "lontano_pasti": "Lontano dai pasti",
        "mattino": "Al mattino",
        "sera": "Alla sera",
        "secondo_necessita": "Secondo necessità"
    }
    return mapping.get(indicazioni, indicazioni)
def get_terapie_list_for_edit(terapie, paziente):
    """Lista delle terapie del paziente per la selezione in modifica"""
    terapie_cards = []
    
    for terapia in terapie:
        # Prepara le informazioni della terapia
        data_inizio_str = terapia.data_inizio.strftime('%d/%m/%Y') if terapia.data_inizio else "Non specificata"
        data_fine_str = terapia.data_fine.strftime('%d/%m/%Y') if terapia.data_fine else "Continuativa"
        
        # Info sul medico che ha modificato per ultimo
        modificata_info = ""
        if terapia.modificata:
            modificata_info = f" (Modificata da: {terapia.modificata})"
        
        # Crea la chiave composita per identificare la terapia
        # Usa il formato: medico_nome|paziente_username|nome_farmaco|data_inizio
        composite_key = f"{terapia.medico_nome}|{terapia.paziente.username}|{terapia.nome_farmaco}|{terapia.data_inizio.strftime('%Y-%m-%d') if terapia.data_inizio else 'None'}"
        
        card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6(f"{terapia.nome_farmaco}", className="card-title text-primary"),
                        html.P([
                            html.Strong("Dosaggio: "), terapia.dosaggio_per_assunzione, html.Br(),
                            html.Strong("Assunzioni giornaliere: "), str(terapia.assunzioni_giornaliere), html.Br(),
                            html.Strong("Dal: "), data_inizio_str, 
                            html.Strong(" al: ") if terapia.data_fine else html.Strong(" - "), data_fine_str, html.Br(),
                            html.Strong("Prescritto da: "), terapia.medico_nome, modificata_info
                        ], className="card-text small"),
                        
                        # Mostra indicazioni se presenti
                        html.P([
                            html.Strong("Indicazioni: "), 
                            terapia.indicazioni if terapia.indicazioni else "Nessuna indicazione specifica"
                        ], className="card-text small text-muted") if terapia.indicazioni else html.Div(),
                        
                        # Mostra note se presenti
                        html.P([
                            html.Strong("Note: "), 
                            terapia.note if terapia.note else "Nessuna nota"
                        ], className="card-text small text-muted") if terapia.note else html.Div(),
                        
                    ], width=8),
                    
                    dbc.Col([
                        dbc.Button(
                            [
                                html.I(className="fas fa-edit me-1"),
                                "Modifica"
                            ],
                            id={'type': 'btn-modifica-terapia-specifica', 'index': composite_key},
                            className="btn-modify-medical w-100",  # Usa la classe CSS personalizzata
                            size="sm"
                        )
                    ], width=4, className="d-flex align-items-center")
                ])
            ])
        ], className="mb-2", style={"border-left": "4px solid #28a745"})
        
        terapie_cards.append(card)
    
    return html.Div([
        html.Hr(),
        html.H6(f"Terapie di {paziente.name} {paziente.surname}:", className="text-primary mb-3"),
        html.Div(terapie_cards)
    ])

def get_edit_terapia_form(terapia, pazienti):
    """Form per modificare una terapia esistente con dati precompilati"""
    # Prepara le opzioni per il dropdown pazienti
    pazienti_options = [
        {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
        for p in pazienti
    ]
    
    # Crea la chiave composita della terapia - STESSO FORMATO della lista
    composite_key = f"{terapia.medico_nome}|{terapia.paziente.username}|{terapia.nome_farmaco}|{terapia.data_inizio.strftime('%Y-%m-%d') if terapia.data_inizio else 'None'}"
    
    # Determina quale indicazione è selezionata
    selected_indicazione = None
    indicazioni_custom_value = ""
    
    if terapia.indicazioni:
        # Controlla se è una delle indicazioni predefinite
        reverse_mapping = {
            "Prima dei pasti": "prima_pasti",
            "Dopo i pasti": "dopo_pasti", 
            "Lontano dai pasti": "lontano_pasti",
            "Al mattino": "mattino",
            "Alla sera": "sera",
            "Secondo necessità": "secondo_necessita"
        }
        
        # Cerca se l'indicazione corrisponde a una predefinita
        for display, value in reverse_mapping.items():
            if terapia.indicazioni.startswith(display):
                selected_indicazione = value
                # Se ci sono indicazioni aggiuntive, mettile nel campo custom
                resto = terapia.indicazioni.replace(display, "").strip()
                if resto.startswith("."):
                    resto = resto[1:].strip()
                indicazioni_custom_value = resto
                break
        
        # Se non è predefinita, metti tutto nel campo custom
        if not selected_indicazione:
            indicazioni_custom_value = terapia.indicazioni
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Modifica Terapia", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            # Campo nascosto per la chiave composita della terapia
            html.Div(id="hidden-terapia-key", children=composite_key, style={"display": "none"}),
            
            # Alert informativo
            dbc.Alert([
                html.Strong("Stai modificando: "),
                f"{terapia.nome_farmaco} per {terapia.paziente.name} {terapia.paziente.surname}"
            ], color="info", className="mb-4"),
            
            # Selezione paziente (preselezionato)
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona Paziente *", className="form-label"),
                    dbc.Select(
                        id="select-paziente-terapia-edit",
                        options=pazienti_options,
                        value=terapia.paziente.username,
                        className="form-control"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Nome farmaco e dosaggio (precompilati)
            dbc.Row([
                dbc.Col([
                    dbc.Label("Nome del farmaco *", className="form-label"),
                    dbc.Input(
                        id="input-nome-farmaco-terapia-edit",
                        type="text",
                        value=terapia.nome_farmaco,
                        placeholder="es. Metformina, Insulina...",
                        className="form-control"
                    )
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Dosaggio per assunzione *", className="form-label"),
                    dbc.Input(
                        id="input-dosaggio-terapia-edit",
                        type="text",
                        value=terapia.dosaggio_per_assunzione,
                        placeholder="es. 500mg, 1 compressa, 10 UI...",
                        className="form-control"
                    )
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Assunzioni giornaliere e indicazioni (precompilate)
            dbc.Row([
                dbc.Col([
                    dbc.Label("Numero di assunzioni giornaliere *", className="form-label"),
                    dbc.Input(
                        id="input-assunzioni-giornaliere-edit",
                        type="number",
                        min=1,
                        max=10,
                        step=1,
                        value=terapia.assunzioni_giornaliere,
                        className="form-control"
                    )
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Indicazioni", className="form-label"),
                    dbc.Select(
                        id="select-indicazioni-terapia-edit",
                        options=[
                            {"label": "Prima dei pasti", "value": "prima_pasti"},
                            {"label": "Dopo i pasti", "value": "dopo_pasti"},
                            {"label": "Lontano dai pasti", "value": "lontano_pasti"},
                            {"label": "Al mattino", "value": "mattino"},
                            {"label": "Alla sera", "value": "sera"},
                            {"label": "Secondo necessità", "value": "secondo_necessita"}
                        ],
                        value=selected_indicazione,
                        placeholder="Seleziona indicazioni...",
                        className="form-control"
                    )
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Date inizio e fine (precompilate)
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data inizio terapia *", className="form-label"),
                    dbc.Input(
                        id="input-data-inizio-terapia-edit",
                        type="date",
                        value=terapia.data_inizio.strftime('%Y-%m-%d') if terapia.data_inizio else '',
                        className="form-control"
                    )
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Data fine terapia (se applicabile)", className="form-label"),
                    dbc.Input(
                        id="input-data-fine-terapia-edit",
                        type="date",
                        value=terapia.data_fine.strftime('%Y-%m-%d') if terapia.data_fine else '',
                        className="form-control"
                    ),
                    dbc.FormText("Lascia vuoto per terapia continuativa", className="text-muted")
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Indicazioni aggiuntive personalizzate (precompilate)
            dbc.Row([
                dbc.Col([
                    dbc.Label("Indicazioni aggiuntive", className="form-label"),
                    dbc.Textarea(
                        id="textarea-indicazioni-terapia-edit",
                        placeholder="es. Assumere con abbondante acqua, non assumere se glicemia < 80 mg/dL...",
                        value=indicazioni_custom_value,
                        rows=3,
                        className="form-control"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Note (precompilate)
            dbc.Row([
                dbc.Col([
                    dbc.Label("Note (opzionale)", className="form-label"),
                    dbc.Textarea(
                        id="textarea-note-terapia-edit",
                        placeholder="Eventuali note aggiuntive per il paziente...",
                        value=terapia.note if terapia.note else '',
                        rows=2,
                        className="form-control"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Pulsanti
            html.Div([
                dbc.Button(
                    "Salva Modifiche",
                    id="btn-salva-modifiche-terapia",
                    color="success",
                    size="lg",
                    className="me-2"
                ),
                dbc.Button(
                    "Torna al Menu Terapie",
                    id="btn-torna-menu-terapie",
                    color="info",
                    size="lg",
                    className="btn-info"
                )
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_terapia_modify_success_message(paziente_nome, nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine=None):
    """Messaggio di successo dopo modifica terapia"""
    children = [
        html.H5("Terapia modificata con successo!", className="alert-heading"),
        html.P(f"Paziente: {paziente_nome}"),
        html.P(f"Farmaco: {nome_farmaco}"),
        html.P(f"Dosaggio: {dosaggio}"),
        html.P(f"Assunzioni giornaliere: {assunzioni_giornaliere}"),
        html.P(f"Data inizio: {data_inizio.strftime('%d/%m/%Y')}")
    ]
    
    if data_fine:
        children.append(html.P(f"Data fine: {data_fine.strftime('%d/%m/%Y')}"))
    else:
        children.append(html.P("Durata: Terapia continuativa"))
    
    children.extend([
        html.Hr(),
        # Layout con pulsanti separati per migliore spaziatura
        dbc.Row([
            dbc.Col([
                dbc.Button("Modifica altra terapia", 
                         id="btn-modifica-altra-terapia", 
                         color="primary", 
                         size="sm",
                         className="w-100")
            ], width=6),
            dbc.Col([
                dbc.Button("Torna al Menu Terapie", 
                         id="btn-torna-menu-terapie", 
                         color="info", 
                         size="lg",
                         className="btn-info w-100")
            ], width=6)
        ], className="g-3")  # g-3 aggiunge spaziatura tra le colonne
    ])
    
    return dbc.Alert(children, color="success", dismissable=True)

# Aggiungi queste funzioni al file view/doctor.py

def get_terapie_list_for_delete(terapie, paziente):
    """Lista delle terapie del paziente per la selezione in eliminazione"""
    terapie_cards = []
    
    for terapia in terapie:
        # Prepara le informazioni della terapia
        data_inizio_str = terapia.data_inizio.strftime('%d/%m/%Y') if terapia.data_inizio else "Non specificata"
        data_fine_str = terapia.data_fine.strftime('%d/%m/%Y') if terapia.data_fine else "Continuativa"
        
        # Info sul medico che ha modificato per ultimo
        modificata_info = ""
        if terapia.modificata:
            modificata_info = f" (Modificata da: {terapia.modificata})"
        
        # Crea la chiave composita per identificare la terapia (stesso formato delle altre funzioni)
        composite_key = f"{terapia.medico_nome}|{terapia.paziente.username}|{terapia.nome_farmaco}|{terapia.data_inizio.strftime('%Y-%m-%d') if terapia.data_inizio else 'None'}"
        
        card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6(f"{terapia.nome_farmaco}", className="card-title text-primary"),
                        html.P([
                            html.Strong("Dosaggio: "), terapia.dosaggio_per_assunzione, html.Br(),
                            html.Strong("Assunzioni giornaliere: "), str(terapia.assunzioni_giornaliere), html.Br(),
                            html.Strong("Dal: "), data_inizio_str, 
                            html.Strong(" al: ") if terapia.data_fine else html.Strong(" - "), data_fine_str, html.Br(),
                            html.Strong("Prescritto da: "), terapia.medico_nome, modificata_info
                        ], className="card-text small"),
                        
                        # Mostra indicazioni se presenti
                        html.P([
                            html.Strong("Indicazioni: "), 
                            terapia.indicazioni if terapia.indicazioni else "Nessuna indicazione specifica"
                        ], className="card-text small text-muted") if terapia.indicazioni else html.Div(),
                        
                        # Mostra note se presenti
                        html.P([
                            html.Strong("Note: "), 
                            terapia.note if terapia.note else "Nessuna nota"
                        ], className="card-text small text-muted") if terapia.note else html.Div(),
                        
                    ], width=8),
                    
                    dbc.Col([
                        dbc.Button(
                            [
                                html.I(className="fas fa-trash me-1"),
                                "Elimina"
                            ],
                            id={'type': 'btn-elimina-terapia-specifica', 'index': composite_key},
                            color="danger",
                            size="sm",
                            className="w-100"
                        )
                    ], width=4, className="d-flex align-items-center")
                ])
            ])
        ], className="mb-2", style={"border-left": "4px solid #dc3545"})  # Bordo rosso per distinguere dall'eliminazione
        
        terapie_cards.append(card)
    
    return html.Div([
        html.Hr(),
        dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Strong("Attenzione: "),
            "Stai per eliminare una terapia. Questa azione è irreversibile!"
        ], color="warning", className="mb-3"),
        html.H6(f"Terapie di {paziente.name} {paziente.surname}:", className="text-danger mb-3"),
        html.P("Seleziona la terapia da eliminare:", className="text-muted mb-3"),
        html.Div(terapie_cards)
    ])

def get_terapia_delete_success_message(paziente_nome, nome_farmaco, dosaggio):
    """Messaggio di successo dopo eliminazione terapia"""
    children = [
        html.I(className="fas fa-check-circle fa-2x text-success mb-3"),
        html.H5("Terapia eliminata con successo!", className="alert-heading"),
        html.P(f"È stata eliminata la seguente terapia:"),
        html.Ul([
            html.Li(f"Paziente: {paziente_nome}"),
            html.Li(f"Farmaco: {nome_farmaco}"),
            html.Li(f"Dosaggio: {dosaggio}")
        ]),
        html.P("La terapia è stata rimossa definitivamente dal sistema.", className="text-muted"),
        html.Hr(),
        # Layout con pulsanti separati per migliore spaziatura
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-trash me-2"),
                        "Elimina altra terapia"
                    ], 
                    id="btn-elimina-altra-terapia", 
                    color="danger", 
                    size="sm",
                    className="w-100"
                )
            ], width=6),
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-arrow-left me-2"),
                        "Torna al Menu Terapie"
                    ], 
                    id="btn-torna-menu-terapie", 
                    color="info", 
                    size="lg",
                    className="btn-info w-100"
                )
            ], width=6)
        ], className="g-3")  # g-3 aggiunge spaziatura tra le colonne
    ]
    
    return dbc.Alert(children, color="success", dismissable=True)

def get_dati_pazienti_menu(pazienti):
    """Menu per selezionare il paziente di cui visualizzare i dati"""
    # Prepara le opzioni per il dropdown pazienti
    pazienti_options = [
        {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
        for p in pazienti
    ]
    
    if not pazienti_options:
        return dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H5("Dati Pazienti", className="mb-0 text-primary", style={"display": "inline-block"})
                ])
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.H5("Nessun paziente trovato", className="alert-heading"),
                    html.P("Non hai ancora pazienti assegnati. Contatta l'amministratore per associare pazienti al tuo profilo."),
                    html.Hr(),
                    dbc.Button(
                        "Torna al Menu Principale",
                        id="btn-torna-menu-principale",
                        color="warning",
                        size="sm"
                    )
                ], color="warning")
            ])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5("Dati Pazienti", className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            html.P("Seleziona il paziente di cui vuoi visualizzare o modificare i dati clinici:", className="card-text mb-4"),
            
            # Selezione paziente
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona Paziente *", className="form-label"),
                    dbc.Select(
                        id="select-paziente-dati",
                        options=pazienti_options,
                        placeholder="Seleziona il paziente...",
                        className="form-control"
                    ),
                    dbc.FormText("Seleziona un paziente per visualizzare i suoi dati clinici", className="text-muted")
                ], width=12)
            ], className="mb-3"),
            
            # Area dove appariranno i dati del paziente selezionato
            html.Div(id="dati-paziente-display", className="mt-3"),
        ])
    ], className="mt-3")

def get_patient_data_display(paziente, can_modify=True):
    """Visualizza i dati clinici del paziente con opzione di modifica"""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.Img(src="/assets/patient.png", 
                       style={"width": "30px", "height": "30px", "margin-right": "8px"}),
                html.H6(f"Dati Clinici - {paziente.name} {paziente.surname}", 
                       className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            # Informazioni di base del paziente
            dbc.Row([
                dbc.Col([
                    html.H6("Informazioni Generali", className="text-secondary mb-3"),
                    html.P([
                        html.Strong("Nome Completo: "), f"{paziente.name} {paziente.surname}", html.Br(),
                        html.Strong("Username: "), paziente.username, html.Br(),
                        html.Strong("Data di Nascita: "), 
                        paziente.birth_date.strftime('%d/%m/%Y') if paziente.birth_date else "Non specificata", html.Br(),
                        html.Strong("Età: "), f"{paziente.eta} anni" if paziente.eta else "Non specificata", html.Br(),
                        html.Strong("Codice Fiscale: "), paziente.codice_fiscale if paziente.codice_fiscale else "Non specificato"
                    ], className="card-text")
                ], width=12, md=6),
                
                dbc.Col([
                    html.H6("Dati Clinici", className="text-secondary mb-3"),
                    html.P([
                        html.Strong("Fattori di Rischio: "), html.Br(),
                        html.Span(paziente.fattori_rischio if paziente.fattori_rischio else "Nessun fattore di rischio specificato", 
                                className="text-muted" if not paziente.fattori_rischio else ""), html.Br(), html.Br(),
                        
                        html.Strong("Pregresse Patologie: "), html.Br(),
                        html.Span(paziente.pregresse_patologie if paziente.pregresse_patologie else "Nessuna patologia pregressa specificata", 
                                className="text-muted" if not paziente.pregresse_patologie else ""), html.Br(), html.Br(),
                        
                        html.Strong("Comorbidità: "), html.Br(),
                        html.Span(paziente.comorbidita if paziente.comorbidita else "Nessuna comorbidità specificata", 
                                className="text-muted" if not paziente.comorbidita else ""), html.Br(), html.Br(),
                    ], className="card-text")
                ], width=12, md=6)
            ], className="mb-4"),
            
            # Sezione informazioni sulla modifica (solo se presente)
            html.Div([
                html.Hr(),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Ultima modifica effettuata da: "),
                    html.Span(paziente.info_aggiornate, className="fw-bold")
                ], color="info", className="mb-3")
            ]) if paziente.info_aggiornate else html.Div(),
            
            # Alert se il medico non può modificare i dati
            html.Div([
                html.Hr() if paziente.info_aggiornate else html.Div(),
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    html.Strong("Accesso limitato: "),
                    "Non sei autorizzato a modificare i dati clinici di questo paziente. Solo i medici che seguono il paziente possono modificare i suoi dati."
                ], color="warning", className="mb-3")
            ]) if not can_modify else html.Div(),
            
            # Bottoni per le azioni
            html.Hr() if (not paziente.info_aggiornate and can_modify) else html.Div(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [
                            html.I(className="fas fa-edit me-2"),
                            "Modifica Dati Clinici"
                        ],
                        id="btn-modifica-dati-paziente",
                        color="primary",
                        size="lg",
                        className="w-100",
                        disabled=not can_modify  # Disabilita se non può modificare
                    )
                ], width=12, md=4),
                
                dbc.Col([
                    dbc.Button(
                        [
                            html.I(className="fas fa-user-plus me-2"),
                            "Seleziona Altro Paziente"
                        ],
                        id="btn-altro-paziente",
                        color="primary",
                        size="lg",
                        className="w-100"
                    )
                ], width=12, md=4),
                
                dbc.Col([
                    dbc.Button(
                        [
                            html.I(className="fas fa-arrow-left me-2"),
                            "Torna al Menu"
                        ],
                        id="btn-torna-menu-principale",
                        color="info",
                        size="lg",
                        className="btn-info w-100"
                    )
                ], width=12, md=4)
            ], className="g-3")
        ])
    ], className="mt-3")


def get_edit_patient_data_form(paziente):
    """Form per modificare i dati clinici del paziente"""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-user-edit fa-lg me-2"),
                html.H5(f"Modifica Dati Clinici - {paziente.name} {paziente.surname}", 
                       className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            # Campo nascosto per l'username del paziente
            html.Div(id="hidden-patient-username", children=paziente.username, style={"display": "none"}),
            
            # Alert informativo
            dbc.Alert([
                html.Strong("Stai modificando i dati clinici di: "),
                f"{paziente.name} {paziente.surname} ({paziente.username})"
            ], color="info", className="mb-4"),
            
            # Fattori di rischio
            dbc.Row([
                dbc.Col([
                    dbc.Label("Fattori di Rischio", className="form-label"),
                    dbc.Textarea(
                        id="textarea-fattori-rischio",
                        placeholder="es. Diabete familiare, ipertensione, obesità, fumo...",
                        value=paziente.fattori_rischio if paziente.fattori_rischio else '',
                        rows=3,
                        className="form-control"
                    ),
                    dbc.FormText("Elenca i principali fattori di rischio del paziente", className="text-muted")
                ], width=12)
            ], className="mb-3"),
            
            # Pregresse patologie
            dbc.Row([
                dbc.Col([
                    dbc.Label("Pregresse Patologie", className="form-label"),
                    dbc.Textarea(
                        id="textarea-pregresse-patologie",
                        placeholder="es. Infarto del miocardio 2020, bypass coronarico 2018...",
                        value=paziente.pregresse_patologie if paziente.pregresse_patologie else '',
                        rows=3,
                        className="form-control"
                    ),
                    dbc.FormText("Elenca le principali patologie pregresse del paziente", className="text-muted")
                ], width=12)
            ], className="mb-3"),
            
            # Comorbidità
            dbc.Row([
                dbc.Col([
                    dbc.Label("Comorbidità", className="form-label"),
                    dbc.Textarea(
                        id="textarea-comorbidita",
                        placeholder="es. Insufficienza renale cronica, BPCO, depressione...",
                        value=paziente.comorbidita if paziente.comorbidita else '',
                        rows=3,
                        className="form-control"
                    ),
                    dbc.FormText("Elenca le comorbidità attuali del paziente", className="text-muted")
                ], width=12)
            ], className="mb-3"),
            
            
            # Note informative
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                html.Strong("Nota: "),
                "I campi possono essere lasciati vuoti se non applicabili. Le modifiche saranno salvate immediatamente."
            ], color="info", className="mb-4"),
            
            # Pulsanti
            html.Div([
                dbc.Button(
                    [
                        html.I(className="fas fa-save me-2"),
                        "Salva Modifiche"
                    ],
                    id="btn-salva-dati-paziente",
                    color="primary",
                    size="lg",
                    className="me-2"
                ),
                dbc.Button(
                    [
                        html.I(className="fas fa-times me-2"),
                        "Annulla"
                    ],
                    id="btn-annulla-modifica-dati",
                    color="secondary",
                    size="lg"
                )
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_patient_data_update_success_message(paziente_nome):
    """Messaggio di successo dopo aggiornamento dati paziente"""
    children = [
        html.I(className="fas fa-check-circle fa-2x text-success mb-3"),
        html.H5("Dati clinici aggiornati con successo!", className="alert-heading"),
        html.P(f"I dati clinici di {paziente_nome} sono stati aggiornati correttamente."),
        html.P("Le modifiche sono state salvate nel sistema.", className="text-muted"),
        html.Hr(),
        # Layout con pulsanti separati
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-eye me-2"),
                        "Visualizza Dati Aggiornati"
                    ], 
                    id="btn-visualizza-dati-aggiornati", 
                    color="primary", 
                    size="sm",
                    className="w-100"
                )
            ], width=6),
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-users me-2"),
                        "Gestisci Altri Pazienti"
                    ], 
                    id="btn-gestisci-altri-pazienti", 
                    color="primary", 
                    size="sm",
                    className="w-100"
                )
            ], width=6)
        ], className="g-3 mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-arrow-left me-2"),
                        "Torna al Menu Principale"
                    ], 
                    id="btn-torna-menu-principale", 
                    color="info", 
                    size="lg",
                    className="btn-info w-100"
                )
            ], width=12)
        ])
    ]
    
    return dbc.Alert(children, color="success", dismissable=True)

def get_segui_paziente_form(tutti_pazienti, pazienti_seguiti):
    """Form per seguire un nuovo paziente"""
    # Prepara le opzioni per il dropdown - solo pazienti non ancora seguiti
    pazienti_non_seguiti = [
        p for p in tutti_pazienti 
        if p not in pazienti_seguiti
    ]
    
    pazienti_options = [
        {"label": f"{p.name} {p.surname} ({p.username})", "value": p.username} 
        for p in pazienti_non_seguiti
    ]
    
    if not pazienti_options:
        return dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H5("Segui Nuovo Paziente", className="mb-0 text-primary", style={"display": "inline-block"})
                ])
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.H5("Nessun nuovo paziente disponibile", className="alert-heading"),
                    html.P("Stai già seguendo tutti i pazienti disponibili nel sistema."),
                    html.Hr(),
                    dbc.Button(
                        "Torna al Menu Principale",
                        id="btn-torna-menu-principale",
                        color="info",
                        size="sm",
                        className="btn-info"
                    )
                ], color="info")
            ])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.Img(src="/assets/segui.png", 
                       style={"width": "40px", "height": "40px", "margin-right": "10px"}),
                html.H5("Segui Nuovo Paziente", className="mb-0 text-primary", style={"display": "inline-block"})
            ])
        ]),
        dbc.CardBody([
            html.P("Seleziona il paziente che vuoi iniziare a seguire:", className="card-text mb-4"),
            
            # Informazioni sui pazienti attualmente seguiti
            html.Div([
                html.H6("Pazienti che segui attualmente:", className="text-secondary mb-2"),
                html.Ul([
                    html.Li(f"{p.name} {p.surname} ({p.username})") 
                    for p in pazienti_seguiti
                ]) if pazienti_seguiti else html.P("Non segui ancora nessun paziente.", className="text-muted"),
                html.Hr()
            ]),
            
            # Selezione nuovo paziente
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona Nuovo Paziente *", className="form-label"),
                    dbc.Select(
                        id="select-nuovo-paziente",
                        options=pazienti_options,
                        placeholder="Seleziona il paziente da seguire...",
                        className="form-control"
                    ),
                    dbc.FormText("Seleziona un paziente per iniziare a seguirlo", className="text-muted")
                ], width=12)
            ], className="mb-4"),
            
            # Note informative
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                html.Strong("Nota: "),
                "Una volta che inizi a seguire un paziente, potrai gestire le sue terapie e modificare i suoi dati clinici."
            ], color="info", className="mb-4"),
            
            # Pulsanti
            html.Div([
                dbc.Button(
                    [
                        html.I(className="fas fa-user-plus me-2"),
                        "Inizia a Seguire"
                    ],
                    id="btn-conferma-segui-paziente",
                    color="success",
                    size="lg",
                    className="btn-primary"
                ),
                dbc.Button(
                    [
                        html.I(className="fas fa-arrow-left me-2"),
                        "Torna al Menu"
                    ],
                    id="btn-torna-menu-principale",
                    color="info",
                    size="lg",
                    className="btn-info ms-2"
                )
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_segui_paziente_success_message(paziente_nome, paziente_username):
    """Messaggio di successo dopo aver iniziato a seguire un paziente"""
    children = [
        html.I(className="fas fa-check-circle fa-2x text-success mb-3"),
        html.H5("Paziente aggiunto con successo!", className="alert-heading"),
        html.P(f"Ora stai seguendo: {paziente_nome} ({paziente_username})"),
        html.P("Puoi ora gestire le sue terapie e visualizzare i suoi dati clinici.", className="text-muted"),
        html.Hr(),
        # Layout con pulsanti separati
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-user-plus me-2"),
                        "Segui Altro Paziente"
                    ], 
                    id="btn-segui-altro-paziente", 
                    color="primary", 
                    size="lg",
                    className="w-100"
                )
            ], width=6),
        ], className="g-3 mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-arrow-left me-2"),
                        "Torna al Menu Principale"
                    ], 
                    id="btn-torna-menu-principale", 
                    color="info", 
                    size="lg",
                    className="btn-info"
                )
            ], width=12)
        ])
    ]
    
    return dbc.Alert(children, color="success", dismissable=True)

def get_paziente_gia_seguito_message(paziente_nome):
    """Messaggio quando si tenta di seguire un paziente già seguito"""
    children = [
        html.I(className="fas fa-info-circle fa-2x text-info mb-3"),
        html.H5("Paziente già seguito", className="alert-heading"),
        html.P(f"Stai già seguendo il paziente: {paziente_nome}"),
        html.P("Non è necessario aggiungerlo nuovamente.", className="text-muted"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-user-plus me-2"),
                        "Segui Altro Paziente"
                    ], 
                    id="btn-segui-altro-paziente", 
                    color="success", 
                    size="sm",
                    className="w-100"
                )
            ], width=6),
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-arrow-left me-2"),
                        "Torna al Menu"
                    ], 
                    id="btn-torna-menu-principale", 
                    color="info", 
                    size="lg",
                    className="btn-info w-100"
                )
            ], width=6)
        ], className="g-3")
    ]
    
    return dbc.Alert(children, color="info", dismissable=True)

    