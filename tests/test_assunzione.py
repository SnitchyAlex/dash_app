# tests/test_assunzione.py
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import controller.patient as patient

class TestSaveAssunzione(unittest.TestCase):
    def setUp(self):
        # input comuni
        self.selected_farmaco = "altro"   # simuliamo scelta custom, ma patchiamo _get_farmaco_name
        self.nome_custom = "Metformina"
        self.dosaggio = "500 mg"
        self.data = "2025-09-15"
        self.ora = "08:00"
        self.note = "dopo colazione"
        self.terapie_data = {}           # non usato perché patchiamo il resolver del nome

    def call(self, n_clicks=1):
        return patient._save_assunzione_core(
            n_clicks=n_clicks,
            selected_farmaco=self.selected_farmaco,
            nome_custom=self.nome_custom,
            dosaggio=self.dosaggio,
            data_assunzione=self.data,
            ora=self.ora,
            note=self.note,
            terapie_data=self.terapie_data
        )

    def test_no_clicks_ritorna_no_update(self):
        res, refresh = self.call(n_clicks=0)
        self.assertIs(res, patient.dash.no_update)
        self.assertIs(refresh, patient.dash.no_update)

    @patch("controller.patient._get_farmaco_name", return_value="Metformina")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_assunzione_input_updated", return_value="Errore di validazione")
    def test_errore_validazione_interrompe(self, mock_validate, mock_Paziente, mock_get_name):
        res, refresh = self.call()
        self.assertEqual(res, "Errore di validazione")
        self.assertIs(refresh, patient.dash.no_update)
        mock_Paziente.get.assert_not_called()

    @patch("controller.patient._get_farmaco_name", return_value="Metformina")
    @patch("controller.patient.get_error_message", return_value="Errore: paziente non trovato!")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_assunzione_input_updated", return_value=None)
    def test_paziente_non_trovato(self, _, mock_Paziente, mock_get_error, mock_get_name):
        mock_Paziente.get.return_value = None
        patient.current_user = MagicMock(username="mario")

        res, refresh = self.call()

        self.assertEqual(res, "Errore: paziente non trovato!")
        self.assertIs(refresh, patient.dash.no_update)
        mock_get_error.assert_called()
        mock_Paziente.get.assert_called_once_with(username="mario")

    @patch("controller.patient._get_farmaco_name", return_value="Metformina")
    @patch("controller.patient.get_assunzione_success_message", return_value="OK")
    @patch("controller.patient.pytime.time", return_value=1234567890)
    @patch("controller.patient.commit")
    @patch("controller.patient.Assunzione")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_assunzione_input_updated", return_value=None)
    def test_successo_crea_assunzione_e_commit(
        self, _, mock_Paziente, mock_Assunzione, mock_commit, mock_time, mock_success, mock_get_name
    ):
        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        res, refresh = self.call()

        self.assertEqual(res, "OK")
        self.assertIsInstance(refresh, dict)
        self.assertEqual(refresh.get("ts"), 1234567890)

        attesa_data = datetime.strptime(self.data, "%Y-%m-%d").date()
        attesa_ora = datetime.strptime(self.ora, "%H:%M").time()
        attesa_data_ora = datetime.combine(attesa_data, attesa_ora)

        mock_Assunzione.assert_called_once()
        kwargs = mock_Assunzione.call_args.kwargs
        self.assertIs(kwargs["paziente"], paz)
        self.assertEqual(kwargs["nome_farmaco"], "Metformina")
        self.assertEqual(kwargs["dosaggio"], self.dosaggio.strip())
        self.assertEqual(kwargs["data_ora"], attesa_data_ora)
        self.assertEqual(kwargs["note"], self.note.strip())

        mock_commit.assert_called_once()
        mock_Paziente.get.assert_called_once_with(username="mario")
        mock_success.assert_called()

    @patch("controller.patient._get_farmaco_name", return_value="Metformina")
    @patch("controller.patient.get_error_message", return_value="Errore durante il salvataggio: BOOM")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_assunzione_input_updated", return_value=None)
    def test_eccezione_gestita_ritorna_errore(self, _, mock_Paziente, mock_get_error, mock_get_name):
        patient.current_user = MagicMock(username="mario")
        mock_Paziente.get.side_effect = RuntimeError("BOOM")

        res, refresh = self.call()

        self.assertEqual(res, "Errore durante il salvataggio: BOOM")
        self.assertIs(refresh, patient.dash.no_update)
        mock_get_error.assert_called()

    @patch("controller.patient._get_farmaco_name", return_value="Metformina")
    @patch("controller.patient.get_error_message", return_value="Errore durante il salvataggio")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_assunzione_input_updated", return_value=None)
    def test_data_o_ora_formato_errato(self, _, mock_Paziente, mock_get_error, mock_get_name):
        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        self.data = "2025/09/15"  # formato sbagliato rispetto a '%Y-%m-%d'
        # self.ora = "8:00"       # alternativa: formato sbagliato rispetto a '%H:%M'

        res, refresh = self.call()

        self.assertEqual(res, "Errore durante il salvataggio")
        self.assertIs(refresh, patient.dash.no_update)
        mock_get_error.assert_called_once()
        mock_Paziente.get.assert_called_once_with(username="mario")

    @patch("controller.patient.get_assunzione_success_message", return_value="OK")
    @patch("controller.patient.pytime.time", return_value=1234567890)
    @patch("controller.patient.commit")
    @patch("controller.patient.Assunzione")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_assunzione_input_updated", return_value=None)
    def test_successo_con_terapia_prescritta_composite_key(
        self, _, mock_Paziente, mock_Assunzione, mock_commit, mock_time, mock_success
    ):
        # Chiave "UI" che rappresenta la PK composta di Terapia: medico_nome||paziente||nome_farmaco||data_inizio_iso
        key = "DR_MARIO||anna.sandre||Metformina||2025-09-01T08:00:00"
        self.selected_farmaco = key
        self.terapie_data = {
            key: {"nome": "Metformina", "dosaggio": "850 mg"}
        }
        # La UI precompila il dosaggio suggerito e lo passa al core
        self.dosaggio = "850 mg"

        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        # NON patchiamo _get_farmaco_name per testare il ramo reale che usa terapie_data
        res, refresh = self.call()

        self.assertEqual(res, "OK")
        self.assertEqual(refresh.get("ts"), 1234567890)

        attesa_data = datetime.strptime(self.data, "%Y-%m-%d").date()
        attesa_ora = datetime.strptime(self.ora, "%H:%M").time()
        attesa_data_ora = datetime.combine(attesa_data, attesa_ora)

        mock_Assunzione.assert_called_once()
        kwargs = mock_Assunzione.call_args.kwargs
        self.assertIs(kwargs["paziente"], paz)
        self.assertEqual(kwargs["nome_farmaco"], "Metformina")  # risolto da terapie_data
        self.assertEqual(kwargs["dosaggio"], "850 mg")          # suggerito e passato
        self.assertEqual(kwargs["data_ora"], attesa_data_ora)
        self.assertEqual(kwargs["note"], self.note.strip())

        mock_commit.assert_called_once()
        mock_Paziente.get.assert_called_once_with(username="mario")
        mock_success.assert_called()
    # --- EDGE: quando ho un dosaggio vuoto ------------------------------------------------
    @patch("controller.patient._get_farmaco_name", return_value="Metformina")
    @patch("controller.patient.get_error_message", return_value="Il dosaggio non può essere vuoto!")
    @patch("controller.patient.Paziente")
    def test_dosaggio_vuoto_bloccato(self, mock_Paziente, mock_get_error, mock_get_name):
        # dosaggio vuoto / solo spazi
        self.dosaggio = "   "
        # opzionale: settiamo anche selected_farmaco="altro" ma non è necessario perché mock_get_name già ritorna "Metformina"
        self.selected_farmaco = "altro"

        res, refresh = self.call()

        # La validazione deve bloccare prima di toccare il DB
        self.assertEqual(res, "Il dosaggio non può essere vuoto!")
        self.assertIs(refresh, patient.dash.no_update)
        mock_Paziente.get.assert_not_called()
        mock_get_name.assert_called_once()
        mock_get_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
