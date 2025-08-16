# controller/patient.py
"""Controller per la gestione dei pazienti"""
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import html
from datetime import datetime
from pony.orm import db_session, commit
from model.glicemia import Glicemia
from model.paziente import Paziente
from view.patient import get_glicemia_form, get_success_message, get_error_message

def register_patient_callbacks(app):
    """Registra tutti i callback per i pazienti"""
    
    @app.callback(
        Output('patient-content', 'children'),
        Input('btn-registra-glicemia', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_glicemia_form(n_clicks):
        """Mostra il form per registrare la glicemia"""
        if n_clicks:
            return get_glicemia_form()
        return dash.no_update
    
    # NUOVO CALLBACK - Mostra/nasconde il campo due ore
    @app.callback(
        Output('due-ore-pasto-container', 'style'),
        Input('select-momento-pasto', 'value')
    )
    def toggle_due_ore_pasto(momento_pasto):
        """Mostra/nasconde il campo due ore in base al momento del pasto"""
        if momento_pasto == 'dopo_pasto':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-salva-glicemia', 'n_clicks'),
        [State('input-valore-glicemia', 'value'),
         State('input-data-glicemia', 'value'),  # Cambiato da 'date' a 'value'
         State('input-ora-glicemia', 'value'),
         State('select-momento-pasto', 'value'),
         State('textarea-note-glicemia', 'value'),
         State('radio-due-ore-pasto', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_glicemia_measurement(n_clicks, valore, data_misurazione, ora, momento_pasto, note, due_ore_pasto):
        """Salva la misurazione della glicemia nel database"""
        if not n_clicks:
            return dash.no_update
        
        # Validazione campi obbligatori
        if not valore or not data_misurazione or not ora or not momento_pasto:
            return get_error_message("Per favore compila tutti i campi obbligatori e inserisci un valore glicemico valido!")
        
        # NUOVA VALIDAZIONE - Controllo date valide
        try:
            data_inserita = datetime.strptime(data_misurazione, '%Y-%m-%d').date()
            data_oggi = datetime.now().date()
            data_minima = datetime(1900, 1, 1).date()
            
            if data_inserita > data_oggi:
                return get_error_message("La data di misurazione non può essere nel futuro!")
            
            if data_inserita < data_minima:
                return get_error_message("La data di misurazione non può essere precedente al 1900!")
                
        except ValueError:
            return get_error_message("Formato data non valido!")
        
        # VALIDAZIONE - Controllo campo due ore per "dopo_pasto"
        if momento_pasto == 'dopo_pasto' and due_ore_pasto is None:
            return get_error_message("Per favore specifica se sono passate almeno due ore dal pasto!")
        
        try:
            # Trova il paziente corrente
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            # Combina data e ora
            data_ora = datetime.combine(
                data_inserita,
                datetime.strptime(ora, '%H:%M').time()
            )
            
            # Determina il valore per due_ore_pasto
            campo_due_ore = due_ore_pasto if momento_pasto == 'dopo_pasto' else None
            
            # Crea e salva la misurazione
            misurazione = Glicemia(
                paziente=paziente,
                valore=float(valore),
                data_ora=data_ora,
                momento_pasto=momento_pasto,
                note=note if note else '',
                due_ore_pasto=campo_due_ore
            )
            commit()
            
            return get_success_message(valore, data_ora, momento_pasto, due_ore_pasto)
            
        except ValueError as e:
            return get_error_message(f"Errore nei dati inseriti: {str(e)}")
        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-nuova-misurazione', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_new_form(n_clicks):
        """Mostra un nuovo form dopo aver salvato"""
        if n_clicks:
            return get_glicemia_form()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-annulla-glicemia', 'n_clicks'),
        prevent_initial_call=True
    )
    def cancel_form(n_clicks):
        """Nasconde il form quando si clicca annulla"""
        if n_clicks:
            return html.Div()
        return dash.no_update