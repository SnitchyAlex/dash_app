# controller/admin.py
from datetime import datetime
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

from view.admin import (
    get_create_user_form, 
    get_delete_user_form,
    get_patients_list,
    get_doctors_list
)

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
    
    @app.callback(
        [Output('new-eta', 'value'),
         Output('new-eta', 'disabled'),
         Output('new-eta', 'placeholder')],
        [Input('new-birth-date', 'value')],
        prevent_initial_call=False
    )
    def calculate_age_from_birth_date(birth_date):
        if birth_date:
            try:
                # Calcola l'età dalla data di nascita
                birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - birth_date_obj.year
                
                # Verifica se il compleanno è già passato quest'anno
                if today.month < birth_date_obj.month or (today.month == birth_date_obj.month and today.day < birth_date_obj.day):
                    age -= 1
                
                return age, True, f"Calcolata automaticamente: {age} anni"
            except:
                return None, False, "Inserisci età (opzionale)"
        else:
            # Se non c'è data di nascita, permetti inserimento manuale dell'età
            return None, False, "Inserisci età (opzionale)"
    
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
         Output('new-birth-date', 'value'),
         Output('new-codice-fiscale', 'value')],
        [Input('submit-new-user', 'n_clicks')],
        [State('new-username', 'value'),
         State('new-password', 'value'),
         State('new-name', 'value'),
         State('new-surname', 'value'),
         State('new-telefono', 'value'),
         State('new-role', 'value'),
         State('new-specializzazione', 'value'),
         State('new-birth-date', 'value'),
         State('new-eta', 'value'),
         State('new-codice-fiscale', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def create_new_user(submit_clicks, username, password, name, surname, 
                       telefono, role, specializzazione, birth_date, eta, codice_fiscale):
        
        if not submit_clicks:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # Validazione campi obbligatori
        if not all([username, password, name, surname, role]):
            return dbc.Alert('Tutti i campi obbligatori devono essere compilati!', 
                           color='danger'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        if role == 'paziente':
            # Validazione età se inserita manualmente (senza data di nascita)
            if eta is not None and not birth_date:
                try:
                    eta_int = int(eta)
                    if eta_int < 0 or eta_int > 125:
                        return dbc.Alert('L\'età deve essere compresa tra 0 e 125 anni!', 
                                       color='danger'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
                except (ValueError, TypeError):
                    return dbc.Alert('L\'età deve essere un numero valido!', 
                                   color='danger'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
            # Validazione data di nascita
            if birth_date:
                try:
                    birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
                    if birth_date_obj.year < 1900:
                        return dbc.Alert('La data di nascita non può essere precedente al 1900!', 
                                       color='danger'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
                    if birth_date_obj > datetime.now():
                        return dbc.Alert('La data di nascita non può essere nel futuro!', 
                                       color='danger'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
                except:
                    return dbc.Alert('Formato data non valido!', 
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
                    telefono=telefono if telefono else '',
                    is_admin=False,
                    specializzazione=specializzazione or None
                )
                
            elif role == 'paziente':
                paziente = Paziente(
                    username=username,
                    password_hash=generate_password_hash(password),
                    name=name,
                    surname=surname,
                    telefono=telefono if telefono else '',
                    is_admin=False,
                    birth_date=datetime.strptime(birth_date, '%Y-%m-%d') if birth_date else None,
                    eta=int(eta) if eta else None,
                    codice_fiscale=codice_fiscale or None
                )
                
            else:  # utente base
                user = User(
                    username=username,
                    password_hash=generate_password_hash(password),
                    name=name,
                    surname=surname,
                    telefono= telefono if telefono else '',
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
    
    # Callback per gestire l'eliminazione dell'utente
    @app.callback(
        [Output('delete-user-output', 'children'),
        Output('user-to-delete', 'value')],
        [Input('submit-delete-user', 'n_clicks')],
        [State('user-to-delete', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def delete_selected_user(submit_clicks, selected_username):
        if not submit_clicks or not selected_username:
            return dash.no_update, dash.no_update
    
        try:
        # Importa le funzioni dal model
            from model.operations import get_user_by_username, delete_user_with_relations
        
        # Ottieni l'utente da eliminare
            user_to_delete = get_user_by_username(selected_username)
            if not user_to_delete:
                return dbc.Alert('Utente non trovato!', color='danger'), dash.no_update
        
        # Non permettere di eliminare admin
            if user_to_delete.is_admin:
                return dbc.Alert('Non è possibile eliminare un utente amministratore!', color='danger'), dash.no_update

        # if hasattr(current_user, 'username') and current_user.username == selected_username:
        # return dbc.Alert('Non puoi eliminare il tuo stesso account!', color='danger'), dash.no_update
        
        # Elimina l'utente con le sue relazioni
            success, message = delete_user_with_relations(selected_username)
        
            if success:
                return dbc.Alert(message, color='success'), ''
            else:
             return dbc.Alert(f'Errore durante l\'eliminazione: {message}', color='danger'), dash.no_update
        
        except Exception as e:
            print(f"Errore durante l'eliminazione dell'utente: {e}")
            return dbc.Alert(f'Errore durante l\'eliminazione: {str(e)}', color='danger'), dash.no_update

# Callback per popolare la dropdown degli utenti
    @app.callback(
        Output('user-to-delete', 'options'),
        [Input('delete-user-button', 'n_clicks'),
         Input('refresh-users-list', 'n_clicks')],
        prevent_initial_call=False
    )
    @db_session 
    def update_users_dropdown(delete_clicks, refresh_clicks):
        """Aggiorna la dropdown con tutti gli utenti disponibili"""
        from model.operations import get_all_users_for_dropdown
    
        try:
            users_options = get_all_users_for_dropdown()
            return users_options
        except Exception as e:
            print(f"Errore nel caricamento utenti: {e}")
            return []

    