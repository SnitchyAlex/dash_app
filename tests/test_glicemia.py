# tests/test_glicemia.py
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import controller.patient as patient


class TestSaveGlicemiaMeasurement(unittest.TestCase):

    def setUp(self):
        # input comuni
        self.valore = "120"
        self.data = "2025-09-15"
        self.ora = "08:00"
        self.note = "prova"
        self.momento_pasto = "dopo_pasto"      # cambia in 'dopo_pasto' per testare due_ore_pasto o meti digiuno/prima_pasto e sotto None
        self.due_ore_pasto = True

    def call(self, n_clicks=1):
        
        return patient._save_glicemia_measurement_core(
            n_clicks=n_clicks,
            valore=self.valore,
            data_misurazione=self.data,
            ora=self.ora,
            momento_pasto=self.momento_pasto,
            note=self.note,
            due_ore_pasto=self.due_ore_pasto
        )

    def test_no_clicks_ritorna_no_update(self):
        res, refresh = self.call(n_clicks=0)
        self.assertIs(res, patient.dash.no_update)
        self.assertIs(refresh, patient.dash.no_update)

    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_glicemia_input", return_value="Errore di validazione")
    def test_errore_validazione_interrompe(self, mock_validate, mock_Paziente):
        res, refresh = self.call()
        self.assertEqual(res, "Errore di validazione")
        self.assertIs(refresh, patient.dash.no_update)
        mock_Paziente.get.assert_not_called()

    @patch("controller.patient.get_error_message", return_value="Errore: paziente non trovato!")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_glicemia_input", return_value=None)
    def test_paziente_non_trovato(self, _, mock_Paziente, mock_get_error):
        mock_Paziente.get.return_value = None
        patient.current_user = MagicMock(username="mario")

        res, refresh = self.call()

        self.assertEqual(res, "Errore: paziente non trovato!")
        self.assertIs(refresh, patient.dash.no_update)
        mock_get_error.assert_called()
        mock_Paziente.get.assert_called_once_with(username="mario")

    @patch("controller.patient.get_success_message", return_value="OK")
    @patch("controller.patient.pytime.time", return_value=1234567890)
    @patch("controller.patient.commit")
    @patch("controller.patient.Glicemia")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_glicemia_input", return_value=None)
    def test_successo_crea_glicemia_e_commit(
        self, _, mock_Paziente, mock_Glicemia, mock_commit, mock_time, mock_success
    ):
        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        self.momento_pasto = "dopo_pasto"
        self.due_ore_pasto = True

        res, refresh = self.call()

        self.assertEqual(res, "OK")
        self.assertIsInstance(refresh, dict)
        self.assertEqual(refresh.get("ts"), 1234567890)

        attesa_data = datetime.strptime(self.data, "%Y-%m-%d").date()
        attesa_ora = datetime.strptime(self.ora, "%H:%M").time()
        attesa_data_ora = datetime.combine(attesa_data, attesa_ora)

        mock_Glicemia.assert_called_once()
        kwargs = mock_Glicemia.call_args.kwargs
        self.assertIs(kwargs["paziente"], paz)
        self.assertEqual(kwargs["valore"], float(self.valore))
        self.assertEqual(kwargs["data_ora"], attesa_data_ora)
        self.assertEqual(kwargs["momento_pasto"], "dopo_pasto")
        self.assertEqual(kwargs["note"], self.note.strip())
        self.assertTrue(kwargs["due_ore_pasto"])

        mock_commit.assert_called_once()
        mock_Paziente.get.assert_called_once_with(username="mario")
        mock_success.assert_called()

    @patch("controller.patient.get_error_message", return_value="Errore durante il salvataggio: BOOM")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_glicemia_input", return_value=None)
    def test_eccezione_gestita_ritorna_errore(self, _, mock_Paziente, mock_get_error):
        patient.current_user = MagicMock(username="mario")
        mock_Paziente.get.side_effect = RuntimeError("BOOM")

        res, refresh = self.call()

        self.assertEqual(res, "Errore durante il salvataggio: BOOM")
        self.assertIs(refresh, patient.dash.no_update)
        mock_get_error.assert_called()

    # --- EDGE: data/ora con formato errato ----------------------------------
    @patch("controller.patient.get_error_message", return_value="Errore durante il salvataggio")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_glicemia_input", return_value=None)
    def test_data_o_ora_formato_errato(self, _, mock_Paziente, mock_get_error):
        # Arrivo alla fase di parsing data/ora e forzo ValueError di strptime
        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        self.data = "2025/09/15"  # formato errato rispetto a '%Y-%m-%d'
        # self.ora = "8:00"        # in alternativa, formato errato rispetto a '%H:%M'

        res, refresh = self.call()

        self.assertEqual(res, "Errore durante il salvataggio")
        self.assertIs(refresh, patient.dash.no_update)
        mock_get_error.assert_called_once()
        mock_Paziente.get.assert_called_once_with(username="mario")

if __name__ == "__main__":
    unittest.main()
