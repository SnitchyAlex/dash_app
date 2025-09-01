# controller/doctor.py
"""Controller per la gestione dei medici"""
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import html
from datetime import datetime, timedelta
from pony.orm import db_session, commit, select
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime as _dt
import json

from model.terapia import Terapia
from model.medico import Medico
from model.paziente import Paziente
from view.doctor import *


def register_doctor_callbacks(app):
    """Registra tutti i callback per i medici"""

    # HELPER FUNCTIONS
    @db_session
    def get_current_medico():
        """Helper per ottenere il medico corrente"""
        return Medico.get(username=current_user.username)

    def validate_terapia_data(nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine):
        """Valida i dati della terapia"""
        if not nome_farmaco or not dosaggio or not assunzioni_giornaliere:
            return "Per favore compila tutti i campi obbligatori!"
        
        if len(nome_farmaco.strip()) < 2:
            return "Il nome del farmaco deve essere di almeno 2 caratteri!"
        
        if len(dosaggio.strip()) < 1:
            return "Il dosaggio non può essere vuoto!"
        
        try:
            assunzioni = int(assunzioni_giornaliere)
            if assunzioni < 1 or assunzioni > 10:
                return "Il numero di assunzioni giornaliere deve essere tra 1 e 10!"
        except ValueError:
            return "Numero di assunzioni non valido!"
        
        # Validazione date
        data_inizio_obj = None
        if data_inizio:
            try:
                data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d')
                if data_inizio_obj < datetime(1900, 1, 1):
                    return "La data di inizio non può essere precedente al 1900!"
            except ValueError:
                return "Formato data inizio non valido!"
        
        data_fine_obj = None
        if data_fine and data_fine.strip():
            try:
                data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d')
                if data_inizio_obj and data_fine_obj < data_inizio_obj:
                    return "La data di fine non può essere precedente alla data di inizio!"
            except ValueError:
                return "Formato data fine non valido!"
        
        return None  # Nessun errore

    def parse_composite_key(composite_key):
        """Parse della chiave composita per le terapie"""
        parts = composite_key.split('|')
        if len(parts) != 4:
            raise ValueError("Formato chiave terapia non valido!")
        
        medico_nome, paziente_username, nome_farmaco, data_inizio_str = parts
        
        if data_inizio_str == 'None':
            data_inizio_obj = None
        else:
            data_inizio_obj = datetime.strptime(data_inizio_str, '%Y-%m-%d')
        
        return medico_nome, paziente_username, nome_farmaco, data_inizio_obj

    def get_terapia_from_composite_key(composite_key):
        """Trova una terapia usando la chiave composita"""
        medico_nome, paziente_username, nome_farmaco, data_inizio_obj = parse_composite_key(composite_key)
        
        paziente = Paziente.get(username=paziente_username)
        if not paziente:
            raise ValueError("Paziente non trovato!")
        
        terapia = Terapia.get(
            medico_nome=medico_nome,
            paziente=paziente,
            nome_farmaco=nome_farmaco,
            data_inizio=data_inizio_obj
        )
        
        if not terapia:
            raise ValueError("Terapia non trovata!")
        
        return terapia, paziente

    def check_medico_paziente_authorization(medico, paziente):
        """Verifica che il medico possa gestire questo paziente"""
        if medico not in paziente.doctors:
            return get_error_message(
                f"Accesso negato: Non sei autorizzato a gestire i dati del paziente {paziente.name} {paziente.surname}."
            )
        return None

    # MENU NAVIGATION CALLBACKS
    @app.callback(
        Output('doctor-content', 'children'),
        Input('btn-gestisci-terapie', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_terapie_menu(n_clicks):
        return get_terapie_menu() if n_clicks else dash.no_update

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-torna-menu-principale', 'n_clicks'),
        prevent_initial_call=True
    )
    def torna_menu_principale(n_clicks):
        return get_doctor_welcome_content() if n_clicks else dash.no_update
    
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        [Input('btn-torna-menu-terapie', 'n_clicks')],
        prevent_initial_call=True
    )
    def torna_menu_terapie(n_clicks):
        return get_terapie_menu() if n_clicks else dash.no_update

    # TERAPIA FORM DISPLAYS
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-assegna-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_assegna_terapia_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")
        
        pazienti = list(Paziente.select())
        return get_assegna_terapia_form(pazienti)

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-modifica-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_modifica_terapia_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")
        
        pazienti = list(Paziente.select())
        return get_modifica_terapia_form(pazienti)

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-elimina-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_elimina_terapia_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")
        
        pazienti = list(Paziente.select())
        return get_elimina_terapia_form(pazienti)

    # TERAPIA CRUD OPERATIONS
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
        if not n_clicks:
            return dash.no_update

        # Validazione
        validation_error = validate_terapia_data(nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine)
        if validation_error:
            return get_error_message(validation_error)

        try:
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=paziente_id)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")

            # Assegna automaticamente il paziente al medico se necessario
            if medico not in paziente.doctors:
                paziente.doctors.add(medico)
                commit()

            # Processa indicazioni
            indicazioni_complete = []
            if indicazioni_select:
                indicazioni_complete.append(get_indicazioni_display(indicazioni_select))
            if indicazioni_custom and indicazioni_custom.strip():
                indicazioni_complete.append(indicazioni_custom.strip())
            
            indicazioni_finali = ". ".join(indicazioni_complete) if indicazioni_complete else ""

            # Converti date
            data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d') if data_inizio else None
            data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d') if data_fine and data_fine.strip() else None

            # Crea terapia
            terapia = Terapia(
                medico=medico,
                medico_nome=f"Dr. {medico.name} {medico.surname}",
                paziente=paziente,
                nome_farmaco=nome_farmaco.strip(),
                dosaggio_per_assunzione=dosaggio.strip(),
                assunzioni_giornaliere=int(assunzioni_giornaliere),
                indicazioni=indicazioni_finali if indicazioni_finali else '',
                data_inizio=data_inizio_obj,
                data_fine=data_fine_obj,
                note=note.strip() if note else ''
            )
            commit()

            paziente_nome = f"{paziente.name} {paziente.surname}"
            return get_terapia_success_message(
                paziente_nome, nome_farmaco, dosaggio, int(assunzioni_giornaliere),
                data_inizio_obj, data_fine_obj
            )

        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-nuova-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_new_terapia_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if medico:
            pazienti = list(Paziente.select())
            return get_assegna_terapia_form(pazienti)
        return dash.no_update

    # PATIENT THERAPY LISTS
    @app.callback(
        Output('terapie-paziente-list', 'children'),
        Input('select-paziente-modifica', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def show_patient_therapies_for_edit(patient_username):
        if not patient_username:
            return dash.no_update

        try:
            paziente = Paziente.get(username=patient_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")

            terapie = paziente.terapies

            if not terapie:
                return dbc.Alert([
                    html.H6("Nessuna terapia trovata", className="alert-heading"),
                    html.P(f"Il paziente {paziente.name} {paziente.surname} non ha terapie assegnate.")
                ], color="info")

            return get_terapie_list_for_edit(terapie, paziente)

        except Exception as e:
            return get_error_message(f"Errore: {str(e)}")

    @app.callback(
        Output('terapie-paziente-elimina-list', 'children'),
        Input('select-paziente-elimina', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def show_patient_therapies_for_delete(patient_username):
        if not patient_username:
            return dash.no_update

        try:
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=patient_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")

            terapie = paziente.terapies

            if not terapie:
                return dbc.Alert([
                    html.H6("Nessuna terapia trovata", className="alert-heading"),
                    html.P(f"Il paziente {paziente.name} {paziente.surname} non ha terapie assegnate.")
                ], color="info")

            return get_terapie_list_for_delete(terapie, paziente)

        except Exception as e:
            return get_error_message(f"Errore: {str(e)}")

    # THERAPY MODIFICATION
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input({'type': 'btn-modifica-terapia-specifica', 'index': dash.dependencies.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def load_therapy_for_edit(n_clicks_list):
        if not any(n_clicks_list):
            return dash.no_update

        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        try:
            # Parse button ID
            button_id = ctx.triggered[0]['prop_id']
            json_start = button_id.find('{')
            json_end = button_id.rfind('}') + 1
            button_data = json.loads(button_id[json_start:json_end])
            composite_key = button_data['index']

            terapia, paziente = get_terapia_from_composite_key(composite_key)

            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            auth_error = check_medico_paziente_authorization(medico, paziente)
            if auth_error:
                return auth_error

            pazienti = list(Paziente.select())
            return get_edit_terapia_form(terapia, pazienti)

        except (json.JSONDecodeError, ValueError) as e:
            return get_error_message(f"Errore nel parsing: {str(e)}")
        except Exception as e:
            return get_error_message(f"Errore nel caricamento della terapia: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-salva-modifiche-terapia', 'n_clicks'),
        [State('hidden-terapia-key', 'children'),
         State('select-paziente-terapia-edit', 'value'),
         State('input-nome-farmaco-terapia-edit', 'value'),
         State('input-dosaggio-terapia-edit', 'value'),
         State('input-assunzioni-giornaliere-edit', 'value'),
         State('select-indicazioni-terapia-edit', 'value'),
         State('textarea-indicazioni-terapia-edit', 'value'),
         State('input-data-inizio-terapia-edit', 'value'),
         State('input-data-fine-terapia-edit', 'value'),
         State('textarea-note-terapia-edit', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_therapy_modifications(n_clicks, terapia_key, paziente_id, nome_farmaco, dosaggio,
                                  assunzioni_giornaliere, indicazioni_select, indicazioni_custom,
                                  data_inizio, data_fine, note):
        if not n_clicks:
            return dash.no_update

        # Validazione
        validation_error = validate_terapia_data(nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine)
        if validation_error:
            return get_error_message(validation_error)

        if not terapia_key or not paziente_id:
            return get_error_message("Dati mancanti per il salvataggio!")

        try:
            terapia, paziente_orig = get_terapia_from_composite_key(terapia_key)

            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            auth_error = check_medico_paziente_authorization(medico, paziente_orig)
            if auth_error:
                return auth_error

            paziente_nuovo = Paziente.get(username=paziente_id)
            if not paziente_nuovo:
                return get_error_message("Nuovo paziente non trovato!")

            # Processa indicazioni
            indicazioni_complete = []
            if indicazioni_select:
                indicazioni_complete.append(get_indicazioni_display(indicazioni_select))
            if indicazioni_custom and indicazioni_custom.strip():
                indicazioni_complete.append(indicazioni_custom.strip())
            
            indicazioni_finali = ". ".join(indicazioni_complete) if indicazioni_complete else ""

            # Converti date
            data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d') if data_inizio else None
            data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d') if data_fine and data_fine.strip() else None

            # Se la chiave primaria cambia, elimina e ricrea
            if (paziente_nuovo != terapia.paziente or
                nome_farmaco.strip() != terapia.nome_farmaco or
                data_inizio_obj != terapia.data_inizio):

                medico_orig = terapia.medico
                terapia.delete()
                commit()

                terapia_nuova = Terapia(
                    medico=medico_orig,
                    medico_nome=f"Dr. {medico.name} {medico.surname}",
                    paziente=paziente_nuovo,
                    nome_farmaco=nome_farmaco.strip(),
                    dosaggio_per_assunzione=dosaggio.strip(),
                    assunzioni_giornaliere=int(assunzioni_giornaliere),
                    indicazioni=indicazioni_finali if indicazioni_finali else '',
                    data_inizio=data_inizio_obj,
                    data_fine=data_fine_obj,
                    note=note.strip() if note else '',
                    modificata=f"Dr. {medico.name} {medico.surname}"
                )
            else:
                # Aggiorna direttamente
                terapia.dosaggio_per_assunzione = dosaggio.strip()
                terapia.assunzioni_giornaliere = int(assunzioni_giornaliere)
                terapia.indicazioni = indicazioni_finali if indicazioni_finali else ''
                terapia.data_fine = data_fine_obj
                terapia.note = note.strip() if note else ''
                terapia.modificata = f"Dr. {medico.name} {medico.surname}"

            commit()

            paziente_nome = f"{paziente_nuovo.name} {paziente_nuovo.surname}"
            return get_terapia_modify_success_message(
                paziente_nome, nome_farmaco, dosaggio, int(assunzioni_giornaliere),
                data_inizio_obj, data_fine_obj
            )

        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-modifica-altra-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_modify_another_therapy_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if medico:
            pazienti = list(Paziente.select())
            return get_modifica_terapia_form(pazienti)
        return dash.no_update

    # THERAPY DELETION
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input({'type': 'btn-elimina-terapia-specifica', 'index': dash.dependencies.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def delete_specific_therapy(n_clicks_list):
        if not any(n_clicks_list):
            return dash.no_update

        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        try:
            # Parse button ID
            button_id = ctx.triggered[0]['prop_id']
            json_start = button_id.find('{')
            json_end = button_id.rfind('}') + 1
            button_data = json.loads(button_id[json_start:json_end])
            composite_key = button_data['index']

            terapia, paziente = get_terapia_from_composite_key(composite_key)

            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            auth_error = check_medico_paziente_authorization(medico, paziente)
            if auth_error:
                return auth_error

            # Salva dati per messaggio conferma
            paziente_nome = f"{terapia.paziente.name} {terapia.paziente.surname}"
            farmaco_eliminato = terapia.nome_farmaco
            dosaggio_eliminato = terapia.dosaggio_per_assunzione

            terapia.delete()
            commit()

            return get_terapia_delete_success_message(
                paziente_nome, farmaco_eliminato, dosaggio_eliminato
            )

        except (json.JSONDecodeError, ValueError) as e:
            return get_error_message(f"Errore nel parsing: {str(e)}")
        except Exception as e:
            return get_error_message(f"Errore nell'eliminazione della terapia: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-elimina-altra-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_delete_another_therapy_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if medico:
            pazienti = list(Paziente.select())
            return get_elimina_terapia_form(pazienti)
        return dash.no_update

    # PATIENT DATA MANAGEMENT
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-dati-paziente', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_dati_pazienti_menu(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")

        pazienti_lista = list(Paziente.select())
        return get_dati_pazienti_menu(pazienti_lista)

    @app.callback(
        Output('dati-paziente-display', 'children'),
        Input('select-paziente-dati', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def show_patient_data(patient_username):
        if not patient_username:
            return dash.no_update

        try:
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=patient_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")

            can_modify = medico in paziente.doctors
            return get_patient_data_display(paziente, can_modify)

        except Exception as e:
            return get_error_message(f"Errore: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-modifica-dati-paziente', 'n_clicks'),
        State('select-paziente-dati', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def show_edit_patient_data_form(n_clicks, patient_username):
        if not n_clicks or not patient_username:
            return dash.no_update

        try:
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=patient_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")

            auth_error = check_medico_paziente_authorization(medico, paziente)
            if auth_error:
                return auth_error

            return get_edit_patient_data_form(paziente)

        except Exception as e:
            return get_error_message(f"Errore: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-salva-dati-paziente', 'n_clicks'),
        [State('hidden-patient-username', 'children'),
         State('textarea-fattori-rischio', 'value'),
         State('textarea-pregresse-patologie', 'value'),
         State('textarea-comorbidita', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_patient_data_modifications(n_clicks, patient_username, fattori_rischio,
                                       pregresse_patologie, comorbidita):
        if not n_clicks or not patient_username:
            return dash.no_update

        try:
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=patient_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")

            auth_error = check_medico_paziente_authorization(medico, paziente)
            if auth_error:
                return auth_error

            # Aggiorna i dati clinici
            paziente.fattori_rischio = fattori_rischio.strip() if fattori_rischio else None
            paziente.pregresse_patologie = pregresse_patologie.strip() if pregresse_patologie else None
            paziente.comorbidita = comorbidita.strip() if comorbidita else None
            paziente.info_aggiornate = f"Dr. {medico.name} {medico.surname}"

            commit()

            paziente_nome = f"{paziente.name} {paziente.surname}"
            return get_patient_data_update_success_message(paziente_nome)

        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    # NAVIGATION CALLBACKS FOR PATIENT DATA
    def create_patient_menu_callback(button_input, callback_name):
        """Factory per creare callback che tornano al menu dati pazienti"""
        @app.callback(
            Output('doctor-content', 'children', allow_duplicate=True),
            Input(button_input, 'n_clicks'),
            *([State('hidden-patient-username', 'children')] if 'annulla' in button_input else []),
            prevent_initial_call=True
        )
        @db_session
        def callback_func(n_clicks, *args):
            if not n_clicks:
                return dash.no_update
            
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            pazienti = list(Paziente.select())
            return get_dati_pazienti_menu(pazienti)
        
        # Rinomina la funzione per evitare conflitti
        callback_func.__name__ = callback_name
        return callback_func

    # Crea i callback per la navigazione dei dati pazienti
    create_patient_menu_callback('btn-annulla-modifica-dati', 'cancel_patient_data_edit')
    create_patient_menu_callback('btn-altro-paziente', 'show_another_patient_menu')
    create_patient_menu_callback('btn-visualizza-dati-aggiornati', 'show_updated_patient_data')
    create_patient_menu_callback('btn-gestisci-altri-pazienti', 'manage_other_patients')

    # FOLLOW PATIENT MANAGEMENT
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-segui-pazienti', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_segui_paziente_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")

        tutti_pazienti = list(Paziente.select())
        pazienti_seguiti = list(medico.patients)
        return get_segui_paziente_form(tutti_pazienti, pazienti_seguiti, medico)

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-conferma-segui-paziente', 'n_clicks'),
        State('select-nuovo-paziente-seguire', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def conferma_segui_paziente(n_clicks, paziente_username):
        if not n_clicks or not paziente_username:
            return dash.no_update

        try:
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=paziente_username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")

            paziente_nome = f"{paziente.name} {paziente.surname}"

            if paziente in medico.patients:
                return get_paziente_gia_seguito_message(paziente_nome)

            medico.patients.add(paziente)
            commit()

            return get_segui_paziente_success_message(paziente_nome, paziente_username)

        except Exception as e:
            return get_error_message(f"Errore durante l'operazione: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-conferma-medico-riferimento', 'n_clicks'),
        State('select-nuovo-medico-riferimento', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def conferma_medico_riferimento(n_clicks, paziente_username):
        if not n_clicks or not paziente_username:
            return dash.no_update

        try:
            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=paziente_username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")

            paziente_nome = f"{paziente.name} {paziente.surname}"

            if paziente.medico_riferimento is not None:
                medico_attuale = paziente.medico_riferimento
                return get_error_message(
                    f"Il paziente {paziente_nome} ha già un medico di riferimento: "
                    f"Dr. {medico_attuale.name} {medico_attuale.surname}."
                )

            paziente.medico_riferimento = medico
            
            if paziente not in medico.patients:
                medico.patients.add(paziente)
            
            commit()

            return get_segui_come_medico_riferimento_success_message(paziente_nome, paziente_username)

        except Exception as e:
            return get_error_message(f"Errore durante l'operazione: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input({'type': 'btn-smetti-seguire-paziente', 'index': dash.dependencies.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def smetti_seguire_paziente_specifico(n_clicks_list):
        if not any(n_clicks_list):
            return dash.no_update

        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        try:
            button_id = ctx.triggered[0]['prop_id']
            json_start = button_id.find('{')
            json_end = button_id.rfind('}') + 1
            button_data = json.loads(button_id[json_start:json_end])
            paziente_username = button_data['index']

            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            paziente = Paziente.get(username=paziente_username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")

            if paziente not in medico.patients:
                return get_error_message("Non stai seguendo questo paziente.")

            medico.patients.remove(paziente)

            if paziente.medico_riferimento == medico:
                paziente.medico_riferimento = None
    
            commit()

            tutti_pazienti = list(Paziente.select())
            pazienti_seguiti = list(medico.patients)
            return get_segui_paziente_form(tutti_pazienti, pazienti_seguiti, medico)

        except Exception as e:
            return get_error_message(f"Errore durante la rimozione: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-segui-altro-paziente', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_segui_altro_paziente_form(n_clicks):
        if not n_clicks:
            return dash.no_update
        
        medico = get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")

        tutti_pazienti = list(Paziente.select())
        pazienti_seguiti = list(medico.patients)
        return get_segui_paziente_form(tutti_pazienti, pazienti_seguiti, medico)
    
    @app.callback(
    Output('doctor-content', 'children', allow_duplicate=True),
    Input('btn-miei-pazienti', 'n_clicks'),
    prevent_initial_call=True
    )
    @db_session
    def show_miei_pazienti(n_clicks):
        if not n_clicks:
            return dash.no_update
    
        medico = get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")
    
        return get_miei_pazienti_view(medico)

    # STATISTICS AND CHARTS
    @app.callback(
        Output("doctor-content", "children", allow_duplicate=True),
        Input("btn-statistiche", "n_clicks"),
        prevent_initial_call=True
    )
    @db_session
    def show_andamenti_glicemici_medico(n_clicks):
        if not n_clicks:
            return dash.no_update
        return get_andamento_glicemico_medico_view()

    @app.callback(
        Output("doctor-patient-selector", "options"),
        Input("doctor-content", "children"),
        prevent_initial_call=False
    )
    @db_session
    def load_patients_options(_children):
        patients = list(Paziente.select())
        options = []
        for p in patients:
            cognome = (p.surname or "").strip()
            nome = (p.name or "").strip()
            label = f"{cognome} {nome} ({p.username})".strip()
            label = " ".join(label.split())
            options.append({"label": label, "value": p.username})
        return options

    @app.callback(
        Output("doctor-week-dow", "figure"),
        Output("doctor-weekly-avg", "figure"),
        Output("doctor-monthly-avg", "figure"),
        Input("doctor-patient-selector", "value"),
        Input("weeks-window-medico", "value"),
        prevent_initial_call=True
    )
    @db_session
    def render_week_month_charts_medico(selected_username, weeks_window):
        def empty_fig(msg):
            f = go.Figure()
            f.update_yaxes(range=[0, 300], title="mg/dL")
            f.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            f.update_layout(
                height=360, margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="white", paper_bgcolor="white", hovermode="x unified"
            )
            f.update_xaxes(showline=True, linecolor="black", linewidth=1)
            f.update_yaxes(showline=True, linecolor="black", linewidth=1)
            return f

        if not selected_username:
            ef = empty_fig("Seleziona un paziente")
            return ef, ef, ef

        paz = Paziente.get(username=selected_username)
        all_meas = list(paz.rilevazione) if paz else []

        if not all_meas:
            ef = empty_fig("Nessuna glicemia registrata")
            return ef, ef, ef

        df = pd.DataFrame(
            [(m.data_ora, m.valore) for m in all_meas],
            columns=["data", "valore"]
        ).set_index("data").sort_index()

        # A) Giorni della settimana (settimana corrente)
        today = _dt.now()
        start_week = (today - timedelta(days=today.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_week = start_week + timedelta(days=7)

        week_df = df.loc[(df.index >= start_week) & (df.index < end_week)].copy()

        fig_dow = go.Figure()
        fig_dow.update_yaxes(range=[0, 300], title="mg/dL")

        dow_order = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        fig_dow.update_xaxes(categoryorder="array", categoryarray=dow_order, title="Giorno della settimana")

        if not week_df.empty:
            week_df["giorno_label"] = week_df.index.dayofweek.map({
                0: "Lunedì", 1: "Martedì", 2: "Mercoledì",
                3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"
            })
            daily_mean = week_df.groupby("giorno_label")["valore"].mean().reindex(dow_order)

            fig_dow.add_trace(go.Scatter(
                x=dow_order, y=daily_mean.values,
                mode="lines+markers", name="Media giorno",
                line=dict(color="#F58518", width=2), connectgaps=True
            ))

            add_glucose_reference_lines(fig_dow, dow_order)
        else:
            fig_dow.add_annotation(
                text="Nessun dato nella settimana corrente",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )

        # B) Media settimana per settimana
        weeks_window = weeks_window or 8
        since = _dt.now() - timedelta(weeks=int(weeks_window))
        recent = df.loc[df.index >= since].copy()
        weekly_mean = recent["valore"].resample("W-MON", label="left", closed="left").mean()
        
        fig_week = go.Figure()
        fig_week.update_yaxes(range=[0, 300], title="mg/dL")

        if not weekly_mean.empty:
            x_labels = [
                (ts.strftime("%d/%m") + "→" + (ts + timedelta(days=6)).strftime("%d/%m"))
                for ts in weekly_mean.index
            ]

            fig_week.add_trace(go.Scatter(
                x=x_labels, y=weekly_mean.values,
                mode="lines+markers",
                name=f"Media settimanale (ultime {weeks_window} sett.)",
                line=dict(color="#4C78A8", width=2), connectgaps=True
            ))

            add_glucose_reference_lines(fig_week, x_labels)
        else:
            fig_week.add_annotation(
                text="Nessuna settimana con dati nel periodo",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
        
        fig_week.update_layout(xaxis_title="Settimana (Lun→Dom)")

        # C) Media mese per mese (anno corrente)
        year = _dt.now().year
        year_start = pd.Timestamp(year=year, month=1, day=1)
        idx_months = pd.date_range(start=year_start, periods=12, freq="MS")
        df_year = df.loc[
            (df.index >= year_start) & 
            (df.index < year_start + pd.offsets.YearEnd(0) + pd.Timedelta(days=1))
        ].copy()
        monthly_mean = df_year["valore"].resample("MS").mean().reindex(idx_months)

        mesi_it = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
                   "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
        x_m = [mesi_it[ts.month - 1] for ts in monthly_mean.index]

        fig_month = go.Figure()
        fig_month.update_yaxes(range=[0, 300], title="mg/dL")

        fig_month.add_trace(go.Scatter(
            x=x_m, y=monthly_mean.values,
            mode="lines+markers", name=f"Media mensile {year}",
            line=dict(color="#4C78A8", width=2), connectgaps=True
        ))

        if monthly_mean.isna().all():
            fig_month.add_annotation(
                text="Nessun dato per l'anno selezionato",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )

        add_glucose_reference_lines(fig_month, x_m)
        fig_month.update_layout(xaxis_title=f"Anno ({year})")

        for fig in (fig_dow, fig_week, fig_month):
            fig.update_layout(
                height=360, margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="white", paper_bgcolor="white", hovermode="x unified"
            )
            fig.update_xaxes(showline=True, linecolor="black", linewidth=1)
            fig.update_yaxes(showline=True, linecolor="black", linewidth=1)

        return fig_dow, fig_week, fig_month


def add_glucose_reference_lines(fig, x_labels):
    """Aggiunge le linee di riferimento per i valori glicemici"""
    fig.add_trace(go.Scatter(
        x=x_labels, y=[180] * len(x_labels),
        mode="lines", name="Glicemia superiore a 180",
        line=dict(color="red", dash="dash"), hoverinfo="skip"
    ))
    
    y_low, y_high = [80] * len(x_labels), [130] * len(x_labels)
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_low, mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip", legendgroup="norma"
    ))
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_high, mode="lines",
        line=dict(width=0), fill="tonexty",
        fillcolor="rgba(144,238,144,0.20)",
        name="Glicemia nella norma (80–130)",
        hoverinfo="skip", legendgroup="norma"
    ))