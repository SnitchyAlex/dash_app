# controller/doctor.py
"""Controller per la gestione dei medici"""
import dash
from dash.dependencies import Input, Output, State
from flask_login import current_user
from dash import html
from datetime import datetime
from pony.orm import db_session, commit, select
from model.terapia import Terapia
from model.medico import Medico
from model.paziente import Paziente
from view.doctor import (
    get_assegna_terapia_form,
    get_terapia_success_message,
    get_error_message,
    get_indicazioni_display
)


def register_doctor_callbacks(app):
    """Registra tutti i callback per i medici"""
    
    @app.callback(
        Output('doctor-content', 'children'),
        Input('btn-assegna-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_assegna_terapia_form(n_clicks):
        """Mostra il form per assegnare una terapia"""
        print(f"DEBUG: n_clicks = {n_clicks}")  # Debug
        print(f"DEBUG: current_user.username = {current_user.username}")  # Debug
        
        if n_clicks:
            # Recupera il medico corrente per verificare che sia un medico
            medico = Medico.get(username=current_user.username)
            print(f"DEBUG: medico trovato = {medico}")  # Debug
            
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            # MODIFICA: Prendi TUTTI i pazienti del sistema, non solo quelli associati
            pazienti = list(Paziente.select())  # Converte il QueryResultIterator in lista
            print(f"DEBUG: numero pazienti totali = {len(pazienti)}")  # Debug
            
            return get_assegna_terapia_form(pazienti)
        return dash.no_update

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-salva-terapia', 'n_clicks'),
        [State('select-paziente-terapia', 'value'),
         State('input-nome-farmaco-terapia', 'value'),
         State('input-dosaggio-terapia', 'value'),
         State('input-assunzioni-giornaliere', 'value'),
         State('select-indicazioni-terapia', 'value'),
         State('textarea-indicazioni-terapia', 'value'),
         State('input-data-inizio-terapia', 'value'),
         State('input-data-fine-terapia', 'value'),
         State('textarea-note-terapia', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_terapia(n_clicks, paziente_id, nome_farmaco, dosaggio, assunzioni_giornaliere, 
                     indicazioni_select, indicazioni_custom, data_inizio, data_fine, note):
        """Salva la terapia assegnata nel database"""
        if not n_clicks:
            return dash.no_update
        
        # Validazione campi obbligatori
        if not paziente_id or not nome_farmaco or not dosaggio or not assunzioni_giornaliere:
            return get_error_message("Per favore compila tutti i campi obbligatori e inserisci un numero di assunzioni valido!")
        
        # Validazione lunghezza campi
        if len(nome_farmaco.strip()) < 2:
            return get_error_message("Il nome del farmaco deve essere di almeno 2 caratteri!")
        
        if len(dosaggio.strip()) < 1:
            return get_error_message("Il dosaggio non può essere vuoto!")
        
        # Validazione numero assunzioni
        try:
            assunzioni = int(assunzioni_giornaliere)
            if assunzioni < 1 or assunzioni > 10:
                return get_error_message("Il numero di assunzioni giornaliere deve essere tra 1 e 10!")
        except ValueError:
            return get_error_message("Numero di assunzioni non valido!")
        
        # Validazione date
        data_inizio_obj = None
        if data_inizio:
            try:
                data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d')
                data_oggi = datetime.now()
                data_minima = datetime(1900, 1, 1)
                
                if data_inizio_obj < data_minima:
                    return get_error_message("La data di inizio non può essere precedente al 1900!")
                    
            except ValueError:
                return get_error_message("Formato data inizio non valido!")
        
        # Validazione data fine se presente
        data_fine_obj = None
        if data_fine and data_fine.strip():
            try:
                data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d')
                
                if data_inizio_obj and data_fine_obj < data_inizio_obj:
                    return get_error_message("La data di fine non può essere precedente alla data di inizio!")
                    
            except ValueError:
                return get_error_message("Formato data fine non valido!")
        
        try:
            # Trova il medico corrente
            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            # Trova il paziente selezionato (qualsiasi paziente del sistema)
            paziente = Paziente.get(username=paziente_id)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            # MODIFICA: Rimuovi il controllo che limitava solo ai pazienti associati
            # Il medico può ora assegnare terapie a qualsiasi paziente
            
            # Combina le indicazioni
            indicazioni_complete = []
            if indicazioni_select:
                indicazioni_complete.append(get_indicazioni_display(indicazioni_select))
            if indicazioni_custom and indicazioni_custom.strip():
                indicazioni_complete.append(indicazioni_custom.strip())
            
            indicazioni_finali = ". ".join(indicazioni_complete) if indicazioni_complete else ""
            
            # Crea e salva la terapia
            terapia = Terapia(
                medico=medico,
                medico_nome=f"Dr. {medico.name} {medico.surname}",
                paziente=paziente,
                nome_farmaco=nome_farmaco.strip(),
                dosaggio_per_assunzione=dosaggio.strip(),
                assunzioni_giornaliere=assunzioni,
                indicazioni=indicazioni_finali if indicazioni_finali else None,
                data_inizio=data_inizio_obj,
                data_fine=data_fine_obj,
                note=note.strip() if note else ''
            )
            commit()
            
            paziente_nome = f"{paziente.name} {paziente.surname}"
            return get_terapia_success_message(
                paziente_nome, nome_farmaco, dosaggio, assunzioni, 
                data_inizio_obj, data_fine_obj
            )
            
        except ValueError as e:
            return get_error_message(f"Errore nei dati inseriti: {str(e)}")
        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-nuova-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_new_terapia_form(n_clicks):
        """Mostra un nuovo form terapia dopo aver salvato"""
        if n_clicks:
            medico = Medico.get(username=current_user.username)
            if medico:
                # MODIFICA: Prendi tutti i pazienti, non solo quelli associati al medico
                pazienti = list(Paziente.select())
                return get_assegna_terapia_form(pazienti)
        return dash.no_update

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-annulla-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    def cancel_terapia_form(n_clicks):
        """Nasconde il form terapia quando si clicca annulla"""
        if n_clicks:
            return html.Div()
        return dash.no_update