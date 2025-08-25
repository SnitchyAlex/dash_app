# controller/doctor.py
"""Controller per la gestione dei medici"""
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import html
from datetime import datetime
from pony.orm import db_session, commit, select
from model.terapia import Terapia
from model.medico import Medico
from model.paziente import Paziente
from view.doctor import (
    get_terapie_menu,
    get_assegna_terapia_form,
    get_modifica_terapia_form,
    get_elimina_terapia_form,
    get_terapia_success_message,
    get_error_message,
    get_indicazioni_display,
    get_terapie_list_for_edit,
    get_edit_terapia_form,
    get_terapia_modify_success_message,
    get_terapie_list_for_delete,
    get_terapia_delete_success_message
)


def register_doctor_callbacks(app):
    """Registra tutti i callback per i medici"""
    
    # Callback principale: mostra il menu terapie
    @app.callback(
        Output('doctor-content', 'children'),
        Input('btn-gestisci-terapie', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_terapie_menu(n_clicks):
        """Mostra il menu delle opzioni terapie"""
        if n_clicks:
            return get_terapie_menu()
        return dash.no_update

    # Callback per tornare al menu principale (svuota il contenuto)
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-torna-menu-principale', 'n_clicks'),
        prevent_initial_call=True
    )
    def torna_menu_principale(n_clicks):
        """Torna al menu principale nascondendo il contenuto"""
        if n_clicks:
            return html.Div()
        return dash.no_update

    # Callback per mostrare il form assegna terapia
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-assegna-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_assegna_terapia_form(n_clicks):
        """Mostra il form per assegnare una terapia"""
        print(f"DEBUG: n_clicks = {n_clicks}")
        print(f"DEBUG: current_user.username = {current_user.username}")
        
        if n_clicks:
            medico = Medico.get(username=current_user.username)
            print(f"DEBUG: medico trovato = {medico}")
            
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            pazienti = list(Paziente.select())
            print(f"DEBUG: numero pazienti totali = {len(pazienti)}")
            
            return get_assegna_terapia_form(pazienti)
        return dash.no_update

    # Callback per mostrare il form modifica terapia
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-modifica-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_modifica_terapia_form(n_clicks):
        """Mostra il form per modificare una terapia"""
        if n_clicks:
            medico = Medico.get(username=current_user.username)
            
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            pazienti = list(Paziente.select())
            return get_modifica_terapia_form(pazienti)
        return dash.no_update

    # Callback per mostrare il form elimina terapia
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-elimina-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_elimina_terapia_form(n_clicks):
        """Mostra il form per eliminare una terapia"""
        if n_clicks:
            medico = Medico.get(username=current_user.username)
            
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            pazienti = list(Paziente.select())
            return get_elimina_terapia_form(pazienti)
        return dash.no_update

    # Callback generico che cattura tutti i possibili bottoni "torna menu terapie"
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        [Input('btn-torna-menu-terapie', 'n_clicks')],
        prevent_initial_call=True
    )
    def torna_menu_terapie_generico(n_clicks):
        """Torna al menu terapie"""
        if n_clicks:
            return get_terapie_menu()
        return dash.no_update

    # Callback per salvare la terapia
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
            
            # Trova il paziente selezionato
            paziente = Paziente.get(username=paziente_id)
            if not paziente:
                return get_error_message("Errore: paziente non trovato!")
            
            # assegna in automatico il paziente al medico
            if medico not in paziente.doctors:
                print(f"DEBUG: Assegnando automaticamente il Dr. {medico.name} {medico.surname} al paziente {paziente.name} {paziente.surname}")
                paziente.doctors.add(medico)
                # Committa l'assegnazione prima di procedere con la terapia
                commit()
                print(f"DEBUG: Assegnazione completata. Il medico ora segue il paziente.")
            else:
                print(f"DEBUG: Il Dr. {medico.name} {medico.surname} seguiva già il paziente {paziente.name} {paziente.surname}")
            
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

    # Callback per il bottone "nuova terapia" nel messaggio di successo
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
                pazienti = list(Paziente.select())
                return get_assegna_terapia_form(pazienti)
        return dash.no_update

    # CALLBACK PER MODIFICA TERAPIE

    # Callback per mostrare le terapie del paziente selezionato (form modifica)
    @app.callback(
        Output('terapie-paziente-list', 'children'),
        Input('select-paziente-modifica', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def show_patient_therapies_for_edit(patient_username):
        """Mostra le terapie del paziente selezionato per la modifica"""
        if not patient_username:
            return dash.no_update
        
        try:
            paziente = Paziente.get(username=patient_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")
            
            # Modo semplice: prendi tutte le terapie e filtra manualmente
            terapie = []
            for terapia in Terapia.select():
                if terapia.paziente.username == patient_username:
                    terapie.append(terapia)
            
            if not terapie:
                return dbc.Alert([
                    html.H6("Nessuna terapia trovata", className="alert-heading"),
                    html.P(f"Il paziente {paziente.name} {paziente.surname} non ha terapie assegnate.")
                ], color="info")
            
            return get_terapie_list_for_edit(terapie, paziente)
            
        except Exception as e:
            return get_error_message(f"Errore: {str(e)}")

    # Callback per caricare i dati della terapia nel form di modifica
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input({'type': 'btn-modifica-terapia-specifica', 'index': dash.dependencies.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def load_therapy_for_edit(n_clicks_list):
        """Carica i dati della terapia selezionata nel form di modifica"""
        if not any(n_clicks_list):
            return dash.no_update
        
        # Trova quale bottone è stato cliccato
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        
        # Estrai la chiave composta dal bottone cliccato
        button_id = ctx.triggered[0]['prop_id']
        
        # Parsing della chiave composita dal JSON del button ID
        import json
        try:
            # Estrai la parte JSON dell'ID
            json_start = button_id.find('{')
            json_end = button_id.rfind('}') + 1
            button_data = json.loads(button_id[json_start:json_end])
            composite_key = button_data['index']
            
            print(f"DEBUG: Composite key ricevuta: {composite_key}")
            
            # Parsing della chiave composita: medico_nome|paziente_username|nome_farmaco|data_inizio
            parts = composite_key.split('|')
            if len(parts) != 4:
                return get_error_message("Formato chiave terapia non valido!")
            
            medico_nome, paziente_username, nome_farmaco, data_inizio_str = parts
            
            # Converti la data
            if data_inizio_str == 'None':
                data_inizio_obj = None
            else:
                data_inizio_obj = datetime.strptime(data_inizio_str, '%Y-%m-%d')
            
            print(f"DEBUG: Ricerca terapia con parametri:")
            print(f"  - medico_nome: {medico_nome}")
            print(f"  - paziente_username: {paziente_username}")
            print(f"  - nome_farmaco: {nome_farmaco}")
            print(f"  - data_inizio: {data_inizio_obj}")
            
            # Trova la terapia usando la chiave composita
            paziente = Paziente.get(username=paziente_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")

            # Verifica che il medico corrente possa modificare questa terapia
            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
        
            # CONTROLLO AUTORIZZAZIONI: verifica che il medico segua questo paziente
            if medico not in paziente.doctors:
                return get_error_message(f"Accesso negato: Non sei autorizzato a modificare le terapie del paziente {paziente.name} {paziente.surname}.")
            
            # Cerca la terapia con i parametri della chiave composita
            terapia = Terapia.get(
                medico_nome=medico_nome,
                paziente=paziente,
                nome_farmaco=nome_farmaco,
                data_inizio=data_inizio_obj
            )
            
            if not terapia:
                return get_error_message("Terapia non trovata!")
            
            print(f"DEBUG: Terapia trovata: {terapia.nome_farmaco} per {terapia.paziente.name}")
            
            # Verifica che il medico corrente possa modificare questa terapia
            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            # Carica tutti i pazienti per il dropdown
            pazienti = list(Paziente.select())
            
            return get_edit_terapia_form(terapia, pazienti)
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: Errore parsing JSON: {e}")
            return get_error_message("Errore nel parsing dell'ID del bottone!")
        except ValueError as e:
            print(f"DEBUG: Errore conversione data: {e}")
            return get_error_message("Errore nella conversione della data!")
        except Exception as e:
            print(f"DEBUG: Errore generico: {e}")
            import traceback
            traceback.print_exc()
            return get_error_message(f"Errore nel caricamento della terapia: {str(e)}")

    # Callback per salvare le modifiche alla terapia
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-salva-modifiche-terapia', 'n_clicks'),
        [State('hidden-terapia-key', 'children'),  # Cambiato da hidden-terapia-id a hidden-terapia-key
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
        """Salva le modifiche alla terapia"""
        if not n_clicks:
            return dash.no_update
        
        # Validazione campi obbligatori
        if not terapia_key or not paziente_id or not nome_farmaco or not dosaggio or not assunzioni_giornaliere:
            return get_error_message("Per favore compila tutti i campi obbligatori!")
        
        # Validazioni come nel salvataggio normale...
        if len(nome_farmaco.strip()) < 2:
            return get_error_message("Il nome del farmaco deve essere di almeno 2 caratteri!")
        
        try:
            # Parsing della chiave composita per trovare la terapia originale
            parts = terapia_key.split('|')
            if len(parts) != 4:
                return get_error_message("Formato chiave terapia non valido!")
            
            medico_nome_orig, paziente_username_orig, nome_farmaco_orig, data_inizio_str_orig = parts
            
            # Converti la data originale
            if data_inizio_str_orig == 'None':
                data_inizio_obj_orig = None
            else:
                data_inizio_obj_orig = datetime.strptime(data_inizio_str_orig, '%Y-%m-%d')
            
            # Trova il paziente originale
            paziente_orig = Paziente.get(username=paziente_username_orig)
            if not paziente_orig:
                return get_error_message("Paziente originale non trovato!")
            
            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
        
            # CONTROLLO AUTORIZZAZIONI: verifica che il medico segua il paziente originale
            if medico not in paziente_orig.doctors:
                return get_error_message(f"Accesso negato: Non sei autorizzato a modificare le terapie del paziente {paziente_orig.name} {paziente_orig.surname}.")
        
            
            # Trova la terapia da modificare usando la chiave composita
            terapia = Terapia.get(
                medico_nome=medico_nome_orig,
                paziente=paziente_orig,
                nome_farmaco=nome_farmaco_orig,
                data_inizio=data_inizio_obj_orig
            )
            
            if not terapia:
                return get_error_message("Terapia non trovata!")
            
            # Trova il nuovo paziente
            paziente_nuovo = Paziente.get(username=paziente_id)
            if not paziente_nuovo:
                return get_error_message("Nuovo paziente non trovato!")
            
            # Trova il medico corrente
            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            # Validazione assunzioni
            assunzioni = int(assunzioni_giornaliere)
            if assunzioni < 1 or assunzioni > 10:
                return get_error_message("Il numero di assunzioni giornaliere deve essere tra 1 e 10!")
            
            # Validazione date
            data_inizio_obj = None
            if data_inizio:
                data_inizio_obj = datetime.strptime(data_inizio, '%Y-%m-%d')
            
            data_fine_obj = None
            if data_fine and data_fine.strip():
                data_fine_obj = datetime.strptime(data_fine, '%Y-%m-%d')
                if data_inizio_obj and data_fine_obj < data_inizio_obj:
                    return get_error_message("La data di fine non può essere precedente alla data di inizio!")
            
            # Combina le indicazioni
            indicazioni_complete = []
            if indicazioni_select:
                indicazioni_complete.append(get_indicazioni_display(indicazioni_select))
            if indicazioni_custom and indicazioni_custom.strip():
                indicazioni_complete.append(indicazioni_custom.strip())
            
            indicazioni_finali = ". ".join(indicazioni_complete) if indicazioni_complete else ""
            
            # IMPORTANTE: Se stai cambiando la chiave primaria, devi eliminare e ricreare
            if (paziente_nuovo != terapia.paziente or 
                nome_farmaco.strip() != terapia.nome_farmaco or 
                data_inizio_obj != terapia.data_inizio):
                
                # Salva i valori vecchi
                medico_orig = terapia.medico
                
                # Elimina la vecchia terapia
                terapia.delete()
                commit()
                
                # Crea la nuova terapia con i nuovi dati
                terapia_nuova = Terapia(
                    medico=medico_orig,
                    medico_nome=f"Dr. {medico.name} {medico.surname}",
                    paziente=paziente_nuovo,
                    nome_farmaco=nome_farmaco.strip(),
                    dosaggio_per_assunzione=dosaggio.strip(),
                    assunzioni_giornaliere=assunzioni,
                    indicazioni=indicazioni_finali if indicazioni_finali else None,
                    data_inizio=data_inizio_obj,
                    data_fine=data_fine_obj,
                    note=note.strip() if note else '',
                    modificata=f"Dr. {medico.name} {medico.surname}"
                )
            else:
                # Se la chiave primaria non cambia, aggiorna direttamente
                terapia.dosaggio_per_assunzione = dosaggio.strip()
                terapia.assunzioni_giornaliere = assunzioni
                terapia.indicazioni = indicazioni_finali if indicazioni_finali else None
                terapia.data_fine = data_fine_obj
                terapia.note = note.strip() if note else ''
                terapia.modificata = f"Dr. {medico.name} {medico.surname}"
            
            commit()
            
            paziente_nome = f"{paziente_nuovo.name} {paziente_nuovo.surname}"
            return get_terapia_modify_success_message(
                paziente_nome, nome_farmaco, dosaggio, assunzioni, 
                data_inizio_obj, data_fine_obj
            )
            
        except ValueError as e:
            return get_error_message(f"Errore nei dati inseriti: {str(e)}")
        except Exception as e:
            print(f"DEBUG: Errore nel salvataggio: {e}")
            import traceback
            traceback.print_exc()
            return get_error_message(f"Errore durante il salvataggio: {str(e)}")

    # Callback per il bottone "modifica altra terapia" nel messaggio di successo
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-modifica-altra-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_modify_another_therapy_form(n_clicks):
        """Mostra di nuovo il form di modifica terapia dopo aver salvato"""
        if n_clicks:
            medico = Medico.get(username=current_user.username)
            if medico:
                pazienti = list(Paziente.select())
                return get_modifica_terapia_form(pazienti)
        return dash.no_update


        # Callback per mostrare le terapie del paziente selezionato (form elimina)
    @app.callback(
        Output('terapie-paziente-elimina-list', 'children'),
        Input('select-paziente-elimina', 'value'),
        prevent_initial_call=True
    )
    @db_session
    def show_patient_therapies_for_delete(patient_username):
        """Mostra le terapie del paziente selezionato per l'eliminazione"""
        if not patient_username:
            return dash.no_update
        
        try:

            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
        
            paziente = Paziente.get(username=patient_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")
            
            # Prendi tutte le terapie del paziente
            terapie = []
            for terapia in Terapia.select():
                if terapia.paziente.username == patient_username:
                    terapie.append(terapia)
            
            if not terapie:
                return dbc.Alert([
                    html.H6("Nessuna terapia trovata", className="alert-heading"),
                    html.P(f"Il paziente {paziente.name} {paziente.surname} non ha terapie assegnate.")
                ], color="info")
            
            return get_terapie_list_for_delete(terapie, paziente)
            
        except Exception as e:
            return get_error_message(f"Errore: {str(e)}")

    # Callback per eliminare la terapia selezionata
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input({'type': 'btn-elimina-terapia-specifica', 'index': dash.dependencies.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def delete_specific_therapy(n_clicks_list):
        """Elimina la terapia selezionata"""
        if not any(n_clicks_list):
            return dash.no_update
        
        # Trova quale bottone è stato cliccato
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        
        # Estrai la chiave composta dal bottone cliccato
        button_id = ctx.triggered[0]['prop_id']
        
        # Parsing della chiave composita dal JSON del button ID
        import json
        try:
            # Estrai la parte JSON dell'ID
            json_start = button_id.find('{')
            json_end = button_id.rfind('}') + 1
            button_data = json.loads(button_id[json_start:json_end])
            composite_key = button_data['index']
            
            print(f"DEBUG: Composite key ricevuta per eliminazione: {composite_key}")
            
            # Parsing della chiave composita: medico_nome|paziente_username|nome_farmaco|data_inizio
            parts = composite_key.split('|')
            if len(parts) != 4:
                return get_error_message("Formato chiave terapia non valido!")
            
            medico_nome, paziente_username, nome_farmaco, data_inizio_str = parts
            
            # Converti la data
            if data_inizio_str == 'None':
                data_inizio_obj = None
            else:
                data_inizio_obj = datetime.strptime(data_inizio_str, '%Y-%m-%d')
            
            # Trova la terapia usando la chiave composita
            paziente = Paziente.get(username=paziente_username)
            if not paziente:
                return get_error_message("Paziente non trovato!")
            
             # Verifica che il medico corrente possa eliminare questa terapia
            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
        
            # CONTROLLO AUTORIZZAZIONI: verifica che il medico segua questo paziente
            if medico not in paziente.doctors:
                return get_error_message(f"Accesso negato: Non sei autorizzato a gestire le terapie del paziente {paziente.name} {paziente.surname}.")
            
            # Cerca la terapia con i parametri della chiave composita
            terapia = Terapia.get(
                medico_nome=medico_nome,
                paziente=paziente,
                nome_farmaco=nome_farmaco,
                data_inizio=data_inizio_obj
            )
            
            if not terapia:
                return get_error_message("Terapia non trovata!")
            
            print(f"DEBUG: Terapia da eliminare: {terapia.nome_farmaco} per {terapia.paziente.name}")
            
            # Verifica che il medico corrente possa eliminare questa terapia
            medico = Medico.get(username=current_user.username)
            if not medico:
                return get_error_message("Errore: medico non trovato!")
            
            # Salva i dati per il messaggio di conferma prima di eliminare
            paziente_nome = f"{terapia.paziente.name} {terapia.paziente.surname}"
            farmaco_eliminato = terapia.nome_farmaco
            dosaggio_eliminato = terapia.dosaggio_per_assunzione
            
            # Elimina la terapia
            terapia.delete()
            commit()
            
            return get_terapia_delete_success_message(
                paziente_nome, farmaco_eliminato, dosaggio_eliminato
            )
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: Errore parsing JSON: {e}")
            return get_error_message("Errore nel parsing dell'ID del bottone!")
        except ValueError as e:
            print(f"DEBUG: Errore conversione data: {e}")
            return get_error_message("Errore nella conversione della data!")
        except Exception as e:
            print(f"DEBUG: Errore generico nell'eliminazione: {e}")
            import traceback
            traceback.print_exc()
            return get_error_message(f"Errore nell'eliminazione della terapia: {str(e)}")

    # Callback per il bottone "elimina altra terapia" nel messaggio di successo
    @app.callback(
        Output('doctor-content', 'children', allow_duplicate=True),
        Input('btn-elimina-altra-terapia', 'n_clicks'),
        prevent_initial_call=True
    )
    @db_session
    def show_delete_another_therapy_form(n_clicks):
        """Mostra di nuovo il form di eliminazione terapia dopo aver eliminato"""
        if n_clicks:
            medico = Medico.get(username=current_user.username)
            if medico:
                pazienti = list(Paziente.select())
                return get_elimina_terapia_form(pazienti)
        return dash.no_update
        