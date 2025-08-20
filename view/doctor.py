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
                                        "Assegna Terapia"
                                    ],
                                    id="btn-assegna-terapia",
                                    className="btn-primary w-100",
                                    size="lg"
                                )
                            ], width=12, md=6, className="mb-3"),
                            
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.Img(src="/assets/pazienti.png", 
                                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                                        "Gestisci Pazienti"
                                    ],
                                    id="btn-gestisci-pazienti",
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
                                        html.Img(src="/assets/report.png", 
                                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                                        "Report Pazienti"
                                    ],
                                    id="btn-report-pazienti",
                                    className="btn-success w-100",
                                    size="lg"
                                )
                            ], width=12, md=6, className="mb-3"),
                            
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.Img(src="/assets/statistiche.png", 
                                               style={"width": "35px", "height": "35px", "margin-right": "8px"}),
                                        "Statistiche"
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
                    html.P("Non hai ancora pazienti assegnati. Contatta l'amministratore per associare pazienti al tuo profilo.")
                ], color="warning")
            ])
        ], className="mt-3")
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Assegnazione Terapia", className="mb-0 text-primary")
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
                    "Annulla",
                    id="btn-annulla-terapia",
                    color="secondary",
                    size="lg"
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
        dbc.Button("Assegna nuova terapia", 
                 id="btn-nuova-terapia", 
                 color="primary", 
                 size="sm")
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