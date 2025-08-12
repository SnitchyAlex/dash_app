# view/admin.py
import dash_bootstrap_components as dbc
from dash import html, dcc

def get_admin_dashboard():
    """Restituisce il layout della dashboard admin"""
    
    return dbc.Container([
        # Header della dashboard
        html.Div([
            html.H1([
                html.Img(src="/assets/admin.png", style={"width": "50px", "height": "50px", "marginRight": "8px"}),
            "Dashboard Amministratore"], className="gradient-title text-center mb-4"),
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
                            "Crea Nuovo Utente"], className="card-title text-success"),
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
                        "Elimina Utente"], className="card-title text-danger"),
                        html.P("Rimuovi utenti dal sistema", className="card-text"),
                        dbc.Button("Elimina Utente", id="delete-user-button", 
                                 color="red", size="sm", disabled=False)
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
                            "Visualizza Medici"], className="card-title text-primary"),
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
                            "Visualizza Pazienti"], className="card-title text-info"),
                        html.P("Mostra tutti i pazienti registrati", className="card-text"),
                        dbc.Button("Visualizza Pazienti", id="view-patients-button", 
                                 color="primary", size="sm")
                    ])
                ], className="mb-4 card")
            ], md=6)
        ]),
        
        # Form per creare utente (inizialmente nascosto)
        html.Div(id="create-user-form", style={'display': 'none'}, children=[
            dbc.Card([
                dbc.CardHeader(html.H4("➕ Crea Nuovo Utente")),
                dbc.CardBody([
                    # Output per messaggi
                    html.Div(id="create-user-output"),
                    
                    # Form fields
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
                                    {"label": "👨‍⚕️ Medico", "value": "medico"},
                                    {"label": "👤 Paziente", "value": "paziente"},
                                    {"label": "👥 Utente", "value": "user"}
                                ],
                                value=""
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    # Campi specifici per medico
                    html.Div(id="medico-fields", style={'display': 'none'}, children=[
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Specializzazione", className="form-label"),
                                dbc.Input(id="new-specializzazione", type="text", 
                                         placeholder="Es: Cardiologia, Neurologia... (opzionale)")
                            ], md=12)
                        ], className="mb-3")
                    ]),
                    
                    # Campi specifici per paziente
                    html.Div(id="paziente-fields", style={'display': 'none'}, children=[
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Età", className="form-label"),
                                dbc.Input(id="new-eta", type="number", placeholder="Inserisci età (opzionale)")
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Codice Fiscale", className="form-label"),
                                dbc.Input(id="new-codice-fiscale", type="text", 
                                         placeholder="Inserisci codice fiscale (opzionale)")
                            ], md=6)
                        ], className="mb-3")
                    ]),
                    
                    # Bottoni
                    html.Div([
                        dbc.Button("Annulla", id="cancel-create-user", 
                                 color="secondary", className="me-2"),
                        dbc.Button("Crea Utente", id="submit-new-user", 
                                 color="success", disabled=True)
                    ], className="text-end")
                ])
            ], className="card mb-4")
        ]),
        
        # Sezione per visualizzare contenuti dinamici
        html.Div([
            # Area per mostrare liste di medici/pazienti o form di eliminazione
            html.Div(id="content-area", children=[
                # Inizialmente mostra un messaggio di benvenuto
                dbc.Alert([
                    html.H4([
                        html.Img(src="/assets/wave.gif", style={"width": "50px", "height": "50px", "marginRight": "8px"}),
                    "Benvenuto nella Dashboard Admin!"], className="alert-heading"),
                    html.P("Seleziona una delle opzioni sopra per iniziare a gestire il sistema."),
                    html.Hr(),
                    html.P("🔹 Crea nuovi utenti per medici o pazienti"),
                    html.P("🔹 Visualizza liste complete di medici e pazienti"),
                    html.P("🔹 Elimina utenti quando necessario")
                ], color="light", className="mb-4")
            ])
        ])
        
    ], fluid=True, className="main-container")


def get_admin_sidebar():
    """Restituisce la sidebar per l'admin (opzionale)"""
    
    return dbc.Card([
        dbc.CardHeader("🔧 Strumenti Admin"),
        dbc.CardBody([
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/admin", active=True)),
                dbc.NavItem(dbc.NavLink("Gestione Utenti", href="/admin/users")),
                dbc.NavItem(dbc.NavLink("Statistiche", href="/admin/stats", disabled=True)),
                dbc.NavItem(dbc.NavLink("Impostazioni", href="/admin/settings", disabled=True))
            ], vertical=True)
        ])
    ], className="card")