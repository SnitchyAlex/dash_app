# controller/patient.py
"""Controller per la gestione dei pazienti"""
import dash
from dash.dependencies import Input, Output, State
from flask_login import current_user
from dash import html, dcc
from datetime import datetime, timedelta
from datetime import time as dtime
import time as pytime
from pony.orm import db_session, commit,exists
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from model.glicemia import Glicemia
from model.assunzione import Assunzione
from model.paziente import Paziente
from model.sintomi import Sintomi
from model.terapia import Terapia

from view.patient import *
#print iniziale di debug
print("DEBUG: controller/patient.py caricato!")
# callback principale

def register_patient_callbacks(app):
    """Registra tutti i callback per i pazienti"""
    _register_form_callbacks(app)
    _register_data_callbacks(app)
    _register_chart_callbacks(app)
    _register_navigation_callbacks(app)
    _register_alert_callbacks(app)


def _register_form_callbacks(app):
    """Registra i callbacks relativi ai form"""
    
    @app.callback(
        Output('patient-content', 'children'),
        Input('btn-registra-glicemia', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_glicemia_form(n_clicks):
        if n_clicks:
            return get_glicemia_form()
        return dash.no_update
    
    @app.callback(
        Output('due-ore-pasto-container', 'style'),
        Input('select-momento-pasto', 'value')
    )
    def toggle_due_ore_pasto(momento_pasto):
        """Mostra/nasconde il campo due ore in base al momento del pasto"""
        return {'display': 'block' if momento_pasto == 'dopo_pasto' else 'none'}

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
            return dash.no_update,dash.no_update
        
        # Validazione input
        validation_error = _validate_glicemia_input(valore, data_misurazione, ora, momento_pasto, due_ore_pasto)
        if validation_error:
            return validation_error,dash.no_update
        
        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!"),dash.no_update
            
            # Creazione oggetto datetime
            data_inserita = datetime.strptime(data_misurazione, '%Y-%m-%d').date()
            data_ora = datetime.combine(data_inserita, datetime.strptime(ora, '%H:%M').time())
            campo_due_ore = due_ore_pasto if momento_pasto == 'dopo_pasto' else None
            
            # Salvataggio
            misurazione = Glicemia(
                paziente=paziente,
                valore=float(valore),
                data_ora=data_ora,
                momento_pasto=momento_pasto,
                note=note if note else '',
                due_ore_pasto=campo_due_ore
            )
            commit()
            refresh_data2 = {'ts': pytime.time()}
            print(f"DEBUG: Restituendo refresh_data = {refresh_data2}")
            
            return get_success_message(valore, data_ora, momento_pasto, due_ore_pasto),refresh_data2
            
        except Exception as e:
            return get_error_message(f"Errore durante il salvataggio: {str(e)}"),dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-nuova-assunzione', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_assunzione_form(n_clicks):
        if n_clicks:
            return get_nuova_assunzione_form()
        return dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Output('alerts-refresh', 'data', allow_duplicate=True),
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
        if not n_clicks:
            return dash.no_update,dash.no_update
        
        # Validazione input
        validation_error = _validate_assunzione_input(nome_farmaco, dosaggio, data_assunzione, ora)
        if validation_error:
            return validation_error,dash.no_update
        
        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!"),dash.no_update
            
            # Creazione datetime
            data_inserita = datetime.strptime(data_assunzione, '%Y-%m-%d').date()
            ora_obj = datetime.strptime(ora, '%H:%M').time()
            data_ora = datetime.combine(data_inserita, ora_obj)
            
            # Salvataggio
            assunzione = Assunzione(
                paziente=paziente,
                nome_farmaco=nome_farmaco.strip(),
                dosaggio=dosaggio.strip(),
                data_ora=data_ora,
                note=note.strip() if note else ''
            )
            commit()
            #debug
            refresh_data = {'ts': pytime.time()}
            print(f"DEBUG: Restituendo refresh_data = {refresh_data}")
            
            return get_assunzione_success_message(nome_farmaco, dosaggio, data_ora),refresh_data
            
        except Exception as e:
            print(f"DEBUG: Errore nel salvataggio: {str(e)}")
            return get_error_message(f"Errore durante il salvataggio: {str(e)}"),dash.no_update

    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-sintomi-trattamenti', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_sintomi_form(n_clicks):
        if n_clicks:
            return get_sintomi_trattamenti_form()
        return dash.no_update

    @app.callback(
        Output('campi-sintomi-container', 'style'),
        Input('select-tipo-sintomo', 'value')
    )
    def toggle_campi_sintomi(tipo_sintomo):
        """Mostra/nasconde i campi frequenza per i sintomi"""
        return {'display': 'block' if tipo_sintomo == 'sintomo' else 'none'}

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
        
        # Validazione input
        validation_error = _validate_sintomi_input(tipo, descrizione, data_inizio, data_fine, frequenza)
        if validation_error:
            return validation_error
        
        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            # Conversione date
            data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d').date()
            data_fine_obj = None
            if data_fine and data_fine.strip():
                data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d').date()
            
            # Salvataggio
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
        
    _register_form_actions(app)


def _register_form_actions(app):
    """Registra i callbacks per azioni sui form (annulla, nuova registrazione)"""
    
    # Callbacks per pulsanti "Nuova registrazione"
    for btn_id, form_func in [
        ('btn-nuova-misurazione', get_glicemia_form),
        ('btn-nuova-assunzione-bis', get_nuova_assunzione_form),
        ('btn-nuovo-sintomo', get_sintomi_trattamenti_form)
    ]:
        @app.callback(
            Output('patient-content', 'children', allow_duplicate=True),
            Input(btn_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def show_new_form(n_clicks, form=form_func):
            if n_clicks:
                return form()
            return dash.no_update
    
    # Callbacks per pulsanti "Annulla"
    for btn_id in ['btn-annulla-glicemia', 'btn-annulla-assunzione', 'btn-annulla-sintomo']:
        @app.callback(
            Output('patient-content', 'children', allow_duplicate=True),
            Input(btn_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def cancel_form(n_clicks):
            if n_clicks:
                 return get_patient_welcome_content()  # o come hai chiamato la funzione
            return dash.no_update


# visualizzazione

def _register_data_callbacks(app):
    """Registra i callbacks per visualizzazione dati"""
    
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
        if not children or not isinstance(children, dict):
            return dash.no_update
        
        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            return get_patient_personal_data_display(paziente)
        except Exception as e:
            return get_error_message(f"Errore durante il caricamento dei dati: {str(e)}")

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
        if not children:
            return dash.no_update
        
        try:
            children_str = str(children)
            if 'mie-terapie-content' not in children_str:
                return dash.no_update
        except:
            return dash.no_update
        
        try:
            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            terapie = list(paziente.terapies.order_by(Terapia.data_inizio.desc()))
            return get_patient_therapies_display(terapie)
        except Exception as e:
            return get_error_message(f"Errore durante il caricamento delle terapie: {str(e)}")


# grafici

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
    def render_week_month_charts(_children, weeks_window):
        """Genera i 3 grafici: giorni settimana, settimanale, mensile"""
        
        paziente = Paziente.get(username=current_user.username)
        if not paziente:
            return _create_empty_figures()
        
        # Recupera misurazioni
        all_meas = list(paziente.rilevazione)
        if not all_meas:
            return _create_empty_figures("Nessuna glicemia registrata")
        
        # Crea DataFrame base
        df = pd.DataFrame([{"data": g.data_ora, "valore": g.valore} for g in all_meas])
        df = df.sort_values("data")
        df["data"] = pd.to_datetime(df["data"])
        df.set_index("data", inplace=True)
        
        # Genera i tre grafici
        fig_dow = _create_weekly_dow_chart(df)
        fig_week = _create_weekly_avg_chart(df, weeks_window or 8)
        fig_month = _create_monthly_avg_chart(df)
        
        return fig_dow, fig_week, fig_month


def _create_weekly_dow_chart(df):
    """Crea grafico giorni della settimana (settimana corrente)"""
    today = datetime.now()
    start_week = (today - timedelta(days=today.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_week = start_week + timedelta(days=7)
    
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
        
        # Soglie cliniche
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
        # Etichette asse X
        x_labels = []
        for ts in weekly_mean.index:
            start = ts
            end = ts + timedelta(days=6)
            x_labels.append(f"{start.strftime('%d/%m')}—{end.strftime('%d/%m')}")
        
        fig.add_trace(go.Scatter(
            x=x_labels, y=weekly_mean.values,
            mode="lines+markers",
            name=f"Media settimanale (ultime {weeks_window} sett.)",
            line=dict(color="#4C78A8", width=2), connectgaps=True
        ))
        
        # Soglie cliniche
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
    
    # Soglie cliniche
    _add_clinical_thresholds(fig, x_m)
    _apply_chart_styling(fig)
    return fig

def _register_navigation_callbacks(app):
    """Registra i callbacks per la navigazione"""
    
    # Pulsanti "Torna al Menu"
    for btn_id in ['btn-torna-menu-paziente', 'btn-torna-menu-grafici', 'btn-torna-menu-terapie-paziente']:
        @app.callback(
            Output('patient-content', 'children', allow_duplicate=True),
            Input(btn_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def back_to_patient_menu(n_clicks):
            if n_clicks:
                 return get_patient_welcome_content()
            return dash.no_update


def _validate_glicemia_input(valore, data_misurazione, ora, momento_pasto, due_ore_pasto):
    """Valida input form glicemia"""
    if not valore or not data_misurazione or not ora or not momento_pasto:
        return get_error_message("Per favore compila tutti i campi obbligatori!")
    
    # Validazione data
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
    
    # Validazione campo due ore dopo pasto
    if momento_pasto == 'dopo_pasto' and due_ore_pasto is None:
        return get_error_message("Per favore specifica se sono passate almeno due ore dal pasto!")
    
    return None


def _validate_assunzione_input(nome_farmaco, dosaggio, data_assunzione, ora):
    """Valida input form assunzione"""
    if not nome_farmaco or not dosaggio or not data_assunzione or not ora:
        return get_error_message("Per favore compila tutti i campi obbligatori!")
    
    if len(nome_farmaco.strip()) < 2:
        return get_error_message("Il nome del farmaco deve essere di almeno 2 caratteri!")
    
    if len(dosaggio.strip()) < 1:
        return get_error_message("Il dosaggio non può essere vuoto!")
    
    # Validazione data
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
        datetime.strptime(ora, '%H:%M').time()
    except ValueError:
        return get_error_message("Formato ora non valido!")
    
    return None


def _validate_sintomi_input(tipo, descrizione, data_inizio, data_fine, frequenza):
    """Valida input form sintomi"""
    if not tipo or not descrizione or not data_inizio:
        return get_error_message("Per favore compila tutti i campi obbligatori!")
    
    if tipo == 'sintomo' and not frequenza:
        return get_error_message("Per favore seleziona la frequenza del sintomo!")
    
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
    if data_fine and data_fine.strip():
        try:
            data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d').date()
            data_oggi = datetime.now().date()
            
            if data_fine_obj > data_oggi:
                return get_error_message("La data di fine non può essere nel futuro!")
            if data_fine_obj < data_inizio_obj:
                return get_error_message("La data di fine non può essere precedente alla data di inizio!")
        except ValueError:
            return get_error_message("Formato data fine non valido!")
    
    return None

def _create_empty_figures(message="Nessuna glicemia registrata"):
    """Crea tre figure vuote con messaggio"""
    def empty_fig():
        f = go.Figure()
        f.update_yaxes(range=[0, 300])
        f.add_annotation(text=message, xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False)
        f.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
        return f
    
    ef = empty_fig()
    return ef, ef, ef


def _add_clinical_thresholds(fig, x_labels):
    """Aggiunge soglie cliniche al grafico"""
    # Soglia 180 mg/dL
    fig.add_trace(go.Scatter(
        x=x_labels, y=[180]*len(x_labels),
        mode="lines", name="Glicemia superiore a 180",
        line=dict(color="red", dash="dash"), hoverinfo="skip"
    ))
    
    # Fascia normale 80-130 mg/dL
    y_low = [80]*len(x_labels)
    y_high = [130]*len(x_labels)
    
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_low, mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip", legendgroup="norma"
    ))
    
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_high, mode="lines",
        line=dict(width=0), fill="tonexty",
        fillcolor="rgba(144,238,144,0.20)",
        name="Glicemia nella norma (80—130)", hoverinfo="skip", legendgroup="norma"
    ))


def _apply_chart_styling(fig):
    """Applica stile comune ai grafici"""
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=360, margin=dict(l=10, r=10, t=30, b=10)
    )
    fig.update_xaxes(showline=True, linecolor="black", linewidth=1)
    fig.update_yaxes(showline=True, linecolor="black", linewidth=1)



def _day_bounds(d):
    """Restituisce l'intervallo [inizio_giorno, fine_giorno) per la data d."""
    start = datetime.combine(d,dtime.min)
    end = start + timedelta(days=1)
    return start, end

def _check_patient_alerts(paziente):
    """
    Verifica gli alert per il paziente usando EXISTS (evita gli errori interni di Pony).
    """
    alerts = []
    today = datetime.now().date()
    start, end = _day_bounds(today)

    # 1) Assunzioni di oggi 
    try:
        assunzioni_oggi = []
        for assunzione in paziente.assunzione:
            if start <= assunzione.data_ora < end:
                assunzioni_oggi.append(assunzione)
        has_today = len(assunzioni_oggi) > 0    
        
    except Exception:
        # fallback ultra-safe: nessuna assunzione oggi
        has_today = False

    if not has_today:
        alerts.append({
            'type': 'danger',
            'title': 'Promemoria assunzioni giornaliere',
            'message': 'Non hai ancora registrato assunzioni di farmaci per oggi.',
            'icon': 'bell'
        })

    # 2) Terapie attive (calcolate in Python, niente query complesse)
    def _to_date(x):
        if x is None:
            return None
        return x.date() if hasattr(x, 'date') else x

    try:
        terapie = list(paziente.terapies)
    except Exception:
        terapie = []

    terapie_attive = 0
    for t in terapie:
        di = _to_date(t.data_inizio)
        df = _to_date(t.data_fine)
        if (di is None or di <= today) and (df is None or df >= today):
            terapie_attive += 1

    if terapie_attive > 0 and not has_today:
        alerts.append({
            'type': 'info',
            'title': f'Hai {terapie_attive} terapie attive',
            'message': 'Ricorda di seguire le indicazioni del medico per dosaggi e orari.',
            'icon': 'pills'
        })

    # 3) Glicemie di oggi (EXISTS)
    # #try:
    #     glicemie_oggi = []
    #     for g in paziente.glicemias:
    #         if start <= g.data_ora < end:
    #             glicemie_oggi.append(g)
    #     has_glicemia_today = len(glicemie_oggi) > 0       
    # except Exception:
    #     has_glicemia_today = False

    # if not has_glicemia_today:
    #     alerts.append({
    #         'type': 'warning',
    #         'title': 'Promemoria misurazione glicemia',
    #         'message': 'Non hai ancora registrato misurazioni di glicemia oggi.',
    #         'icon': 'tint'
    #     })

    return alerts



# 3. AGGIUNGI questa nuova funzione ALLA FINE del file (dopo _apply_chart_styling)
def _register_alert_callbacks(app):
    """Gestione alert: (1) banner sopra i bottoni, (2) Modal con lista alert"""

    # (1) Mostra/nasconde il banner in base alle assunzioni di oggi
    @app.callback(
        Output('meds-alert-container', 'children'),
        [Input('patient-content', 'children'),
         Input('alerts-refresh', 'data')],
        prevent_initial_call=False
    )
    @db_session
    def render_meds_alert_banner(_, refresh_data):
        """Mostra il banner promemoria per assunzioni giornaliere"""
        #per debug questo sotto
        print(f"DEBUG: render_meds_alert_banner chiamato con refresh_data = {refresh_data}")
        try:
            if not current_user.is_authenticated:
                return dash.no_update

            paziente = Paziente.get(username=current_user.username)
            if not paziente:
                return dash.no_update

            from datetime import datetime
            today = datetime.now().date()
            start, end = _day_bounds(today)

            # Verifica se ci sono assunzioni registrate oggi
            assunzioni_oggi = []
            for assunzione in paziente.assunzione:
                if start <= assunzione.data_ora < end:
                    assunzioni_oggi.append(assunzione)
            has_today = len(assunzioni_oggi) > 0
            #per debug questo sotto
            print(f"DEBUG: has_today = {has_today}")
            if has_today:
                #debug 
                print("DEBUG: Nascondo banner - assunzioni trovate")
                return None  # Nessun banner se ha già registrato assunzioni oggi
            
            # Mostra promemoria per completare le assunzioni giornaliere
            print("DEBUG: Mostro banner - nessuna assunzione oggi")
            return get_medication_alert()

        except Exception as e:
            print(f"DEBUG: Eccezione in render_meds_alert_banner: {str(e)}")
            return dash.no_update

    # (2) Clic campanellina nel header -> apri/chiudi Modal e popola contenuto
    @app.callback(
        Output('alerts-modal', 'is_open'),
        Output('alerts-modal-body', 'children'),
        Output('bell-button', 'color'),  # Cambia colore campanella
        Input('bell-button', 'n_clicks'),
        Input('alerts-modal-close', 'n_clicks'),
        Input('patient-content', 'children'),  # Trigger per aggiornamento
        State('alerts-modal', 'is_open'),
        prevent_initial_call=False
    )
    @db_session
    def toggle_alerts_modal(n_bell, n_close, content_update, is_open):
        ctx = dash.callback_context
        
        # Prepara il contenuto degli alert
        items = []
        bell_color = "success"  # Default verde
        
        try:
            if current_user.is_authenticated:
                paziente = Paziente.get(username=current_user.username)
            else:
                paziente = None

            if paziente:
                alerts = _check_patient_alerts(paziente)
                
                # Determina colore campanella in base alla priorità degli alert
                if any(a['type'] == 'danger' for a in alerts):
                    bell_color = "danger"
                elif any(a['type'] == 'warning' for a in alerts):
                    bell_color = "warning"
                elif alerts:
                    bell_color = "info"
                
                # Crea elementi per il modal
                for alert in alerts:
                    color_map = {
                        'danger': 'text-danger',
                        'warning': 'text-warning', 
                        'info': 'text-info'
                    }
                    
                    items.append(
                        dbc.ListGroupItem([
                            html.Div([
                                html.Strong(alert['title'], className=color_map.get(alert['type'], ''))
                            ]),
                            html.Div(alert['message'], className="mt-1 small")
                        ], className=f"border-start border-{alert['type']} border-3")
                    )
                    
        except Exception as e:
            items.append(dbc.ListGroupItem(f"Errore nel recupero alert: {str(e)}"))

        body_children = dbc.ListGroup(items, flush=True) if items else html.Div(
            "Nessun promemoria al momento. Ottimo lavoro! 🎉", 
            className="text-center p-3"
        )

        # Gestisci apertura/chiusura modal
        if not ctx.triggered:
            # Prima apertura - solo aggiorna colore campanella
            return False, body_children, bell_color
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'bell-button':
            return (not is_open), body_children, bell_color
        elif trigger_id == 'alerts-modal-close':
            return False, body_children, bell_color
        elif trigger_id == 'patient-content':
            # Solo aggiorna contenuto e colore, non aprire
            return is_open, body_children, bell_color

        return is_open, body_children, bell_color