# controller/patient.py
"""Controller per la gestione dei pazienti - versione riorganizzata"""

import dash
from dash.dependencies import Input, Output, State
from flask_login import current_user
from dash import html, dcc
from datetime import datetime, timedelta, time as dtime
import time as pytime
from pony.orm import db_session, commit, exists
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from model.glicemia import Glicemia
from model.assunzione import Assunzione
from model.paziente import Paziente
from model.sintomi import Sintomi
from model.terapia import Terapia
from view.patient import *

print("DEBUG: controller/patient.py caricato!")

# COSTANTI CONFIGURAZIONE
CLINICAL_THRESHOLDS = {
    'LOW_NORMAL': 80,
    'HIGH_NORMAL': 130,
    'HIGH_ALERT': 180
}

VALIDATION_LIMITS = {
    'MIN_YEAR': 1900,
    'MIN_NAME_LENGTH': 2,
    'MIN_DESCRIPTION_LENGTH': 2
}

# =============================================================================
# FUNZIONE PRINCIPALE PER REGISTRARE I CALLBACK
# =============================================================================

def register_patient_callbacks(app):
    """Registra tutti i callback per i pazienti"""
    _register_form_callbacks(app)
    _register_data_callbacks(app)
    _register_chart_callbacks(app)
    _register_navigation_callbacks(app)
    _register_alert_callbacks(app)

# =============================================================================
# CALLBACK PER I FORM
# =============================================================================

def _register_form_callbacks(app):
    """Registra i callbacks relativi ai form di inserimento dati"""
    
    # Form glicemia - mostra
    @app.callback(
        Output('patient-content', 'children'),
        Input('btn-registra-glicemia', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_glicemia_form(n_clicks):
        if n_clicks:
            return get_glicemia_form()
        return dash.no_update

    # Form glicemia - campo "due ore dopo pasto"
    @app.callback(
        Output('due-ore-pasto-container', 'style'),
        Input('select-momento-pasto', 'value')
    )
    def toggle_due_ore_pasto(momento_pasto):
        """Mostra il campo 'due ore' solo se selezionato 'dopo pasto'"""
        return {'display': 'block' if momento_pasto == 'dopo_pasto' else 'none'}

    # Form glicemia - salva dati
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Output('alerts-refresh', 'data', allow_duplicate=True),
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
        if not n_clicks:
            return dash.no_update, dash.no_update

        # Validazione input
        error = _validate_glicemia_input(valore, data_misurazione, ora, momento_pasto, due_ore_pasto)
        if error:
            return error, dash.no_update

        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!"), dash.no_update

            # Crea datetime dalla data e ora inserite
            data_obj = datetime.strptime(data_misurazione, '%Y-%m-%d').date()
            ora_obj = datetime.strptime(ora, '%H:%M').time()
            data_ora = datetime.combine(data_obj, ora_obj)
            
            # Campo due ore solo se necessario
            campo_due_ore = due_ore_pasto if momento_pasto == 'dopo_pasto' else None

            # Salva nel database
            Glicemia(
                paziente=paziente,
                valore=float(valore),
                data_ora=data_ora,
                momento_pasto=momento_pasto,
                note=note.strip() if note else '',
                due_ore_pasto=campo_due_ore
            )
            commit()
            
            # Aggiorna gli alert
            refresh_data = {'ts': pytime.time()}
            return get_success_message(valore, data_ora, momento_pasto, due_ore_pasto), refresh_data

        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}"), dash.no_update

    # Form assunzione farmaci - mostra
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-nuova-assunzione', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_assunzione_form(n_clicks):
        if n_clicks:
            return get_nuova_assunzione_form()
        return dash.no_update

    # Form assunzione - dropdown farmaci dalle terapie
    @app.callback(
        Output('dropdown-farmaco-prescritto', 'options'),
        Output('terapie-data-store', 'data'),
        Input('patient-content', 'children'),
        prevent_initial_call=False
    )
    @db_session
    def load_farmaci_options(children):
        """Carica i farmaci dalle terapie attive del paziente"""
        # Controlla se siamo nel form delle assunzioni
        if not _is_assunzione_form_active(children):
            return dash.no_update, dash.no_update

        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return [], {}

            # Ottieni terapie del paziente
            terapie = list(getattr(paziente, 'terapies', []))
            options, terapie_data = get_terapie_options(terapie)
            return options, terapie_data

        except Exception as e:
            print(f"DEBUG: Errore caricamento farmaci: {str(e)}")
            return [{"label": "Errore nel caricamento", "value": "errore"}], {}

    # Form assunzione - gestione campo farmaco personalizzato
    @app.callback(
        Output('nome-farmaco-custom-container', 'style'),
        Output('dosaggio-suggerito-display', 'children'),
        Output('input-dosaggio-farmaco', 'value'),
        Output('input-dosaggio-farmaco', 'disabled'),
        Input('dropdown-farmaco-prescritto', 'value'),
        State('terapie-data-store', 'data'),
        prevent_initial_call=True
    )
    def toggle_custom_farmaco_field(selected_farmaco, terapie_data):
        """Gestisce campo farmaco personalizzato e dosaggio suggerito"""
        if not selected_farmaco:
            return {"display": "none"}, "Seleziona un farmaco", "", False
        
        if selected_farmaco == "altro":
            return {"display": "block"}, "Nessuno", "", False
        
        # Farmaco da terapia prescritta
        if selected_farmaco in terapie_data:
            terapia_info = terapie_data[selected_farmaco]
            dosaggio_suggerito = terapia_info['dosaggio']
            return {"display": "none"}, dosaggio_suggerito, dosaggio_suggerito, True
        
        return {"display": "none"}, "Farmaco selezionato", "", False

    # Form assunzione - salva dati
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Output('alerts-refresh', 'data', allow_duplicate=True),
        Input('btn-salva-assunzione', 'n_clicks'),
        [State('dropdown-farmaco-prescritto', 'value'),
         State('input-nome-farmaco-custom', 'value'),
         State('input-dosaggio-farmaco', 'value'),
         State('input-data-assunzione', 'value'),
         State('input-ora-assunzione', 'value'),
         State('textarea-note-assunzione', 'value'),
         State('terapie-data-store', 'data')],
        prevent_initial_call=True
    )
    @db_session
    def save_assunzione(n_clicks, selected_farmaco, nome_custom, dosaggio, 
                       data_assunzione, ora, note, terapie_data):
        if not n_clicks:
            return dash.no_update, dash.no_update

        # Determina nome farmaco
        nome_farmaco = _get_farmaco_name(selected_farmaco, nome_custom, terapie_data)
        
        # Validazione
        error = _validate_assunzione_input_updated(selected_farmaco, nome_farmaco, dosaggio, data_assunzione, ora)
        if error:
            return error, dash.no_update

        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!"), dash.no_update

            # Crea datetime
            data_obj = datetime.strptime(data_assunzione, '%Y-%m-%d').date()
            ora_obj = datetime.strptime(ora, '%H:%M').time()
            data_ora = datetime.combine(data_obj, ora_obj)

            # Salva nel database
            Assunzione(
                paziente=paziente,
                nome_farmaco=nome_farmaco.strip(),
                dosaggio=dosaggio.strip(),
                data_ora=data_ora,
                note=note.strip() if note else ''
            )
            commit()
            
            refresh_data = {'ts': pytime.time()}
            return get_assunzione_success_message(nome_farmaco, dosaggio, data_ora), refresh_data

        except Exception as e:
            print(f"DEBUG: Errore salvataggio assunzione: {str(e)}")
            return get_error_message(f"Errore durante il salvataggio: {str(e)}"), dash.no_update

    # Form sintomi - mostra
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-sintomi-terapie', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_sintomi_form(n_clicks):
        if n_clicks:
            return get_sintomi_cure_form()
        return dash.no_update

    # Form sintomi - campo frequenza
    @app.callback(
        Output('campi-sintomi-container', 'style'),
        Input('select-tipo-sintomo', 'value')
    )
    def toggle_campi_sintomi(tipo_sintomo):
        """Mostra campo frequenza solo per i sintomi"""
        return {'display': 'block' if tipo_sintomo == 'sintomo' else 'none'}

    # Form sintomi - salva dati
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
        if not n_clicks:
            return dash.no_update

        # Validazione
        error = _validate_sintomi_input(tipo, descrizione, data_inizio, data_fine, frequenza)
        if error:
            return error

        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")

            # Conversione date
            data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d').date()
            data_fine_obj = None
            if data_fine and data_fine.strip():
                data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d').date()

            # Salva nel database
            Sintomi(
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

    # Pulsanti "Nuova registrazione" e "Annulla"
    _register_form_actions(app)

# =============================================================================
# CALLBACK PER LA VISUALIZZAZIONE DATI
# =============================================================================

def _register_data_callbacks(app):
    """Registra i callbacks per visualizzare i dati del paziente"""

    # Visualizza dati personali
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-miei-dati', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_miei_dati(n_clicks):
        if n_clicks:
            return get_miei_dati_view()
        return dash.no_update

    @app.callback(
        Output('miei-dati-content', 'children'),
        Input('patient-content', 'children'),
        prevent_initial_call=False
    )
    @db_session
    def load_patient_personal_data(children):
        if not _is_data_view_active(children, 'miei-dati-content'):
            return dash.no_update

        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            return get_patient_personal_data_display(paziente)
        except Exception as e:
            return get_error_message(f"Errore durante il caricamento dei dati: {str(e)}")

    # Visualizza terapie
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-terapie', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_mie_terapie(n_clicks):
        if n_clicks:
            return get_mie_terapie_view()
        return dash.no_update

    @app.callback(
        Output('mie-terapie-content', 'children'),
        Input('patient-content', 'children'),
        prevent_initial_call=False
    )
    @db_session
    def load_patient_therapies(children):
        if not _is_data_view_active(children, 'mie-terapie-content'):
            return dash.no_update

        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")

            # Ottieni terapie ordinate per data più recente
            terapie = list(getattr(paziente, 'terapies', []))
            terapie = sorted(terapie, key=lambda t: t.data_inizio or datetime.min, reverse=True)
            return get_patient_therapies_display(terapie)
        except Exception as e:
            return get_error_message(f"Errore durante il caricamento delle terapie: {str(e)}")

    # Visualizza contatti medico
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-messaggi', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_contact_doctor(n_clicks):
        if n_clicks:
            return get_contact_doctor_view()
        return dash.no_update

    @app.callback(
        Output('doctor-contact-info', 'children'),
        Input('patient-content', 'children'),
        prevent_initial_call=False
    )
    @db_session
    def load_doctor_contact_info(children):
        if not _is_data_view_active(children, 'doctor-contact-info'):
            return dash.no_update

        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            return get_doctor_contact_display(paziente.medico_riferimento)
        except Exception as e:
            return get_error_message(f"Errore durante il caricamento delle informazioni del medico: {str(e)}")

# =============================================================================
# CALLBACK PER I GRAFICI
# =============================================================================

def _register_chart_callbacks(app):
    """Registra i callbacks per i grafici dell'andamento glicemico"""

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-andamento-glicemico', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_andamento_glicemico(n_clicks):
        if n_clicks:
            return get_andamento_glicemico_view()
        return dash.no_update

    @app.callback(
        Output("patient-week-dow", "figure"),
        Output("patient-weekly-avg", "figure"),
        Output("patient-monthly-avg", "figure"),
        Input("patient-content", "children"),
        Input("weeks-window", "value"),
        prevent_initial_call=False
    )
    @db_session
    def render_charts(_children, weeks_window):
        """Genera i tre grafici: giorni settimana, settimanale, mensile"""
        paziente = Paziente.get(username=current_user.username)
        if not paziente:
            return _create_empty_figures("Paziente non trovato")

        # Recupera misurazioni glicemiche
        glicemie = _get_patient_glicemie(paziente)
        if not glicemie:
            return _create_empty_figures("Nessuna glicemia registrata")

        # Crea DataFrame
        df = _create_glicemia_dataframe(glicemie)

        # Genera i tre grafici
        fig_dow = _create_weekly_dow_chart(df)
        fig_week = _create_weekly_avg_chart(df, weeks_window or 8)
        fig_month = _create_monthly_avg_chart(df)

        return fig_dow, fig_week, fig_month

# =============================================================================
# CALLBACK PER LA NAVIGAZIONE
# =============================================================================

def _register_navigation_callbacks(app):
    """Registra i callbacks per tornare al menu principale"""
    
    menu_buttons = [
        'btn-torna-menu-paziente', 'btn-torna-menu-grafici', 
        'btn-torna-menu-terapie-paziente', 'btn-torna-menu-miei-dati', 
        'btn-torna-menu-messaggi'
    ]
    
    for btn_id in menu_buttons:
        @app.callback(
            Output('patient-content', 'children', allow_duplicate=True),
            Input(btn_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def back_to_menu(n_clicks):
            if n_clicks:
                return get_patient_welcome_content()
            return dash.no_update

def _register_form_actions(app):
    """Registra pulsanti per nuove registrazioni e annullamento"""
    
    # Pulsanti "Nuova registrazione"
    new_form_buttons = [
        ('btn-nuova-misurazione', get_glicemia_form),
        ('btn-nuova-assunzione-bis', get_nuova_assunzione_form),
        ('btn-nuovo-sintomo', get_sintomi_cure_form)
    ]
    
    for btn_id, form_func in new_form_buttons:
        @app.callback(
            Output('patient-content', 'children', allow_duplicate=True),
            Input(btn_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def show_new_form(n_clicks, form=form_func):
            if n_clicks:
                return form()
            return dash.no_update

    # Pulsanti "Annulla"
    cancel_buttons = ['btn-annulla-glicemia', 'btn-annulla-assunzione', 'btn-annulla-sintomo']
    
    for btn_id in cancel_buttons:
        @app.callback(
            Output('patient-content', 'children', allow_duplicate=True),
            Input(btn_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def cancel_form(n_clicks):
            if n_clicks:
                return get_patient_welcome_content()
            return dash.no_update

# =============================================================================
# CALLBACK PER GLI ALERT
# =============================================================================

def _register_alert_callbacks(app):
    """Gestisce gli alert per promemoria farmaci e glicemia"""

    # Banner promemoria farmaci
    @app.callback(
        Output('meds-alert-container', 'children'),
        [Input('patient-content', 'children'),
         Input('alerts-refresh', 'data')],
        prevent_initial_call=False
    )
    @db_session
    def render_meds_alert_banner(_, refresh_data):
        """Mostra il banner promemoria per assunzioni"""
        return get_medication_alert()

    # Modal alert - gestione apertura/chiusura e contenuto
    @app.callback(
        Output('alerts-modal', 'is_open'),
        Output('alerts-modal-body', 'children'),
        Output('bell-button', 'color'),
        Input('bell-button', 'n_clicks'),
        Input('alerts-modal-close', 'n_clicks'),
        Input('patient-content', 'children'),
        Input('alerts-refresh', 'data'),
        State('alerts-modal', 'is_open'),
        prevent_initial_call=False
    )
    @db_session
    def toggle_alerts_modal(n_bell, n_close, content_update, refresh_data, is_open):
        """Gestisce modal alert e aggiorna colore campanella"""
        ctx = dash.callback_context

        # Prepara contenuto alert
        items, bell_color = _prepare_alert_content()
        
        body_children = (dbc.ListGroup(items, flush=True) if items 
                        else html.Div("Nessun promemoria al momento. Ottimo lavoro! 🎉", 
                                    className="text-center p-3"))

        # Prima apertura - solo aggiorna colore
        if not ctx.triggered:
            return False, body_children, bell_color

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'bell-button':
            return (not is_open), body_children, bell_color
        elif trigger_id == 'alerts-modal-close':
            return False, body_children, bell_color
        else:  # aggiornamento contenuto
            return is_open, body_children, bell_color

# =============================================================================
# FUNZIONI HELPER - VALIDAZIONE
# =============================================================================

def _validate_glicemia_input(valore, data_misurazione, ora, momento_pasto, due_ore_pasto):
    """Valida i dati del form glicemia"""
    if not all([valore, data_misurazione, ora, momento_pasto]):
        return get_error_message("Per favore compila tutti i campi obbligatori!")

    # Validazione data
    error = _validate_date(data_misurazione, "misurazione")
    if error:
        return error

    # Validazione campo "due ore dopo pasto"
    if momento_pasto == 'dopo_pasto' and due_ore_pasto is None:
        return get_error_message("Per favore specifica se sono passate almeno due ore dal pasto!")

    return None

def _validate_assunzione_input_updated(selected_farmaco, nome_farmaco, dosaggio, data_assunzione, ora):
    """Valida i dati del form assunzione"""
    if not selected_farmaco:
        return get_error_message("Per favore seleziona un farmaco dal menu a tendina!")
    
    if selected_farmaco == "altro" and (not nome_farmaco or len(nome_farmaco.strip()) < VALIDATION_LIMITS['MIN_NAME_LENGTH']):
        return get_error_message("Per 'Altro farmaco': inserisci un nome di almeno 2 caratteri!")
    
    if not nome_farmaco:
        return get_error_message("Errore: nome farmaco non valido!")

    if not dosaggio or len(dosaggio.strip()) < 1:
        return get_error_message("Il dosaggio non può essere vuoto!")

    if not all([data_assunzione, ora]):
        return get_error_message("Per favore compila data e ora di assunzione!")

    # Validazione data
    error = _validate_date(data_assunzione, "assunzione")
    if error:
        return error

    # Validazione ora
    try:
        datetime.strptime(ora, '%H:%M').time()
    except ValueError:
        return get_error_message("Formato ora non valido!")

    return None

def _validate_sintomi_input(tipo, descrizione, data_inizio, data_fine, frequenza):
    """Valida i dati del form sintomi"""
    if not all([tipo, descrizione, data_inizio]):
        return get_error_message("Per favore compila tutti i campi obbligatori!")

    if tipo == 'sintomo' and not frequenza:
        return get_error_message("Per favore seleziona la frequenza del sintomo!")

    if len(descrizione.strip()) < VALIDATION_LIMITS['MIN_DESCRIPTION_LENGTH']:
        return get_error_message("La descrizione deve essere di almeno 2 caratteri!")

    # Validazione data inizio
    error = _validate_date(data_inizio, "inizio")
    if error:
        return error

    # Validazione data fine se presente
    if data_fine and data_fine.strip():
        error = _validate_date(data_fine, "fine")
        if error:
            return error
        
        # Controlla che data fine sia dopo data inizio
        try:
            data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d').date()
            data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d').date()
            
            if data_fine_obj < data_inizio_obj:
                return get_error_message("La data di fine non può essere precedente alla data di inizio!")
        except ValueError:
            return get_error_message("Formato data non valido!")

    return None

def _validate_date(date_string, field_name):
    """Valida una data in formato string"""
    try:
        data_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
        today = datetime.now().date()
        min_date = datetime(VALIDATION_LIMITS['MIN_YEAR'], 1, 1).date()

        if data_obj > today:
            return get_error_message(f"La data di {field_name} non può essere nel futuro!")
        if data_obj < min_date:
            return get_error_message(f"La data di {field_name} non può essere precedente al {VALIDATION_LIMITS['MIN_YEAR']}!")
            
    except ValueError:
        return get_error_message("Formato data non valido!")
    
    return None

# =============================================================================
# FUNZIONI HELPER - UTILITÀ GENERALI
# =============================================================================

def _get_farmaco_name(selected_farmaco, nome_custom, terapie_data):
    """Determina il nome del farmaco dalla selezione"""
    if selected_farmaco == "altro":
        return nome_custom
    elif selected_farmaco and selected_farmaco in terapie_data:
        return terapie_data[selected_farmaco]['nome']
    return None

def _is_assunzione_form_active(children):
    """Verifica se il form assunzioni è attivo"""
    try:
        return 'dropdown-farmaco-prescritto' in str(children)
    except Exception:
        return False

def _is_data_view_active(children, element_id):
    """Verifica se una vista dati specifica è attiva"""
    if not children or not isinstance(children, dict):
        return False
    try:
        return element_id in str(children)
    except Exception:
        return False

def _get_patient_glicemie(paziente):
    """Recupera le glicemie del paziente (tollera nomi diversi di relazioni)"""
    return _rel_list(paziente, 'glicemias', 'glicemie', 'rilevazione', 'rilevazioni')

def _rel_list(paziente, *names):
    """Restituisce list(relazione) provando più nomi possibili"""
    for name in names:
        if hasattr(paziente, name):
            try:
                return list(getattr(paziente, name))
            except Exception:
                pass
    return []

def _create_glicemia_dataframe(glicemie):
    """Crea DataFrame dalle glicemie"""
    df = pd.DataFrame([{"data": g.data_ora, "valore": g.valore} for g in glicemie])
    df = df.sort_values("data")
    df["data"] = pd.to_datetime(df["data"])
    df.set_index("data", inplace=True)
    return df

def _day_bounds(date):
    """Restituisce inizio e fine giornata per una data"""
    start = datetime.combine(date, dtime.min)
    end = start + timedelta(days=1)
    return start, end

def _prepare_alert_content():
    """Prepara contenuto degli alert e determina colore campanella"""
    items = []
    bell_color = "success"  # Default verde

    try:
        if current_user.is_authenticated:
            paziente = Paziente.get(username=current_user.username)
        else:
            paziente = None

        if paziente:
            alerts = _check_patient_alerts(paziente)

            # Determina colore campanella basato su priorità alert
            if any(a['type'] == 'danger' for a in alerts):
                bell_color = "danger"
            elif any(a['type'] == 'warning' for a in alerts):
                bell_color = "warning"
            elif alerts:
                bell_color = "info"

            # Crea elementi per il modal
            color_map = {
                'danger': 'text-danger',
                'warning': 'text-warning', 
                'info': 'text-info'
            }

            for alert in alerts:
                items.append(
                    dbc.ListGroupItem([
                        html.Div([
                            html.Strong(alert['title'], 
                                      className=color_map.get(alert['type'], ''))
                        ]),
                        html.Div(alert['message'], className="mt-1 small")
                    ], className=f"border-start border-{alert['type']} border-3")
                )

    except Exception as e:
        items.append(dbc.ListGroupItem(f"Errore nel recupero alert: {str(e)}"))

    return items, bell_color

# =============================================================================
# FUNZIONI HELPER - GESTIONE ALERT
# =============================================================================

def _check_patient_alerts(paziente):
    """Verifica tutti gli alert per il paziente"""
    alerts = []
    today = datetime.now().date()

    # Alert specifici per terapie attive
    therapy_alerts = _check_therapy_alerts(paziente)
    alerts.extend(therapy_alerts)

    # Alert generico solo se non ci sono terapie attive
    if not therapy_alerts:
        # Verifica assunzioni oggi
        has_assunzioni_today = _has_assunzioni_today(paziente, today)
        has_active_therapies = _has_active_therapies(paziente, today)

        if not has_assunzioni_today and not has_active_therapies:
            alerts.append({
                'type': 'info',
                'title': 'Promemoria assunzioni giornaliere',
                'message': 'Ricorda di registrare eventuali farmaci assunti oggi.',
                'icon': 'bell'
            })

    # Alert per glicemia
    if not _has_glicemia_today(paziente, today):
        alerts.append({
            'type': 'warning',
            'title': 'Promemoria misurazione glicemia',
            'message': 'Non hai ancora registrato misurazioni di glicemia oggi.',
            'icon': 'tint'
        })

    return alerts

def _check_therapy_alerts(paziente):
    """Verifica alert specifici per ogni terapia attiva"""
    alerts = []
    today = datetime.now().date()

    # Ottieni assunzioni di oggi
    assunzioni_oggi = _get_assunzioni_today(paziente, today)
    
    # Raggruppa assunzioni per farmaco
    assunzioni_per_farmaco = {}
    for ass in assunzioni_oggi:
        nome = ass.nome_farmaco.lower().strip()
        assunzioni_per_farmaco[nome] = assunzioni_per_farmaco.get(nome, 0) + 1

    # Controlla terapie attive
    terapie_attive = _get_active_therapies(paziente, today)

    for terapia in terapie_attive:
        nome_farmaco = terapia.nome_farmaco.lower().strip()
        assunzioni_richieste = terapia.assunzioni_giornaliere
        assunzioni_fatte = assunzioni_per_farmaco.get(nome_farmaco, 0)
        
        if assunzioni_fatte < assunzioni_richieste:
            mancanti = assunzioni_richieste - assunzioni_fatte
            
            # Costruisci messaggio alert
            if mancanti == assunzioni_richieste:
                message = f"Oggi devi prendere {terapia.dosaggio_per_assunzione} di {terapia.nome_farmaco}"
                if assunzioni_richieste > 1:
                    message += f" per {assunzioni_richieste} volte al giorno"
                else:
                    message += " (1 volta al giorno)"
            else:
                message = f"Ti mancano ancora {mancanti} somministrazioni di {terapia.nome_farmaco} oggi"
                if assunzioni_richieste > 1:
                    message += f" (hai fatto {assunzioni_fatte}/{assunzioni_richieste} assunzioni)"
            
            alerts.append({
                'type': 'danger',
                'title': f'Promemoria: {terapia.nome_farmaco}',
                'message': message,
                'icon': 'pills',
                'farmaco': terapia.nome_farmaco,
                'mancanti': mancanti,
                'totali': assunzioni_richieste
            })

    return alerts

def _get_assunzioni_today(paziente, today):
    """Recupera assunzioni di oggi"""
    start, end = _day_bounds(today)
    try:
        return [a for a in paziente.assunzione if start <= a.data_ora < end]
    except Exception:
        return []

def _get_active_therapies(paziente, today):
    """Recupera terapie attive per oggi"""
    try:
        return [t for t in paziente.terapies
                if (t.data_inizio is None or t.data_inizio.date() <= today) and 
                   (t.data_fine is None or t.data_fine.date() >= today)]
    except Exception:
        return []

def _has_assunzioni_today(paziente, today):
    """Verifica se ha assunzioni registrate oggi"""
    return len(_get_assunzioni_today(paziente, today)) > 0

def _has_active_therapies(paziente, today):
    """Verifica se ha terapie attive"""
    return len(_get_active_therapies(paziente, today)) > 0

def _has_glicemia_today(paziente, today):
    """Verifica se ha glicemie registrate oggi"""
    start, end = _day_bounds(today)
    try:
        glicemie_oggi = [g for g in paziente.rilevazione if start <= g.data_ora < end]
        return len(glicemie_oggi) > 0
    except Exception:
        return False

# =============================================================================
# FUNZIONI HELPER - CREAZIONE GRAFICI
# =============================================================================

def _create_empty_figures(message="Nessuna glicemia registrata"):
    """Crea tre figure vuote con messaggio"""
    def empty_fig():
        fig = go.Figure()
        fig.update_yaxes(range=[0, 300])
        fig.add_annotation(text=message, xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
        return fig

    return empty_fig(), empty_fig(), empty_fig()

def _create_weekly_dow_chart(df):
    """Crea grafico giorni della settimana (settimana corrente)"""
    today = datetime.now()
    start_week = (today - timedelta(days=today.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_week = start_week + timedelta(days=7)

    # Filtra dati settimana corrente
    week_df = df.loc[(df.index >= start_week) & (df.index < end_week)].copy()

    fig = go.Figure()
    fig.update_yaxes(range=[0, 300], title="mg/dL")

    dow_order = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    fig.update_xaxes(categoryorder="array", categoryarray=dow_order, title="Giorno della settimana")

    if not week_df.empty:
        week_df["giorno_label"] = week_df.index.dayofweek.map({
            i: dow_order[i] for i in range(7)
        })

        # Media per giorno
        daily_mean = week_df.groupby("giorno_label")["valore"].mean().reindex(dow_order)
        fig.add_trace(go.Scatter(
            x=dow_order, y=daily_mean.values,
            mode="lines+markers", name="Media giorno",
            line=dict(color="#F58518", width=2), connectgaps=True
        ))

        # Aggiungi soglie cliniche
        _add_clinical_thresholds(fig, dow_order)

    _apply_chart_styling(fig)
    return fig

def _create_weekly_avg_chart(df, weeks_window):
    """Crea grafico media settimanale"""
    since = datetime.now() - timedelta(weeks=int(weeks_window))
    recent = df.loc[df.index >= since].copy()

    # Media settimanale (lunedì come inizio settimana)
    weekly_mean = recent["valore"].resample("W-MON", label="left", closed="left").mean()

    fig = go.Figure()
    fig.update_yaxes(range=[0, 300], title="mg/dL")

    if not weekly_mean.empty:
        # Crea etichette asse X
        x_labels = []
        for ts in weekly_mean.index:
            start = ts
            end = ts + timedelta(days=6)
            x_labels.append(f"{start.strftime('%d/%m')}–{end.strftime('%d/%m')}")

        fig.add_trace(go.Scatter(
            x=x_labels, y=weekly_mean.values,
            mode="lines+markers",
            name=f"Media settimanale (ultime {weeks_window} sett.)",
            line=dict(color="#4C78A8", width=2), connectgaps=True
        ))

        _add_clinical_thresholds(fig, x_labels)
    else:
        fig.add_annotation(text="Nessuna settimana con dati nel periodo",
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)

    _apply_chart_styling(fig)
    return fig

def _create_monthly_avg_chart(df):
    """Crea grafico media mensile (anno corrente)"""
    year = datetime.now().year
    year_start = pd.Timestamp(year=year, month=1, day=1)

    # Indice fisso 12 mesi
    idx_months = pd.date_range(start=year_start, periods=12, freq="MS")

    # Filtra anno corrente e calcola media mensile
    df_year = df.loc[(df.index >= year_start) &
                     (df.index < year_start + pd.offsets.YearEnd(0) + pd.Timedelta(days=1))].copy()
    monthly_mean = df_year["valore"].resample("MS").mean().reindex(idx_months)

    mesi_it = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
               "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
    x_m = [mesi_it[ts.month - 1] for ts in monthly_mean.index]

    fig = go.Figure()
    fig.update_yaxes(range=[0, 300], title="mg/dL")
    
    fig.add_trace(go.Scatter(
        x=x_m, y=monthly_mean.values,
        mode="lines+markers", name=f"Media mensile {year}",
        line=dict(color="#4C78A8", width=2), connectgaps=True
    ))

    if monthly_mean.isna().all():
        fig.add_annotation(text="Nessun dato per l'anno selezionato",
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)

    _add_clinical_thresholds(fig, x_m)
    _apply_chart_styling(fig)
    return fig

def _add_clinical_thresholds(fig, x_labels):
    """Aggiunge soglie cliniche al grafico"""
    # Soglia alta 180 mg/dL
    fig.add_trace(go.Scatter(
        x=x_labels, y=[CLINICAL_THRESHOLDS['HIGH_ALERT']] * len(x_labels),
        mode="lines", name="Glicemia superiore a 180",
        line=dict(color="red", dash="dash"), hoverinfo="skip"
    ))

    # Fascia normale 80-130 mg/dL
    y_low = [CLINICAL_THRESHOLDS['LOW_NORMAL']] * len(x_labels)
    y_high = [CLINICAL_THRESHOLDS['HIGH_NORMAL']] * len(x_labels)

    fig.add_trace(go.Scatter(
        x=x_labels, y=y_low, mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip", legendgroup="norma"
    ))

    fig.add_trace(go.Scatter(
        x=x_labels, y=y_high, mode="lines",
        line=dict(width=0), fill="tonexty",
        fillcolor="rgba(144,238,144,0.20)",
        name="Glicemia nella norma (80–130)", hoverinfo="skip", legendgroup="norma"
    ))

def _apply_chart_styling(fig):
    """Applica stile comune ai grafici"""
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=360, margin=dict(l=10, r=10, t=30, b=10)
    )
    fig.update_xaxes(showline=True, linecolor="black", linewidth=1)
    fig.update_yaxes(showline=True, linecolor="black", linewidth=1)