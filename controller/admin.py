# controller/admin.py
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user
from pony.orm import db_session
from dash import html, dcc
from model.operations import add_user, get_user_by_username
from model.user import User
from model.medico import Medico
from model.paziente import Paziente
from pony.orm import commit

def register_admin_callbacks(app):
    """Register admin-related callbacks"""
    
    # Callback principale per gestire le diverse azioni admin
    @app.callback(
        Output('content-area', 'children'),
        [Input('create-user-button', 'n_clicks'),
         Input('view-doctors-button', 'n_clicks'),
         Input('view-patients-button', 'n_clicks'),
         Input('delete-user-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def handle_admin_actions(create_clicks, doctors_clicks, patients_clicks, delete_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'create-user-button':
            return get_create_user_form()
        elif trigger_id == 'view-doctors-button':
            return get_doctors_list()
        elif trigger_id == 'view-patients-button':
            return get_patients_list()
        elif trigger_id == 'delete-user-button':
            return get_delete_user_form()
        
        return dash.no_update
    
    # Callback per gestire la creazione di un nuovo utente
    @app.callback(
        [Output('create-user-output', 'children'),
         Output('new-username', 'value'),
         Output('new-password', 'value'),
         Output('new-name', 'value'),
         Output('new-surname', 'value'),
         Output('new-telefono', 'value'),
         Output('new-role', 'value'),
         Output('new-specializzazione', 'value'),
         Output('new-eta', 'value'),
         Output('new-codice-fiscale', 'value')],
        [Input('submit-new-user', 'n_clicks')],
        [State('new-username', 'value'),
         State('new-password', 'value'),
         State('new-name', 'value'),
         State('new-surname', 'value'),
         State('new-telefono', 'value'),
         State('new-role', 'value'),
         State('new-specializzazione', 'value'),
         State('new-eta', 'value'),
         State('new-codice-fiscale', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def create_new_user(submit_clicks, username, password, name, surname, 
                       telefono, role, specializzazione, eta, codice_fiscale):
        
        if not submit_clicks:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # Validazione campi obbligatori
        if not all([username, password, name, surname, role]):
            return dbc.Alert('Tutti i campi obbligatori devono essere compilati!', 
                           color='danger'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Controlla se l'utente esiste già
            if get_user_by_username(username):
                return dbc.Alert(f'Username "{username}" già esistente!', 
                               color='danger'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
            # Crea l'utente in base al ruolo
            from werkzeug.security import generate_password_hash
            
            if role == 'medico':
                medico = Medico(
                    username=username,
                    password_hash=generate_password_hash(password),
                    name=name,
                    surname=surname,
                    telefono=telefono or None,
                    is_admin=False,
                    specializzazione=specializzazione or None
                )
                
            elif role == 'paziente':
                paziente = Paziente(
                    username=username,
                    password_hash=generate_password_hash(password),
                    name=name,
                    surname=surname,
                    telefono=telefono or None,
                    is_admin=False,
                    eta=int(eta) if eta else None,
                    codice_fiscale=codice_fiscale or None
                )
                
            else:  # utente base
                user = User(
                    username=username,
                    password_hash=generate_password_hash(password),
                    name=name,
                    surname=surname,
                    telefono=telefono or None,
                    is_admin=False
                )
            commit()
            # Se tutto va bene, pulisci il form e mostra messaggio di successo
            return (dbc.Alert(f'Utente "{username}" creato con successo!', color='success'),
                   '', '', '', '', '', '', '', '', '')
            
        except Exception as e:
            print(f"Errore durante la creazione dell'utente: {e}")
            return (dbc.Alert(f'Errore durante la creazione: {str(e)}', color='danger'),
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)
    
    # Callback per mostrare/nascondere i campi specifici in base al ruolo
    @app.callback(
        [Output('medico-fields', 'style'),
         Output('paziente-fields', 'style')],
        [Input('new-role', 'value')],
        prevent_initial_call=False
    )
    def toggle_role_fields(role):
        medico_style = {'display': 'block'} if role == 'medico' else {'display': 'none'}
        paziente_style = {'display': 'block'} if role == 'paziente' else {'display': 'none'}
        return medico_style, paziente_style
    
    # Callback per abilitare/disabilitare il bottone submit
    @app.callback(
        Output('submit-new-user', 'disabled'),
        [Input('new-username', 'value'),
         Input('new-password', 'value'),
         Input('new-name', 'value'),
         Input('new-surname', 'value'),
         Input('new-role', 'value')],
        prevent_initial_call=False
    )
    def toggle_submit_button(username, password, name, surname, role):
        if not all([username, password, name, surname, role]):
            return True
        return False


# Funzioni helper per generare i diversi contenuti
def get_create_user_form():
    """Restituisce il form per creare un nuovo utente"""
    return dbc.Card([
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
                dbc.Button("Crea Utente", id="submit-new-user", 
                         color="success", disabled=True)
            ], className="text-end")
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
        
        card = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H5([
                        html.Img(src="/assets/doctor.png", style={"width": "30px", "height": "30px", "marginRight": "8px"}),
                        f"Dr. {medico.name} {medico.surname}"], className="card-title text-primary"),
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
                    ], className="card-text")
                ])
            ])
        ], color="primary", outline=True, className="mb-3")
        
        doctors_cards.append(card)
    
    return html.Div([
        html.H3(
            f"Medici Registrati ({len(doctors_cards)})", className="mb-4"),
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
                        f"{paziente.name} {paziente.surname}"], className="card-title text-info"),
                    html.P([
                        html.Strong("Username: "), paziente.username
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
                    ], className="card-text")
                ])
            ])
        ], color="info", outline=True, className="mb-3")
        
        patients_cards.append(card)
    
    return html.Div([
        html.H3(
            f"Pazienti Registrati ({len(patients_cards)})", className="mb-4"),
        html.Div(patients_cards)
    ])


def get_delete_user_form():
    """Restituisce il form per eliminare un utente"""
    return dbc.Card([
        dbc.CardHeader(html.H4("🗑️ Elimina Utente")),
        dbc.CardBody([
            dbc.Alert([
                html.H6("⚠️ Attenzione!", className="alert-heading"),
                html.P("Questa operazione è irreversibile. Seleziona con attenzione l'utente da eliminare.")
            ], color="warning"),
            
            html.P("Funzionalità in sviluppo... 🚧", className="text-muted")
        ])
    ], className="card mb-4")