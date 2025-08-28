# controller/patient.py
"""Controller per la gestione dei pazienti"""
import dash
from dash.dependencies import Input, Output, State
from flask_login import current_user
from dash import html,dcc #aggiunta dcc 
from datetime import datetime
from pony.orm import db_session, commit
from model.glicemia import Glicemia
from model.assunzione import Assunzione
from model.paziente import Paziente
from model.sintomi import Sintomi
import pandas as pd #import per creare grafici su andamento glicemico
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

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
    
    
    # ANDAMENTO GLICEMICO (PAZIENTE): mostra la card con i 3 grafici
    @app.callback(
        Output('patient-content', 'children', allow_duplicate=True),
        Input('btn-andamento-glicemico', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_andamento_glicemico(n_clicks):
        if not n_clicks:
            return dash.no_update
        # UI definita nella VIEW
        return get_andamento_glicemico_view()
    # --- ANDAMENTO GLICEMICO (PAZIENTE): genera i 3 grafici (DOW, settimanale, mensile) ---
    @app.callback(
        Output("patient-week-dow", "figure"),
        Output("patient-weekly-avg", "figure"),
        Output("patient-monthly-avg", "figure"),
        Input("patient-content", "children"),   # render iniziale della card
        Input("weeks-window", "value"),         # 4 / 8 / 52 (tutto l'anno)
        prevent_initial_call=False
    )
    @db_session
    def render_week_month_charts(_children, weeks_window):
        from datetime import timedelta, datetime as _dt

        paz = Paziente.get(username=current_user.username)
        if not paz:
            return go.Figure(), go.Figure(), go.Figure()

        # Recupera tutte le rilevazioni del paziente tramite backref (evita select/generator)
        all_meas = list(paz.rilevazione)
        if not all_meas:
            def empty_fig(msg="Nessuna glicemia registrata"):
                f = go.Figure()
                f.update_yaxes(range=[0, 300])
                f.add_annotation(text=msg, xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                f.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
                return f
            ef = empty_fig()
            return ef, ef, ef

        # DataFrame base
        df = pd.DataFrame([{"data": g.data_ora, "valore": g.valore} for g in all_meas])
        df = df.sort_values("data")
        df["data"] = pd.to_datetime(df["data"])
        df.set_index("data", inplace=True)

                # =============================
        # A) Giorni della settimana (settimana corrente)
        # =============================
        today = _dt.now()
        start_week = (today - timedelta(days=today.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )  # Lunedì
        end_week = start_week + timedelta(days=7)

        week_df = df.loc[(df.index >= start_week) & (df.index < end_week)].copy()

        fig_dow = go.Figure()
        fig_dow.update_yaxes(range=[0, 300], title="mg/dL")

        # Etichette asse X in italiano, Lunedì -> Domenica
        dow_order = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        fig_dow.update_xaxes(categoryorder="array", categoryarray=dow_order, title="Giorno della settimana")

        if not week_df.empty:
            week_df["giorno_label"] = week_df.index.dayofweek.map(
                {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}
            )
            # Punti (grigio neutro) 
            #qua decidere se si vogliono visualizzare anche i punti delle rilevazioni effettuate
            #fig_dow.add_trace(go.Scatter(
               # x=week_df["giorno_label"], y=week_df["valore"],
                #mode="markers", name="Rilevazioni", marker=dict(size=9, color="#6C757D")
            #))
            # Media per giorno (ARANCIO)
            daily_mean = week_df.groupby("giorno_label")["valore"].mean().reindex(dow_order)
            fig_dow.add_trace(go.Scatter(
                x=dow_order, y=daily_mean.values,
                mode="lines+markers", name="Media giorno",
                line=dict(color="#F58518", width=2),
                connectgaps=True
            ))
            # --- Soglia 180 come linea "vera" (cliccabile) ---
            fig_dow.add_trace(go.Scatter(
            x=dow_order,
            y=[180]*len(dow_order),
            mode="lines",
            name="Glicemia superiore a 180",
            line=dict(color="red", dash="dash"),
            hoverinfo="skip"  # evita tooltip ridondanti
            ))
            # --- Fascia 80–130 come area riempita (cliccabile) ---
            y_low  = [80]*len(dow_order)
            y_high = [130]*len(dow_order)
            # base invisibile
            fig_dow.add_trace(go.Scatter(
            x=dow_order, y=y_low,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
            legendgroup="norma"
            ))
            fig_dow.add_trace(go.Scatter(
            x=dow_order, y=y_high,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(144,238,144,0.20)",  # LightGreen con trasparenza
            name="Glicemia nella norma (80–130)",
            hoverinfo="skip",
            legendgroup="norma"
            ))

        
        # Guide cliniche
        #fig_dow.add_hrect(y0=80, y1=130, fillcolor="LightGreen", opacity=0.20, line_width=0)
        #fig_dow.add_hline(y=180, line=dict(color='red',dash="dash"), annotation_text="180")
        #fig_dow.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified")

        #fig_dow.add_trace(go.Scatter(x=[None], y=[None],mode="lines",line=dict(color="red", dash="dash"),
        #name="Glicemia superiore a 180"))
        # Trace fittizio solo per la legenda
        #fig_dow.add_trace(go.Scatter(x=[None], y=[None],mode="markers",marker=dict(size=15,color="LightGreen",
        #symbol="square"),name="Glicemia nella norma (80–130)"))
                # =============================
        # B) Media settimana per settimana (ultime N settimane)
        # =============================
        if not weeks_window:
            weeks_window = 8
        since = _dt.now() - timedelta(weeks=int(weeks_window))
        recent = df.loc[df.index >= since].copy()

        # settimane ISO che iniziano il lunedì
        weekly_mean = recent["valore"].resample("W-MON",label="left", closed="left").mean()
        #questo l'ho fatto per fare in modo che sia posizionato nella settima giusta e non in quella avanti
        fig_week = go.Figure()
        fig_week.update_yaxes(range=[0, 300], title="mg/dL")

        if not weekly_mean.empty:
            # Etichetta X come intervallo: "dd/mm–dd/mm" (Lun→Dom)
            x_labels = []
            for ts in weekly_mean.index:
                start = ts                   # lunedì
                end = ts + timedelta(days=6) # venerdì
                x_labels.append(f"{start.strftime('%d/%m')}–{end.strftime('%d/%m')}")
            fig_week.add_trace(go.Scatter(x=x_labels, y=weekly_mean.values,mode="lines+markers",
                name=f"Media settimanale (ultime {weeks_window} sett.)",
                line=dict(color="#4C78A8", width=2),
                connectgaps=True    # BLU
        ))
        else:
            fig_week.add_annotation(text="Nessuna settimana con dati nel periodo",
                                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if not weekly_mean.empty:
        # Linea soglia 180
            fig_week.add_trace(go.Scatter(
            x=x_labels,
            y=[180]*len(x_labels),
            mode="lines",
            name="Glicemia superiore a 180",
            line=dict(color="red", dash="dash"),
            hoverinfo="skip"
        ))
            # Fascia 80–130 come area riempita
            y_low  = [80]*len(x_labels)
            y_high = [130]*len(x_labels)

            fig_week.add_trace(go.Scatter(
            x=x_labels, y=y_low,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
            legendgroup="norma"
        ))
            fig_week.add_trace(go.Scatter(
            x=x_labels, y=y_high,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(144,238,144,0.20)",  # LightGreen trasparente
            name="Glicemia nella norma (80–130)",
            hoverinfo="skip",
            legendgroup="norma"
        ))
        else:
            fig_week.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name="Glicemia superiore a 180",
            line=dict(color="red", dash="dash")
        ))
            fig_week.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            name="Glicemia nella norma (80–130)",
            marker=dict(size=15, color="LightGreen", symbol="square")
        )) 
            
        #fig_week.add_hrect(y0=80, y1=130, fillcolor="LightGreen", opacity=0.20, line_width=0)
        #fig_week.add_hline(y=180, line=dict(color='red',dash="dash"), annotation_text="180")
        #fig_week.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10),
                               #xaxis_title="Settimana (Lun→Dom)", hovermode="x unified")

                # =============================
        # C) Media mese per mese (ANNO CORRENTE fisso Gen→Dic) — ROSSO
        # =============================
        year = _dt.now().year
        year_start = pd.Timestamp(year=year, month=1, day=1)
        # Indice fisso dei 12 mesi dell'anno corrente (start-of-month)
        idx_months = pd.date_range(start=year_start, periods=12, freq="MS")

        # Filtra i dati all'anno corrente e calcola media per mese (start-of-month)
        df_year = df.loc[(df.index >= year_start) & (df.index < year_start + pd.offsets.YearEnd(0) + pd.Timedelta(days=1))].copy()
        monthly_mean = df_year["valore"].resample("MS").mean().reindex(idx_months)  # NaN se mese senza dati

        mesi_it = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
        x_m = [mesi_it[ts.month - 1] for ts in monthly_mean.index]

        fig_month = go.Figure()
        fig_month.update_yaxes(range=[0, 300], title="mg/dL")
        fig_month.add_trace(go.Scatter(
            x=x_m, y=monthly_mean.values,
            mode="lines+markers", name=f"Media mensile {year}",
            line=dict(color="#4C78A8", width=2),  # ROSSO
            connectgaps=True  # metti True per connettere i mesi anche se mancano dati
        ))

        # (opzionale) Nota se non ci sono dati in nessun mese
        if monthly_mean.isna().all():
            fig_month.add_annotation(text="Nessun dato per l'anno selezionato",
                                     xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)

        #fig_month.add_hrect(y0=80, y1=130, fillcolor="LightGreen", opacity=0.20, line_width=0)
        #fig_month.add_hline(y=180, line=dict(color='red',dash="dash"), annotation_text="180")
        #fig_month.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10),
                                #xaxis_title=f"Anno ({year})", hovermode="x unified")
        fig_month.add_trace(go.Scatter(
        x=x_m,
        y=[180]*len(x_m),
        mode="lines",
        name="Glicemia superiore a 180",
        line=dict(color="red", dash="dash"),
        hoverinfo="skip"
        ))
        # --- Fascia 80–130 come area riempita (cliccabile) ---
        y_low_m  = [80]*len(x_m)
        y_high_m = [130]*len(x_m)
        # base invisibile
        fig_month.add_trace(go.Scatter(
        x=x_m, y=y_low_m,
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
        legendgroup="norma"
        ))

                  # top con fill verso la precedente
        fig_month.add_trace(go.Scatter(
        x=x_m, y=y_high_m,
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(144,238,144,0.20)",  # LightGreen trasparente
        name="Glicemia nella norma (80–130)",
        hoverinfo="skip",
        legendgroup="norma"
        ))     
        # Imposta background bianco per tutti i grafici
        for fig in (fig_dow, fig_week, fig_month):
            fig.update_layout(
            plot_bgcolor="white",   # area dati (dove ci sono linee e punti)
            paper_bgcolor="white"   # intera figura, margini inclusi
        )
            fig.update_xaxes(
            showline=True,          # mostra linea asse X
            linecolor="black",      # colore linea asse
            linewidth=1             # spessore linea
        )
            fig.update_yaxes(
            showline=True,          # mostra linea asse Y
            linecolor="black",
            linewidth=1
        )    
        return fig_dow, fig_week, fig_month
