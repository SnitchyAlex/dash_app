#Funzione per salvare i dati clinici aggiornati del paziente
import unittest
from unittest.mock import MagicMock, patch
import controller.doctor as doctor


class SavePatientDataModificationsCoreTest(unittest.TestCase):

    @patch("controller.doctor.Paziente")
    def test_medico_non_trovato(self, MockPaziente):
        result = doctor.save_patient_data_modifications_core(
            "anna",
            "fumo",
            "asma",
            "ipertensione",
            get_current_medico_func=lambda: None  # medico mancante
        )

        text = str(getattr(result, "children", result))
        self.assertIn("medico non trovato", text.lower())

    @patch("controller.doctor.Paziente")
    def test_paziente_non_trovato(self, MockPaziente):
        medico = MagicMock()
        medico.name = "Mario"
        medico.surname = "Rossi"

        MockPaziente.get.return_value = None  # paziente inesistente

        result = doctor.save_patient_data_modifications_core(
            "sconosciuto",
            "fumo",
            "asma",
            "ipertensione",
            get_current_medico_func=lambda: medico
        )

        text = str(getattr(result, "children", result))
        self.assertIn("paziente non trovato", text.lower())

    @patch("controller.doctor.get_patient_data_update_success_message", return_value="SUCCESSO_OK")
    @patch("controller.doctor.check_medico_paziente_authorization", return_value=None)
    @patch("controller.doctor.Paziente")
    def test_successo(self, MockPaziente, mock_check, mock_success_msg):
        medico = MagicMock()
        medico.name = "Mario"
        medico.surname = "Rossi"

        paziente = MagicMock()
        paziente.username = "anna"
        paziente.name = "Anna"
        paziente.surname = "Bianchi"
        MockPaziente.get.return_value = paziente

        result = doctor.save_patient_data_modifications_core(
            "anna",
            "fumo",
            "asma",
            "ipertensione",
            get_current_medico_func=lambda: medico
        )

        # deve aggiornare i campi del paziente
        self.assertEqual(paziente.fattori_rischio, "fumo")
        self.assertEqual(paziente.pregresse_patologie, "asma")
        self.assertEqual(paziente.comorbidita, "ipertensione")
        self.assertIn("Dr. Mario Rossi", paziente.info_aggiornate)

        # deve restituire il messaggio di successo mockato
        self.assertEqual(result, "SUCCESSO_OK")


if __name__ == "__main__":
    unittest.main()
