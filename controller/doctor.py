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
import re 

from model.terapia import Terapia
from model.medico import Medico
from model.paziente import Paziente
from model.glicemia import Glicemia
from model.assunzione import Assunzione
from view.doctor import *
# =============================================================================
# FUNZIONE CORE per salvataggio terapia (testabile)
# =============================================================================

@db_session
def save_terapia_core(
    n_clicks,
    paziente_id,
    nome_farmaco,
    dosaggio,
    assunzioni_giornaliere,
    indicazioni_select,
    data_inizio,
    data_fine,
    note,
    get_current_medico_func=None,   # injection per i test
):
    if not n_clicks:
        return dash.no_update

    # Validazione input (usa il validator già definito nel file)
    error = validate_terapia_data(nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine)
    if error:
        return get_error_message(error)

    try:
        medico = get_current_medico_func() if get_current_medico_func else get_current_medico()
        if not medico:
            return get_error_message("Errore: medico non trovato!")

        paziente = Paziente.get(username=paziente_id)
        if not paziente:
            return get_error_message("Errore: paziente non trovato!")

        # Associa medico a paziente se necessario
        if medico not in paziente.doctors:
            paziente.doctors.add(medico)
            commit()

        # Preparazione dati
        indicazioni_finali = get_indicazioni_display(indicazioni_select) if indicazioni_select else ""
        data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d') if data_inizio else None
        data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d') if data_fine and data_fine.strip() else None

        # Creazione terapia
        terapia = Terapia(
            medico=medico,
            medico_nome=f"Dr. {medico.name} {medico.surname}",
            paziente=paziente,
            nome_farmaco=nome_farmaco.strip(),
            dosaggio_per_assunzione=dosaggio.strip(),
            assunzioni_giornaliere=int(assunzioni_giornaliere),
            indicazioni=indicazioni_finali,
            data_inizio=data_inizio_obj,
            data_fine=data_fine_obj,
            note=note.strip() if note else ''
        )
        commit()

        return get_terapia_success_message(
            f"{paziente.name} {paziente.surname}",
            nome_farmaco, dosaggio, int(assunzioni_giornaliere),
            data_inizio_obj, data_fine_obj
        )

    except Exception as e:
        return get_error_message(f"Errore durante il salvataggio: {str(e)}")
# controller/doctor.py

@db_session
def save_patient_data_modifications_core(
    patient_username,
    fattori_rischio,
    pregresse_patologie,
    comorbidita,
    get_current_medico_func=None  # injection per i test
):
    """Core per aggiornamento dati paziente (testabile senza Dash)."""
    medico = get_current_medico_func() if get_current_medico_func else get_current_medico()
    if not medico:
        return get_error_message("Errore: medico non trovato!")

    paziente = Paziente.get(username=patient_username)
    if not paziente:
        return get_error_message("Paziente non trovato!")

    # Verifica autorizzazioni
    auth_error = check_medico_paziente_authorization(medico, paziente)
    if auth_error:
        return auth_error

    # Aggiornamento dati paziente
    paziente.fattori_rischio = fattori_rischio.strip() if fattori_rischio else None
    paziente.pregresse_patologie = pregresse_patologie.strip() if pregresse_patologie else None
    paziente.comorbidita = comorbidita.strip() if comorbidita else None
    paziente.info_aggiornate = f"Dr. {medico.name} {medico.surname}"

    commit()

    return get_patient_data_update_success_message(f"{paziente.name} {paziente.surname}")


# ===============================
# FUNZIONI DI SUPPORTO GLOBALI
# ===============================

def _normalize_string(s):
    """Normalizza una stringa rimuovendo spazi e convertendo in lowercase"""
    return re.sub(r"\s+", "", (s or "").strip().lower())

def _same_drug(a_nome, t_nome):
    """Confronta due nomi di farmaco normalizzati"""
    return _normalize_string(a_nome) == _normalize_string(t_nome)

def _same_dose(a_dose, t_dose):
    """Confronta due dosaggi normalizzati"""
    return _normalize_string(a_dose) == _normalize_string(t_dose)

def _matches_therapy(assunzione, terapia):
    """Verifica se un'assunzione corrisponde a una terapia"""
    if getattr(assunzione, "terapia", None) is not None:
        return assunzione.terapia == terapia
    
    return (_same_drug(assunzione.nome_farmaco, terapia.nome_farmaco) and
            _same_dose(assunzione.dosaggio, terapia.dosaggio_per_assunzione))

def _fmt_ctx(misura):
    """Formatta il contesto della misurazione glicemica"""
    momento = (getattr(misura, "momento_pasto", None) or "").strip().lower()
    
    if momento == "digiuno":
        return "a digiuno"
    elif momento == "prima_pasto":
        return "prima del pasto"
    elif momento == "dopo_pasto":
        due_ore = getattr(misura, "due_ore_pasto", None)
        if due_ore is True:
            return "dopo il pasto (≥ 2 ore)"
        elif due_ore is False:
            return "dopo il pasto (< 2 ore)"
        return "dopo il pasto"
    return None

def _is_anomalo_with_severity(valore, misura):
    """
    Determina la gravità di un valore glicemico anomalo.
    
    Returns:
        None: valore normale
        'warning': anomalo lieve (giallo)
        'danger-orange': anomalo moderato (arancione)
        'danger': anomalo critico (rosso)
    """
    if valore is None:
        return None

    try:
        v = float(valore)
    except (ValueError, TypeError):
        return None

    momento = (getattr(misura, "momento_pasto", None) or "").strip().lower()
    
    # Valori critici (ROSSI)
    if v < 54 or v > 250:
        return 'danger'
    
    if momento in ("digiuno", "prima_pasto") and v > 200:
        return 'danger'
    
    # Valori moderati (ARANCIONI)
    if 54 <= v <= 69:
        return 'danger-orange'
    
    if momento in ("digiuno", "prima_pasto") and 151 <= v <= 200:
        return 'danger-orange'
    elif momento == "dopo_pasto" and 201 <= v <= 250:
        return 'danger-orange'
    elif not momento and 201 <= v <= 250:  # momento non specificato
        return 'danger-orange'
    
    # Valori lievi (GIALLI)
    if 70 <= v <= 90:
        return 'warning'
    
    if momento in ("digiuno", "prima_pasto") and 131 <= v <= 150:
        return 'warning'
    elif momento == "dopo_pasto" and 181 <= v <= 200:
        return 'warning'
    elif not momento and 181 <= v <= 200:
        return 'warning'
    
    return None

def _is_anomalo(valore, misura):
    """Verifica se un valore glicemico è anomalo (compatibilità)"""
    return _is_anomalo_with_severity(valore, misura) is not None
# Helper per ottenere il medico corrente
@db_session
def get_current_medico():
    return Medico.get(name=current_user.name, surname=current_user.surname)
# ===============================
    # VALIDATORI 
    # ===============================
    
def validate_terapia_data(nome_farmaco, dosaggio, assunzioni_giornaliere, data_inizio, data_fine):
        """Valida i dati inseriti per una terapia"""
        if not all([nome_farmaco, dosaggio, assunzioni_giornaliere]):
            return "Compila tutti i campi obbligatori!"
        
        if len(nome_farmaco.strip()) < 2:
            return "Il nome del farmaco deve avere almeno 2 caratteri!"
        
        try:
            assunzioni = int(assunzioni_giornaliere)
            if not 1 <= assunzioni <= 10:
                return "Le assunzioni giornaliere devono essere tra 1 e 10!"
        except ValueError:
            return "Numero di assunzioni non valido!"
        
        # Validazione date
        if data_inizio:
            try:
                data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d')
                if data_inizio_obj < datetime(1900, 1, 1):
                    return "La data di inizio non può essere precedente al 1900!"
            except ValueError:
                return "Formato data inizio non valido!"
        
        if data_fine and data_fine.strip():
            try:
                data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d')
                data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d')
                if data_fine_obj < data_inizio_obj:
                    return "La data di fine non può essere precedente a quella di inizio!"
            except ValueError:
                return "Formato data fine non valido!"
        
        return None
#Verifica autorizzazione medico
def check_medico_paziente_authorization(medico, paziente):
        """Verifica autorizzazione medico su paziente"""
        if medico not in paziente.doctors:
            return get_error_message(
                f"Accesso negato: Non sei autorizzato a gestire {paziente.name} {paziente.surname}."
            )
        return None

# ===============================
# REGISTRAZIONE CALLBACK PRINCIPALE
# ===============================

def register_doctor_callbacks(app):
    """Registra tutti i callback per i medici"""



    # ===============================
    #  PARSER
    # ===============================
    

    def parse_composite_key(composite_key):
        """Parse della chiave composita per identificare le terapie"""
        parts = composite_key.split('|')
        if len(parts) != 4:
            raise ValueError("Formato chiave terapia non valido!")
        
        medico_nome, paziente_username, nome_farmaco, data_inizio_str = parts
        data_inizio_obj = None if data_inizio_str == 'None' else datetime.strptime(data_inizio_str, '%Y-%m-%d')
        
        return medico_nome, paziente_username, nome_farmaco, data_inizio_obj

    def get_terapia_from_composite_key(composite_key):
        """Trova una terapia dalla chiave composita"""
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
        """Verifica autorizzazione medico su paziente"""
        if medico not in paziente.doctors:
            return get_error_message(
                f"Accesso negato: Non sei autorizzato a gestire {paziente.name} {paziente.surname}."
            )
        return None

    # ===============================
    # CALLBACK NAVIGAZIONE MENU
    # ===============================
    
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
        Input('btn-torna-menu-terapie', 'n_clicks'),
        prevent_initial_call=True
    )
    def torna_menu_terapie(n_clicks):
        return get_terapie_menu() if n_clicks else dash.no_update

    # ===============================
    # CALLBACK FORM TERAPIE
    # ===============================

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
        
        return get_assegna_terapia_form(list(Paziente.select()))

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
        
        return get_modifica_terapia_form(list(Paziente.select()))

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
        
        return get_elimina_terapia_form(list(Paziente.select()))

    # ===============================
    # CALLBACK CRUD TERAPIE
    # ===============================

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-salva-terapia', 'n_clicks'),
        [State('select-paziente-terapia', 'value'),
         State('input-nome-farmaco-terapia', 'value'),
         State('input-dosaggio-terapia', 'value'),
         State('input-assunzioni-giornaliere', 'value'),
         State('select-indicazioni-terapia', 'value'),
         State('input-data-inizio-terapia', 'value'),
         State('input-data-fine-terapia', 'value'),
         State('textarea-note-terapia', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_terapia(n_clicks, paziente_id, nome_farmaco, dosaggio, assunzioni_giornaliere,
                     indicazioni_select, data_inizio, data_fine, note):
        return save_terapia_core(
        n_clicks,
        paziente_id,
        nome_farmaco,
        dosaggio,
        assunzioni_giornaliere,
        indicazioni_select,
        data_inizio,
        data_fine,
        note
    )

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
            return get_assegna_terapia_form(list(Paziente.select()))
        return dash.no_update

    # ===============================
    # CALLBACK LISTE TERAPIE PAZIENTI
    # ===============================

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

    # ===============================
    # CALLBACK MODIFICA TERAPIE
    # ===============================

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
            # Parse del button ID per ottenere la chiave composita
            button_id = ctx.triggered[0]['prop_id']
            json_start = button_id.find('{')
            json_end = button_id.rfind('}') + 1
            button_data = json.loads(button_id[json_start:json_end])
            composite_key = button_data['index']

            terapia, paziente = get_terapia_from_composite_key(composite_key)

            medico = get_current_medico()
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            # Verifica autorizzazioni
            auth_error = check_medico_paziente_authorization(medico, paziente)
            if auth_error:
                return auth_error

            return get_edit_terapia_form(terapia, list(Paziente.select()))

        except (json.JSONDecodeError, ValueError) as e:
            return get_error_message(f"Errore nel parsing: {str(e)}")
        except Exception as e:
            return get_error_message(f"Errore nel caricamento della terapia: {str(e)}")

    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-salva-modifiche-terapia', 'n_clicks'),
        [State('hidden-terapia-key', 'children'),
         State('select-paziente-terapia-edit', 'children'),
         State('input-nome-farmaco-terapia-edit', 'value'),
         State('input-dosaggio-terapia-edit', 'value'),
         State('input-assunzioni-giornaliere-edit', 'value'),
         State('select-indicazioni-terapia-edit', 'value'),
         State('input-data-inizio-terapia-edit', 'value'),
         State('input-data-fine-terapia-edit', 'value'),
         State('textarea-note-terapia-edit', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def save_therapy_modifications(n_clicks, terapia_key, paziente_id, nome_farmaco, dosaggio,
                                  assunzioni_giornaliere, indicazioni_select,
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

            # Verifica autorizzazioni
            auth_error = check_medico_paziente_authorization(medico, paziente_orig)
            if auth_error:
                return auth_error

            paziente_nuovo = Paziente.get(username=paziente_id)
            if not paziente_nuovo:
                return get_error_message("Nuovo paziente non trovato!")

            # Preparazione dati
            indicazioni_finali = get_indicazioni_display(indicazioni_select) if indicazioni_select else ""
            data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d') if data_inizio else None
            data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d') if data_fine and data_fine.strip() else None

            # Se cambiano i dati chiave, ricreare la terapia
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
                    indicazioni=indicazioni_finali,
                    data_inizio=data_inizio_obj,
                    data_fine=data_fine_obj,
                    note=note.strip() if note else '',
                    modificata=f"Dr. {medico.name} {medico.surname}"
                )
            else:
                # Aggiornamento in place
                terapia.dosaggio_per_assunzione = dosaggio.strip()
                terapia.assunzioni_giornaliere = int(assunzioni_giornaliere)
                terapia.indicazioni = indicazioni_finali
                terapia.data_fine = data_fine_obj
                terapia.note = note.strip() if note else ''
                terapia.modificata = f"Dr. {medico.name} {medico.surname}"

            commit()

            return get_terapia_modify_success_message(
                f"{paziente_nuovo.name} {paziente_nuovo.surname}",
                nome_farmaco, dosaggio, int(assunzioni_giornaliere),
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
            return get_modifica_terapia_form(list(Paziente.select()))
        return dash.no_update

    # ===============================
    # CALLBACK ELIMINAZIONE TERAPIE
    # ===============================

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
            # Parse del button ID
            button_id = ctx.triggered[0]['prop_id']
            json_start = button_id.find('{')
            json_end = button_id.rfind('}') + 1
            button_data = json.loads(button_id[json_start:json_end])
            composite_key = button_data['index']

            terapia, paziente = get_terapia_from_composite_key(composite_key)
            medico = get_current_medico()
            
            if not medico:
                return get_error_message("Errore: medico non trovato!")

            # Verifica autorizzazioni
            auth_error = check_medico_paziente_authorization(medico, paziente)
            if auth_error:
                return auth_error

            # Salva info per messaggio successo
            paziente_nome = f"{terapia.paziente.name} {terapia.paziente.surname}"
            farmaco_eliminato = terapia.nome_farmaco
            dosaggio_eliminato = terapia.dosaggio_per_assunzione

            # Elimina terapia
            terapia.delete()
            commit()

            return get_terapia_delete_success_message(paziente_nome, farmaco_eliminato, dosaggio_eliminato)

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
            return get_elimina_terapia_form(list(Paziente.select()))
        return dash.no_update

    # ===============================
    # CALLBACK GESTIONE DATI PAZIENTI
    # ===============================

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

        return get_dati_pazienti_menu(list(Paziente.select()))

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

            # Verifica autorizzazioni
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
            return save_patient_data_modifications_core(
                patient_username,
            fattori_rischio,
            pregresse_patologie,
            comorbidita
        )

        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    # Callback factory per navigation dei dati pazienti
    def create_patient_menu_callback(button_input, callback_name):
        """Factory per callback che tornano al menu dati pazienti"""
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

            return get_dati_pazienti_menu(list(Paziente.select()))
        
        callback_func.__name__ = callback_name
        return callback_func

    # Registrazione callback navigazione dati pazienti
    create_patient_menu_callback('btn-annulla-modifica-dati', 'cancel_patient_data_edit')
    create_patient_menu_callback('btn-altro-paziente', 'show_another_patient_menu')
    create_patient_menu_callback('btn-visualizza-dati-aggiornati', 'show_updated_patient_data')
    create_patient_menu_callback('btn-gestisci-altri-pazienti', 'manage_other_patients')

    # ===============================
    # CALLBACK SEGUIRE PAZIENTI
    # ===============================

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

            # Aggiungi paziente alla lista seguiti
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

            # Verifica se ha già un medico di riferimento
            if paziente.medico_riferimento is not None:
                medico_attuale = paziente.medico_riferimento
                return get_error_message(
                    f"Il paziente {paziente_nome} ha già un medico di riferimento: "
                    f"Dr. {medico_attuale.name} {medico_attuale.surname}."
                )

            # Imposta come medico di riferimento
            paziente.medico_riferimento = medico
            
            # Aggiungi anche alla lista pazienti se non presente
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
            # Parse del button ID
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

            # Rimuovi dalla lista pazienti
            medico.patients.remove(paziente)

            # Se era medico di riferimento, rimuovi anche quello
            if paziente.medico_riferimento == medico:
                paziente.medico_riferimento = None
    
            commit()

            # Torna al form
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

    # ===============================
    # CALLBACK STATISTICHE E GRAFICI
    # ===============================

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
        """Carica le opzioni per il selettore pazienti nelle statistiche"""
        patients = list(Paziente.select())
        options = []
        
        for p in patients:
            cognome = (p.surname or "").strip()
            nome = (p.name or "").strip()
            label = f"{cognome} {nome} ({p.username})".strip()
            label = " ".join(label.split())  # Normalizza spazi
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
        """Genera i grafici settimanali e mensili per il paziente selezionato"""
        
        def empty_fig(msg):
            """Crea un grafico vuoto con messaggio"""
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

        # Carica dati paziente
        paziente = Paziente.get(username=selected_username)
        misurazioni = list(paziente.rilevazione) if paziente else []

        if not misurazioni:
            ef = empty_fig("Nessuna glicemia registrata")
            return ef, ef, ef

        # Crea DataFrame
        df = pd.DataFrame(
            [(m.data_ora, m.valore) for m in misurazioni],
            columns=["data", "valore"]
        ).set_index("data").sort_index()

        # GRAFICO A: Giorni settimana (settimana corrente)
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
            # Mappa numeri giorni settimana a nomi italiani
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

        # GRAFICO B: Media settimanale
        weeks_window = weeks_window or 8
        since = _dt.now() - timedelta(weeks=int(weeks_window))
        recent = df.loc[df.index >= since].copy()
        weekly_mean = recent["valore"].resample("W-MON", label="left", closed="left").mean()
        
        fig_week = go.Figure()
        fig_week.update_yaxes(range=[0, 300], title="mg/dL")

        if not weekly_mean.empty:
            # Crea etichette settimane
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

        # GRAFICO C: Media mensile (anno corrente)
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

        # Applica stile comune
        for fig in (fig_dow, fig_week, fig_month):
            fig.update_layout(
                height=360, margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="white", paper_bgcolor="white", hovermode="x unified"
            )
            fig.update_xaxes(showline=True, linecolor="black", linewidth=1)
            fig.update_yaxes(showline=True, linecolor="black", linewidth=1)

        return fig_dow, fig_week, fig_month

    def add_glucose_reference_lines(fig, x_labels):
        """Aggiunge linee di riferimento per valori glicemici normali"""
        # Linea superiore (glicemia alta)
        fig.add_trace(go.Scatter(
            x=x_labels, y=[180] * len(x_labels),
            mode="lines", name="Glicemia superiore a 180",
            line=dict(color="red", dash="dash"), hoverinfo="skip"
        ))
    
        # Area normale (80-130)
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

    # ===============================
    # CALLBACK SISTEMA NOTIFICHE
    # ===============================

    @db_session
    def build_alerts_for_doctor():
        """Genera lista completa di alert per il medico corrente"""
        medico = get_current_medico()
        if not medico:
            return []

        alerts = []
        today_date = datetime.now().date()
        now_iso = datetime.now().isoformat()
    
        pazienti = list(medico.patients) if hasattr(medico, "patients") else []
    
        for paziente in pazienti:
            patient_label = f"{getattr(paziente, 'name', '')} {getattr(paziente, 'surname', '')}".strip()

            # Alert aderenza terapie
            for terapia in list(paziente.terapies):
                start_date = terapia.data_inizio.date()
                end_date = terapia.data_fine.date() if terapia.data_fine else None
            
                # Salta terapie non ancora iniziate o già finite
                if start_date > today_date:
                    continue
                if end_date is not None and end_date < today_date:
                    continue
            
                # Calcola giorni di controllo mancanza
                if terapia.data_fine:
                    planned_days = (terapia.data_fine.date() - start_date).days + 1
                else:
                    planned_days = None
                    
                base_thresh = planned_days if planned_days in (1, 2) else 3

                # Conta giorni consecutivi senza assunzioni
                missing_streak = 0
                for i in range(base_thresh):
                    day = today_date - timedelta(days=i)
                    if day < start_date:
                        break

                    day_start = datetime.combine(day, datetime.min.time())
                    next_day = day_start + timedelta(days=1)

                    # Verifica se c'è un'assunzione corrispondente in quel giorno
                    has_matching_intake = any(
                        (day_start <= a.data_ora < next_day) and _matches_therapy(a, terapia)
                        for a in getattr(paziente, "assunzione", [])
                    )

                    if has_matching_intake:
                        break
                    missing_streak += 1

                # Se mancano abbastanza giorni, crea alert
                if missing_streak >= base_thresh:
                    giorni_txt = "giorno" if missing_streak == 1 else "giorni"
                    dosaggio = getattr(terapia, "dosaggio_per_assunzione", None)
                    dosaggio_txt = f" (dosaggio: {dosaggio})" if dosaggio else ""

                    start_str = start_date.strftime("%d/%m/%Y")
                    if terapia.data_fine:
                        end_str = terapia.data_fine.strftime("%d/%m/%Y")
                        periodo_label = f"dal {start_str} al {end_str}"
                        is_continuativa = False
                    else:
                        end_str = None
                        periodo_label = f"dal {start_str} (continuativa)"
                        is_continuativa = True
                
                    msg = (f"Il paziente {patient_label} non ha registrato assunzioni di "
                        f"{terapia.nome_farmaco}{dosaggio_txt} negli ultimi {missing_streak} {giorni_txt} consecutivi. "
                        f"Terapia {periodo_label}.")
                       
                    alerts.append({
                        "type": "danger",
                        "patient_id": getattr(paziente, "username", None) or getattr(paziente, "id", None),
                        "patient_name": patient_label or getattr(paziente, "username", ""),
                        "drug_name": terapia.nome_farmaco,
                        "dosaggio_per_assunzione": dosaggio,
                        "streak_days": missing_streak,
                        "timestamp": now_iso,
                        "message": msg,
                        "therapy_start": start_str,
                        "therapy_end": end_str,
                        "therapy_continuativa": is_continuativa
                    })

            # Alert glicemie anomale
            misurazioni = list(paziente.rilevazione) 
            for misura in misurazioni:
                ts = getattr(misura, "data_ora", None)
                val = getattr(misura, "valore", None)

                severity = _is_anomalo_with_severity(val, misura)
                if severity:
                    ctx_txt = _fmt_ctx(misura)
                    val_txt = f"{val:g} mg/dL" if val is not None else "valore non disponibile"
                    ts_txt = ts.strftime("%d/%m/%Y %H:%M") if ts else "data sconosciuta"
                    ctx_phrase = f" ({ctx_txt})" if ctx_txt else ""

                    # Determina etichetta gravità
                    if severity == 'danger':
                        severity_label = "critica"
                    elif severity == 'danger-orange':
                        severity_label = "preoccupante"
                    else:  # warning
                        severity_label = "anomala"

                    msg = (f"Il paziente {patient_label} ha rilevato una glicemia {severity_label} di "
                        f"{val_txt}{ctx_phrase} in data {ts_txt}.")

                    alerts.append({
                        "type": severity,
                        "patient_id": getattr(paziente, "username", None) or getattr(paziente, "id", None),
                        "patient_name": patient_label or getattr(paziente, "username", ""),
                        "value_mgdl": val,
                        "context": ctx_txt,
                        "timestamp": ts.isoformat() if ts else None,
                        "message": msg,
                        "severity_label": severity_label
                    })

        # Ordina per timestamp (più recenti prima)
        def _ts(alert):
            t = alert.get("timestamp")
            try:
                return _dt.fromisoformat(t) if t else _dt.min
            except Exception:
                return _dt.min

        alerts.sort(key=_ts, reverse=True)
        return alerts

    @app.callback(
        Output("alerts-store-medico", "data"),
        Output("bell-button-medico", "color"),
        Input("alerts-poll-medico", "n_intervals"),
        prevent_initial_call=False
    )
    def refresh_doctor_alerts(_):
        """Aggiorna gli alert e il colore della campanella"""
        alerts = build_alerts_for_doctor()

        # Determina colore campanella in base alla priorità degli alert
        if any(a['type'] == 'danger' for a in alerts):
            bell_color = "danger"    # Rosso per terapie non seguite O glicemie critiche
        elif any(a['type'] == 'danger-orange' for a in alerts):
            bell_color = "orange"   # Arancione per glicemie preoccupanti
        elif any(a['type'] == 'warning' for a in alerts):
            bell_color = "warning"   # Giallo per glicemie anomale
        else:
            bell_color = "success"   # Verde se tutto ok
    
        return alerts, bell_color

    @app.callback(
        Output("alerts-modal-body-medico", "children"),
        Input("alerts-store-medico", "data"),
        prevent_initial_call=False
    )
    def render_doctor_alerts(alerts):
        """Renderizza il contenuto del modal degli alert"""
        alerts = alerts or []
        if not alerts:
            return html.Div(
                "Nessuna notifica al momento. Tutti i pazienti seguiti sono in regola!",
                className="text-center p-3"
            )

        items = []
        for alert in alerts:
            alert_type = alert.get("type", "info")

            # Mappa tipo alert a stili Bootstrap
            if alert_type == "danger":  # Terapie non seguite O glicemie critiche (ROSSO)
                border_type = "danger"
                title_class = "text-danger"
                if "drug_name" in alert:  # È un alert terapia
                    title = f"Mancata aderenza terapeutica - {alert.get('patient_name', 'Paziente')}"
                else:  # È un alert glicemia critica
                    title = f"Glicemia critica - {alert.get('patient_name', 'Paziente')}"
            elif alert_type == "danger-orange":  # Glicemie preoccupanti (ARANCIONE)
                border_type = "orange"
                title_class = "text-orange"
                title = f"Glicemia preoccupante - {alert.get('patient_name', 'Paziente')}"
            elif alert_type == "warning":  # Glicemie anomale (GIALLO)
                border_type = "warning"
                title_class = "text-warning"
                title = f"Glicemia anomala - {alert.get('patient_name', 'Paziente')}"
            else:
                border_type = "info"
                title_class = "text-info"
                title = "Notifica"

            items.append(
                dbc.ListGroupItem([
                    html.Div([
                        html.Strong(title, className=title_class)
                    ]),
                    html.Div(alert.get("message", ""), className="mt-1 small")
                ], className=f"border-start border-{border_type} border-3")
            )
        
        return dbc.ListGroup(items, flush=True)

    @app.callback(
        Output("alerts-modal-medico", "is_open"),
        Input("bell-button-medico", "n_clicks"),
        Input("alerts-modal-close-medico", "n_clicks"),
        State("alerts-modal-medico", "is_open"),
        prevent_initial_call=True
    )
    def toggle_doctor_modal(_, __, is_open):
        """Toggle del modal notifiche"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
        
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger in ("bell-button-medico", "alerts-modal-close-medico"):
            return not is_open
        return is_open