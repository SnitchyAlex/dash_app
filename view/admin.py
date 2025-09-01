# view/admin.py
import dash_bootstrap_components as dbc
from datetime import datetime
from dash import html, dcc
from pony.orm import db_session

from model.medico import Medico
from model.paziente import Paziente

def get_admin_dashboard():
    """Restituisce il layout della dashboard admin"""
    return html.Div([
        # Immagine home posizionata in alto a sinistra
        html.A([
            html.Img(
                src="/assets/home.png",
                style={
                    "position": "fixed",
                    "top": "20px",
                    "left": "20px",
                    "width": "50px",
                    "height": "50px",
                    "cursor": "pointer",
                    "z-index": "1000",
                    "border-radius": "8px",
                    "box-shadow": "0 2px 8px rgba(0,0,0,0.2)",
                    "transition": "transform 0.2s ease"
                },
                title="Torna alla home"
            )
        ], 
        href="/",
        style={"text-decoration": "none"}),
    
        dbc.Container([
            # Header della dashboard
            html.Div([
                html.H1([
                    html.Img(src="/assets/admin.png", style={"width": "50px", "height": "50px", "marginRight": "8px"}),
                    "Dashboard Amministratore"
                ], className="gradient-title text-center mb-4"),
                html.Hr(className="mb-4")
            ]),
            
            # Cards principali delle funzionalità 
            dbc.Row([
                # Card per creare utente
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4([
                                html.Img(src="/assets/add.png", style={"width": "35px", "height": "35px", "marginRight": "8px"}),
                                "Crea Nuovo Utente"
                            ], className="card-title text-success"),
                            html.P("Aggiungi nuovi utenti al sistema", className="card-text"),
                            dbc.Button("Crea Nuovo Utente", id="create-user-button", 
                                     color="success", className="welcome-btn", size="sm")
                        ])
                    ], className="mb-4 card")
                ], md=6),
                
                # Card per eliminare utente
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4([
                                html.Img(src="/assets/bin.png", style={"width": "35px", "height": "35px", "marginRight": "8px"}),
                                "Elimina Utente"
                            ], className="card-title text-danger"),
                            html.P("Rimuovi utenti dal sistema", className="card-text"),
                            dbc.Button("Elimina Utente", id="delete-user-button", 
                                     color="red", size="sm")
                        ])
                    ], className="mb-4 card")
                ], md=6)
            ]),
            
            dbc.Row([
                # Card per visualizzare medici
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4([
                                html.Img(src="/assets/doctor.png", style={"width": "35px", "height": "35px", "marginRight": "8px"}),
                                "Visualizza Medici"
                            ], className="card-title text-primary"),
                            html.P("Mostra tutti i medici registrati", className="card-text"),
                            dbc.Button("Visualizza Medici", id="view-doctors-button", 
                                     color="primary", size="sm")
                        ])
                    ], className="mb-4 card")
                ], md=6),
                
                # Card per visualizzare pazienti
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4([
                                html.Img(src="/assets/patient.png", style={"width": "35px", "height": "35px", "marginRight": "8px"}),
                                "Visualizza Pazienti"
                            ], className="card-title text-info"),
                            html.P("Mostra tutti i pazienti registrati", className="card-text"),
                            dbc.Button("Visualizza Pazienti", id="view-patients-button", 
                                     color="primary", size="sm")
                        ])
                    ], className="mb-4 card")
                ], md=6)
            ]),
            
            # Sezione per visualizzare contenuti dinamici
            html.Div([
                # Area per mostrare liste di medici/pazienti o form di creazione/eliminazione
                html.Div(id="content-area", children=[
                    # Messaggio di benvenuto iniziale
                    dbc.Alert([
                        html.H4([
                            html.Img(src="/assets/wave.gif", style={"width": "50px", "height": "50px", "marginRight": "8px"}),
                            "Benvenuto/a nella Dashboard Admin!"
                        ], className="alert-heading"),
                        html.P("Seleziona una delle opzioni sopra per iniziare a gestire il sistema."),
                        html.Hr(),
                        html.P("🔹 Crea nuovi utenti per medici o pazienti"),
                        html.P("🔹 Visualizza liste complete di medici e pazienti"),
                        html.P("🔹 Elimina utenti quando necessario")
                    ], color="light", className="mb-4")
                ])
            ])
            
        ], fluid=True, className="main-container")
    ])


def get_create_user_form():
    """Restituisce il form per creare un nuovo utente"""
    return dbc.Card([
        dbc.CardHeader(html.H4("➕ Crea Nuovo Utente")),
        dbc.CardBody([
            # Output per messaggi
            html.Div(id="create-user-output"),
            
            # Form fields - Informazioni base
            dbc.Row([
                dbc.Col([
                    dbc.Label("Username *", className="form-label"),
                    dbc.Input(id="new-username", type="text", placeholder="Inserisci username")
                ], md=6),
                dbc.Col([
                    dbc.Label("Password *", className="form-label"),
                    dbc.Input(id="new-password", type="password", placeholder="Inserisci password")
                ], md=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Nome *", className="form-label"),
                    dbc.Input(id="new-name", type="text", placeholder="Inserisci nome")
                ], md=6),
                dbc.Col([
                    dbc.Label("Cognome *", className="form-label"),
                    dbc.Input(id="new-surname", type="text", placeholder="Inserisci cognome")
                ], md=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Telefono", className="form-label"),
                    dbc.Input(id="new-telefono", type="text", placeholder="Inserisci telefono")
                ], md=6),
                dbc.Col([
                    dbc.Label("Ruolo *", className="form-label"),
                    dbc.Select(
                        id="new-role",
                        options=[
                            {"label": "Seleziona ruolo...", "value": ""},
                            {"label": "👨🏻‍⚕️ Medico", "value": "medico"},
                            {"label": "👤 Paziente", "value": "paziente"},
                            {"label": "👑 Nuovo admin", "value": "user"}
                        ],
                        value=""
                    )
                ], md=6)
            ], className="mb-3"),
            
            # Campi specifici per medico (nascosti inizialmente)
            html.Div(id="medico-fields", style={'display': 'none'}, children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Specializzazione", className="form-label"),
                        dbc.Input(id="new-specializzazione", type="text", 
                                 placeholder="Es: Cardiologia, Neurologia... (opzionale)")
                    ], md=12)
                ], className="mb-3")
            ]),
            
            # Campi specifici per paziente (nascosti inizialmente)
            html.Div(id="paziente-fields", style={'display': 'none'}, children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Data di nascita", className="form-label"),
                        dbc.Input(
                            id="new-birth-date", 
                            type="date", 
                            placeholder="Seleziona la tua data di nascita (opzionale)",
                            max=datetime.now().strftime('%Y-%m-%d'),  # Non permette date future
                            style={"cursor": "pointer"}
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("Età", className="form-label"),
                        dbc.Select(
                            id="new-eta",
                            options=[{"label": "Seleziona età...", "value": ""}] + 
                                   [{"label": f"{i} anni", "value": str(i)} for i in range(0, 151)],
                            value="",
                            placeholder="Seleziona età (opzionale)"
                        )
                    ], md=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Codice Fiscale", className="form-label"),
                        dbc.Input(id="new-codice-fiscale", type="text", 
                                 placeholder="Inserisci codice fiscale (opzionale)")
                    ], md=6),
                    dbc.Col([
                        dbc.Label("Medico di Riferimento", className="form-label"),
                        dbc.Select(
                            id="new-medico-riferimento",
                            placeholder="Seleziona medico di riferimento (opzionale)...",
                            options=[],  # Verrà popolato dal callback
                            value=""
                        )
                    ], md=6)
                ], className="mb-3")
            ]),
            
            # Bottoni
            html.Div([
                dbc.Button("Crea Utente", id="submit-new-user", 
                         color="success", disabled=True)
            ], className="text-end")
        ])
    ], className="card mb-4")


def get_delete_user_form():
    """Restituisce il form per eliminare un utente"""
    return dbc.Card([
        dbc.CardHeader(html.H4("🗑️ Elimina Utente")),
        dbc.CardBody([
            # Output per messaggi
            html.Div(id="delete-user-output"),
            
            # Alert di avvertimento
            dbc.Alert([
                html.H6("⚠️ Attenzione!", className="alert-heading"),
                html.P([
                    "Questa operazione è ", html.Strong("irreversibile"), "."
                ]),
                html.P("L'eliminazione di un utente comporterà anche:"),
                html.Ul([
                    html.Li("Rimozione di tutte le relazioni medico-paziente"),
                    html.Li("Cancellazione di tutti i dati associati"),
                    html.Li("Perdita definitiva delle informazioni")
                ]),
                html.P("Seleziona con attenzione l'utente da eliminare.")
            ], color="warning", className="mb-4"),
            
            # Selezione utente
            dbc.Row([
                dbc.Col([
                    dbc.Label("Seleziona utente da eliminare:", className="form-label fw-bold"),
                    dbc.Select(
                        id="user-to-delete",
                        placeholder="Seleziona un utente...",
                        options=[],  # Verrà popolato dal callback
                        value=""
                    )
                ], md=12)
            ], className="mb-3"),

            # Bottoni
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-trash-alt me-2"),
                    "Elimina Utente"
                ], id="submit-delete-user", 
                color="danger", 

                className="me-2"),
                
                dbc.Button([
                    html.I(className="fas fa-sync-alt me-2"),
                    "Aggiorna Lista"
                ], id="refresh-users-list", 
                color="secondary", 
                outline=True)
            ], className="text-end mt-4")
        ])
    ], className="card mb-4")


@db_session
def get_doctors_list():
    """Restituisce la lista di tutti i medici"""
    medici = Medico.select()
    
    if not medici:
        return dbc.Alert("Nessun medico trovato nel sistema.", color="info")
    
    doctors_cards = []
    for medico in medici:
        # Conta i pazienti assegnati
        num_patients = len(medico.patients)
        # Conta i pazienti di cui è medico di riferimento
        num_riferimento = len(medico.pazienti_riferimento)
        
        card = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H5([
                        html.Img(src="/assets/doctor.png", style={"width": "30px", "height": "30px", "marginRight": "8px"}),
                        f"Dr. {medico.name} {medico.surname}"
                    ], className="card-title text-primary"),
                    html.P([
                        html.Strong("Username: "), medico.username
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Specializzazione: "), 
                        medico.specializzazione or "Non specificata"
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Telefono: "), 
                        medico.telefono or "Non disponibile"
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Pazienti assegnati: "), 
                        html.Span(str(num_patients), className="badge bg-primary")
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Pazienti di riferimento: "), 
                        html.Span(str(num_riferimento), className="badge bg-success")
                    ], className="card-text")
                ])
            ])
        ], color="primary", outline=True, className="mb-3")
        
        doctors_cards.append(card)
    
    return html.Div([
        html.H3(f"Medici Registrati ({len(doctors_cards)})", className="mb-4"),
        html.Div(doctors_cards)
    ])


@db_session
def get_patients_list():
    """Restituisce la lista di tutti i pazienti"""
    pazienti = Paziente.select()
    
    if not pazienti:
        return dbc.Alert("Nessun paziente trovato nel sistema.", color="info")
    
    patients_cards = []
    for paziente in pazienti:
        # Conta i medici assegnati
        num_doctors = len(paziente.doctors)
        
        card = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H5([
                        html.Img(src="/assets/patient.png", style={"width": "30px", "height": "30px", "marginRight": "5px"}),
                        f"{paziente.name} {paziente.surname}"
                    ], className="card-title text-info"),
                    html.P([
                        html.Strong("Username: "), paziente.username
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Data di nascita: "), 
                        str(paziente.birth_date.strftime('%d/%m/%Y')) if paziente.birth_date else "Non specificata"
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Età: "), 
                        str(paziente.eta) if paziente.eta else "Non specificata"
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Codice Fiscale: "), 
                        paziente.codice_fiscale or "Non disponibile"
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Telefono: "), 
                        paziente.telefono or "Non disponibile"  
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Medici assegnati: "), 
                        html.Span(str(num_doctors), className="badge bg-info")
                    ], className="card-text mb-1"),
                    html.P([
                        html.Strong("Medico di riferimento: "), 
                        f"Dr. {paziente.medico_riferimento.name} {paziente.medico_riferimento.surname}" if paziente.medico_riferimento else "Non assegnato",
                        " " if paziente.medico_riferimento else ""
                    ], className="card-text")
                ])
            ])
        ], color="info", outline=True, className="mb-3")
        
        patients_cards.append(card)
    
    return html.Div([
        html.H3(f"Pazienti Registrati ({len(patients_cards)})", className="mb-4"),
        html.Div(patients_cards)
    ])