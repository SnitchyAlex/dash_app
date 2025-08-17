# controller/patient.py
"""Controller per la gestione dei pazienti"""
import dash
from dash.dependencies import Input, Output, State
from flask_login import current_user
from dash import html
from datetime import datetime
from pony.orm import db_session, commit
from model.glicemia import Glicemia
from model.assunzione import Assunzione
from model.paziente import Paziente
from model.sintomi import Sintomi
from view.patient import (
    get_glicemia_form, 
    get_success_message, 
    get_error_message,
    get_nuova_assunzione_form, 
    get_assunzione_success_message,
    get_miei_dati_view, 
    get_andamento_glicemico_view,
    get_sintomi_trattamenti_form,
    get_sintomi_success_message
)


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
         State('input-data-glicemia', 'value'),
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
        
        if not valore or not data_misurazione or not ora or not momento_pasto:
            return get_error_message("Per favore compila tutti i campi obbligatori e inserisci un valore glicemico valido!")
        
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
        
        if momento_pasto == 'dopo_pasto' and due_ore_pasto is None:
            return get_error_message("Per favore specifica se sono passate almeno due ore dal pasto!")
        
        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            data_ora = datetime.combine(
                data_inserita,
                datetime.strptime(ora, '%H:%M').time()
            )
            
            campo_due_ore = due_ore_pasto if momento_pasto == 'dopo_pasto' else None
            
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
    def show_new_glicemia_form(n_clicks):
        """Mostra un nuovo form glicemia dopo aver salvato"""
        if n_clicks:
            return get_glicemia_form()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-annulla-glicemia', 'n_clicks'),
        prevent_initial_call=True
    )
    def cancel_glicemia_form(n_clicks):
        """Nasconde il form glicemia quando si clicca annulla"""
        if n_clicks:
            return html.Div()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-nuova-assunzione', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_assunzione_form(n_clicks):
        """Mostra il form per registrare una nuova assunzione"""
        if n_clicks:
            return get_nuova_assunzione_form()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-salva-assunzione', 'n_clicks'),
        [State('input-nome-farmaco', 'value'),
         State('input-dosaggio-farmaco', 'value'),
         State('input-data-assunzione', 'value'),
         State('input-ora-assunzione', 'value'),
         State('textarea-note-assunzione', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_assunzione(n_clicks, nome_farmaco, dosaggio, data_assunzione, ora, note):
        """Salva l'assunzione di farmaco nel database"""
        if not n_clicks:
            return dash.no_update
        
        # Validazione campi obbligatori
        if not nome_farmaco or not dosaggio or not data_assunzione or not ora:
            return get_error_message("Per favore compila tutti i campi obbligatori!")
        
        # Validazione lunghezza campi
        if len(nome_farmaco.strip()) < 2:
            return get_error_message("Il nome del farmaco deve essere di almeno 2 caratteri!")
        
        if len(dosaggio.strip()) < 1:
            return get_error_message("Il dosaggio non può essere vuoto!")
        
        # Validazione date
        try:
            data_inserita = datetime.strptime(data_assunzione, '%Y-%m-%d').date()
            data_oggi = datetime.now().date()
            data_minima = datetime(1900, 1, 1).date()
            
            if data_inserita > data_oggi:
                return get_error_message("La data di assunzione non può essere nel futuro!")
            
            if data_inserita < data_minima:
                return get_error_message("La data di assunzione non può essere precedente al 1900!")
                
        except ValueError:
            return get_error_message("Formato data non valido!")
        
        # Validazione ora
        try:
            ora_obj = datetime.strptime(ora, '%H:%M').time()
        except ValueError:
            return get_error_message("Formato ora non valido!")
        
        try:
            # Trova il paziente corrente
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            # Combina data e ora
            data_ora = datetime.combine(data_inserita, ora_obj)
            
            # Crea e salva l'assunzione
            assunzione = Assunzione(
                paziente=paziente,
                nome_farmaco=nome_farmaco.strip(),
                dosaggio=dosaggio.strip(),
                data_ora=data_ora,
                note=note.strip() if note else ''
            )
            commit()
            
            return get_assunzione_success_message(nome_farmaco, dosaggio, data_ora)
            
        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-nuova-assunzione-bis', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_new_assunzione_form(n_clicks):
        """Mostra un nuovo form assunzione dopo aver salvato"""
        if n_clicks:
            return get_nuova_assunzione_form()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-annulla-assunzione', 'n_clicks'),
        prevent_initial_call=True
    )
    def cancel_assunzione_form(n_clicks):
        """Nasconde il form assunzione quando si clicca annulla"""
        if n_clicks:
            return html.Div()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-sintomi-trattamenti', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_sintomi_form(n_clicks):
        """Mostra il form per registrare sintomi e trattamenti"""
        if n_clicks:
            return get_sintomi_trattamenti_form()
        return dash.no_update

    @app.callback(
        Output('campi-sintomi-container', 'style'),
        Input('select-tipo-sintomo', 'value')
    )
    def toggle_campi_sintomi(tipo_sintomo):
        """Mostra/nasconde i campi intensità e frequenza per i sintomi"""
        if tipo_sintomo == 'sintomo':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-salva-sintomo', 'n_clicks'),
        [State('select-tipo-sintomo', 'value'),
         State('input-descrizione-sintomo', 'value'),
         State('input-data-inizio-sintomo', 'value'),
         State('input-data-fine-sintomo', 'value'),
         State('select-frequenza-sintomo', 'value'),
         State('textarea-note-sintomo', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_sintomo(n_clicks, tipo, descrizione, data_inizio, data_fine, frequenza, note):
        """Salva il sintomo/patologia/trattamento nel database"""
        if not n_clicks:
            return dash.no_update
        
        # Validazione campi obbligatori
        if not tipo or not descrizione or not data_inizio:
            return get_error_message("Per favore compila tutti i campi obbligatori!")
        
        if tipo == 'sintomo' and not frequenza:
            return get_error_message("Per favore seleziona la frequenza del sintomo!")
        
        # Validazione lunghezza descrizione
        if len(descrizione.strip()) < 2:
            return get_error_message("La descrizione deve essere di almeno 2 caratteri!")
        
        # Validazione date
        try:
            data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d').date()
            data_oggi = datetime.now().date()
            data_minima = datetime(1900, 1, 1).date()
            
            if data_inizio_obj > data_oggi:
                return get_error_message("La data di inizio non può essere nel futuro!")
            
            if data_inizio_obj < data_minima:
                return get_error_message("La data di inizio non può essere precedente al 1900!")
                
        except ValueError:
            return get_error_message("Formato data inizio non valido!")
        
        # Validazione data fine se presente
        data_fine_obj = None
        if data_fine and data_fine.strip():
            try:
                data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d').date()
                
                if data_fine_obj > data_oggi:
                    return get_error_message("La data di fine non può essere nel futuro!")
                
                if data_fine_obj < data_inizio_obj:
                    return get_error_message("La data di fine non può essere precedente alla data di inizio!")
                    
            except ValueError:
                return get_error_message("Formato data fine non valido!")
        
        try:
            # Trova il paziente corrente
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            # Crea e salva il sintomo/patologia/trattamento
            sintomo = Sintomi(
                paziente=paziente,
                tipo=tipo,
                descrizione=descrizione.strip(),
                data_inizio=data_inizio_obj,
                data_fine=data_fine_obj,
                frequenza=frequenza if tipo == 'sintomo' else '',
                note=note.strip() if note else ''
            )
            commit()
            
            return get_sintomi_success_message(tipo, descrizione, data_inizio_obj, data_fine_obj)
            
        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-nuovo-sintomo', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_new_sintomo_form(n_clicks):
        """Mostra un nuovo form sintomi dopo aver salvato"""
        if n_clicks:
            return get_sintomi_trattamenti_form()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-annulla-sintomo', 'n_clicks'),
        prevent_initial_call=True
    )
    def cancel_sintomo_form(n_clicks):
        """Nasconde il form sintomi quando si clicca annulla"""
        if n_clicks:
            return html.Div()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-miei-dati', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_miei_dati(n_clicks):
        """Mostra la vista dei dati personali"""
        if n_clicks:
            return get_miei_dati_view()
        return dash.no_update