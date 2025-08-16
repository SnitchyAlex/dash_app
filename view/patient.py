#view/patient.py
"""Dashboard e layout per i pazienti"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date

def get_patient_dashboard(username):
    """Dashboard per i pazienti"""
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
                html.H2(f"Benvenuto/a {username}", 
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
                            html.Img(src="/assets/patient.png", 
                                   style={"width": "40px", "height": "40px", "margin-right": "10px"}),
                            html.H4("Area Paziente", className="mb-0 patient-title", style={"display": "inline-block"})
                        ])
                    ]),
                    dbc.CardBody([
                        html.P("Benvenuto nella tua area personale. Qui puoi registrare i tuoi dati sanitari.", 
                               className="card-text mb-4"),
                        
                        # Pulsante Registra Glicemia
                        dbc.Button(
                            [
                                html.Img(src="/assets/glicemia.png", 
                                       style={"width": "40px", "height": "40px", "margin-right": "10px"}),
                                "Registra Glicemia"
                            ],
                            id="btn-registra-glicemia",
                            className="btn-primary w-100 mb-3",
                            size="lg"
                        ),
                        
                        # Area per messaggi/feedback
                        html.Div(id="patient-feedback", className="mt-3")
                    ])
                ]),
                
                # QUESTO È IL DIV MANCANTE - Area dove appare il form
                html.Div(id="patient-content", className="mt-3")
                
            ], width=8)
        ], justify="center", className="mt-4")
    ], fluid=True, className="main-container")

def get_glicemia_form():
    """Form per registrare nuova misurazione glicemia"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Registrazione Glicemia", className="mb-0 text-primary")
        ]),
        dbc.CardBody([
            # Valore glicemia
            dbc.Row([
                dbc.Col([
                    dbc.Label("Valore glicemia (mg/dL) *", className="form-label"),
                    dbc.Input(
                        id="input-valore-glicemia",
                        type="number",
                        min=0,
                        max=600,
                        step=1,
                        placeholder="es. 120",
                        className="form-control"
                    )
                ], width=12, md=6),
                
                # Data misurazione
                dbc.Col([
                    dbc.Label("Data misurazione *", className="form-label"),
                    dcc.DatePickerSingle(
                        id="input-data-glicemia",
                        date=date.today(),
                        display_format='DD/MM/YYYY',
                        style={"width": "100%"}
                    )
                ], width=12, md=6)
            ], className="mb-3"),
            
            # Ora e momento pasto
            dbc.Row([
                dbc.Col([
                    dbc.Label("Ora misurazione *", className="form-label"),
                    dbc.Input(
                        id="input-ora-glicemia",
                        type="time",
                        value=datetime.now().strftime("%H:%M"),
                        className="form-control"
                    )
                ], width=12, md=6),
                
                dbc.Col([
                    dbc.Label("Momento rispetto ai pasti *", className="form-label"),
                    dbc.Select(
                        id="select-momento-pasto",
                        options=[
                            {"label": "A digiuno", "value": "digiuno"},
                            {"label": "Prima del pasto", "value": "prima_pasto"},
                            {"label": "Dopo il pasto", "value": "dopo_pasto"}
                        ],
                        placeholder="Seleziona...",
                        className="form-control"
                    )
                ], width=12, md=6)
            ], className="mb-3"),
            
            # NUOVO CAMPO - Container per domanda due ore (nascosto di default)
            html.Div(
                id="due-ore-pasto-container",
                children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Sono passate almeno due ore dopo l'ultimo pasto? *", 
                                    className="form-label text-info"),
                            dbc.RadioItems(
                                id="radio-due-ore-pasto",
                                options=[
                                    {"label": "Sì", "value": True},
                                    {"label": "No", "value": False}
                                ],
                                inline=True,
                                className="mt-2",
                                input_style={
                                    "margin-right": "8px",
                                    "transform": "scale(1.3)",
                                    "accent-color": "#0d6efd",
                                    "border": "2px solid #000000"
                                },
                                labelStyle={"margin-right": "25px", "font-weight": "500"}
                            )
                        ], width=12)
                    ], className="mb-3")
                ],
                style={"display": "none"}  # Nascosto di default
            ),
            
            # Note
            dbc.Row([
                dbc.Col([
                    dbc.Label("Note (opzionale)", className="form-label"),
                    dbc.Textarea(
                        id="textarea-note-glicemia",
                        placeholder="Eventuali note o osservazioni...",
                        rows=3,
                        className="form-control"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Pulsanti
            html.Div([
                dbc.Button(
                    "Salva Misurazione",
                    id="btn-salva-glicemia",
                    color="success",
                    size="lg",
                    className="me-2"
                ),
                dbc.Button(
                    "Annulla",
                    id="btn-annulla-glicemia",
                    color="secondary",
                    size="lg"
                )
            ], className="d-grid gap-2 d-md-flex justify-content-md-end")
        ])
    ], className="mt-3")

def get_success_message(valore, data_ora, momento_pasto, due_ore_pasto=None):
    """Messaggio di successo dopo salvataggio"""
    # Costruisci il messaggio base
    children = [
        html.H5("Misurazione salvata con successo!", className="alert-heading"),
        html.P(f"Glicemia: {valore} mg/dL"),
        html.P(f"Data e ora: {data_ora.strftime('%d/%m/%Y alle %H:%M')}"),
        html.P(f"Momento: {get_momento_display(momento_pasto)}")
    ]
    
    # Aggiungi info sulle due ore se presente
    if momento_pasto == "dopo_pasto" and due_ore_pasto is not None:
        due_ore_text = "Sì" if due_ore_pasto else "No"
        children.append(html.P(f"Due ore dopo il pasto: {due_ore_text}"))
    
    children.extend([
        html.Hr(),
        dbc.Button("Registra nuova misurazione", 
                 id="btn-nuova-misurazione", 
                 color="primary", 
                 size="sm")
    ])
    
    return dbc.Alert(children, color="success", dismissable=True)

def get_error_message(message):
    """Messaggio di errore"""
    return dbc.Alert(message, color="danger", dismissable=True)

def get_momento_display(momento_pasto):
    """Converte il codice momento in testo leggibile"""
    mapping = {
        "digiuno": "A digiuno",
        "prima_pasto": "Prima del pasto",
        "dopo_pasto": "Dopo il pasto"
    }
    return mapping.get(momento_pasto, momento_pasto)