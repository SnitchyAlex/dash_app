# tests/test_sintomi.py
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import controller.patient as patient

class TestSaveSintomo(unittest.TestCase):
    def setUp(self):
        # input comuni
        self.tipo = "sintomo"
        self.descrizione = "Mal di testa"
        self.data_inizio = "2025-09-15"
        self.data_fine = ""              # opzionale
        self.frequenza = "quotidiano"    # richiesto solo se tipo == 'sintomo'
        self.note = "leggero"

    def call(self, n_clicks=1):
        return patient._save_sintomo_core(
            n_clicks=n_clicks,
            tipo=self.tipo,
            descrizione=self.descrizione,
            data_inizio=self.data_inizio,
            data_fine=self.data_fine,
            frequenza=self.frequenza,
            note=self.note
        )

    def test_no_clicks_ritorna_no_update(self):
        res = self.call(n_clicks=0)
        self.assertIs(res, patient.dash.no_update)

    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value="Errore di validazione")
    def test_errore_validazione_interrompe(self, mock_validate, mock_Paziente):
        res = self.call()
        self.assertEqual(res, "Errore di validazione")
        mock_Paziente.get.assert_not_called()

    @patch("controller.patient.get_error_message", return_value="Errore: paziente non trovato!")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value=None)
    def test_paziente_non_trovato(self, _, mock_Paziente, mock_get_error):
        mock_Paziente.get.return_value = None
        patient.current_user = MagicMock(username="mario")

        res = self.call()

        self.assertEqual(res, "Errore: paziente non trovato!")
        mock_get_error.assert_called()
        mock_Paziente.get.assert_called_once_with(username="mario")

    @patch("controller.patient.get_sintomi_success_message", return_value="OK")
    @patch("controller.patient.commit")
    @patch("controller.patient.Sintomi")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value=None)
    def test_successo_crea_sintomo_e_commit(
        self, _, mock_Paziente, mock_Sintomi, mock_commit, mock_success
    ):
        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        res = self.call()

        self.assertEqual(res, "OK")

        attesa_data_inizio = datetime.strptime(self.data_inizio, "%Y-%m-%d").date()

        mock_Sintomi.assert_called_once()
        kwargs = mock_Sintomi.call_args.kwargs
        self.assertIs(kwargs["paziente"], paz)
        self.assertEqual(kwargs["tipo"], "sintomo")
        self.assertEqual(kwargs["descrizione"], self.descrizione.strip())
        self.assertEqual(kwargs["data_inizio"], attesa_data_inizio)
        self.assertIsNone(kwargs["data_fine"])
        self.assertEqual(kwargs["frequenza"], self.frequenza)      # perché tipo == 'sintomo'
        self.assertEqual(kwargs["note"], self.note.strip())

        mock_commit.assert_called_once()
        mock_Paziente.get.assert_called_once_with(username="mario")
        mock_success.assert_called()

    @patch("controller.patient.get_error_message", return_value="Errore durante il salvataggio: BOOM")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value=None)
    def test_eccezione_gestita_ritorna_errore(self, _, mock_Paziente, mock_get_error):
        patient.current_user = MagicMock(username="mario")
        mock_Paziente.get.side_effect = RuntimeError("BOOM")

        res = self.call()

        self.assertEqual(res, "Errore durante il salvataggio: BOOM")
        mock_get_error.assert_called()

    @patch("controller.patient.get_error_message", return_value="Errore durante il salvataggio")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value=None)
    def test_data_inizio_formato_errato(self, _, mock_Paziente, mock_get_error):
        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        self.data_inizio = "2025/09/15"  # formato errato

        res = self.call()

        self.assertEqual(res, "Errore durante il salvataggio")
        mock_get_error.assert_called_once()
        mock_Paziente.get.assert_called_once_with(username="mario")

    # Edge: tipo != 'sintomo' => frequenza non richiesta e salvata come stringa vuota
    @patch("controller.patient.get_sintomi_success_message", return_value="OK")
    @patch("controller.patient.commit")
    @patch("controller.patient.Sintomi")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value=None)
    def test_tipo_cura_frequenza_non_richiesta(
        self, _, mock_Paziente, mock_Sintomi, mock_commit, mock_success
    ):
        paz = MagicMock()
        mock_Paziente.get.return_value = paz
        patient.current_user = MagicMock(username="mario")

        self.tipo = "cura"
        self.frequenza = None  # non obbligatoria

        res = self.call()
        self.assertEqual(res, "OK")

        kwargs = mock_Sintomi.call_args.kwargs
        self.assertEqual(kwargs["tipo"], "cura")
        self.assertEqual(kwargs["frequenza"], "")  # deve essere stringa vuota

    # Edge: data_fine precedente a data_inizio => validazione blocca
    @patch("controller.patient.get_error_message", return_value="La data di fine non può essere precedente alla data di inizio!")
    @patch("controller.patient.Paziente")
    def test_data_fine_precedente_bloccata(self, mock_Paziente, mock_get_error):
        # Usiamo la validazione reale (non patchiamo _validate_sintomi_input)
        self.data_inizio = "2025-09-15"
        self.data_fine = "2025-09-14"
        res = self.call()

        self.assertEqual(res, "La data di fine non può essere precedente alla data di inizio!")
        mock_Paziente.get.assert_not_called()
        mock_get_error.assert_called()
 # Frequenza mancante per 'sintomo'
    @patch("controller.patient.get_error_message", return_value="Per favore seleziona la frequenza del sintomo!")
    @patch("controller.patient.Paziente")
    def test_frequenza_obbligatoria_per_sintomo(self, mock_Paziente, mock_get_error):
        self.frequenza = None
        res = self.call()
        self.assertEqual(res, "Per favore seleziona la frequenza del sintomo!")
        mock_Paziente.get.assert_not_called()
        mock_get_error.assert_called_once()
    #13) Note None -> salvate come stringa vuota 
    @patch("controller.patient.get_sintomi_success_message", return_value="OK")
    @patch("controller.patient.commit")
    @patch("controller.patient.Sintomi")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value=None)
    def test_note_none_diventa_stringa_vuota(self, _, mock_Paziente, mock_Sintomi, mock_commit, mock_success):
        mock_Paziente.get.return_value = MagicMock()
        patient.current_user = MagicMock(username="mario")
        self.note = None
        res = self.call()
        self.assertEqual(res, "OK")
        self.assertEqual(mock_Sintomi.call_args.kwargs["note"], "")

    # data_fine = data_inizio => permesso,puoi mettere che un sintomo inizia e finisce lo stesso giorno
    @patch("controller.patient.get_sintomi_success_message", return_value="OK")
    @patch("controller.patient.commit")
    @patch("controller.patient.Sintomi")
    @patch("controller.patient.Paziente")
    @patch("controller.patient._validate_sintomi_input", return_value=None)
    def test_data_fine_uguale_data_inizio_ok(self, _, mock_Paziente, mock_Sintomi, mock_commit, mock_success):
        mock_Paziente.get.return_value = MagicMock()
        patient.current_user = MagicMock(username="mario")
        self.data_fine = self.data_inizio
        res = self.call()
        self.assertEqual(res, "OK")
        attesa = datetime.strptime(self.data_inizio, "%Y-%m-%d").date()
        self.assertEqual(mock_Sintomi.call_args.kwargs["data_fine"], attesa)
        
if __name__ == "__main__":
    unittest.main()
