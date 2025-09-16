#Funzioni test per verificare salvataggio della terapia 
import unittest
from unittest.mock import MagicMock, patch
import controller.doctor as doctor  # alias richiesto


class SaveTerapiaCoreTest(unittest.TestCase):

    @patch("controller.doctor.Terapia")
    @patch("controller.doctor.Paziente")
    def test_successo(self, MockPaziente, MockTerapia):
        # medico e paziente finti
        medico = MagicMock()
        medico.name = "Mario"
        medico.surname = "Rossi"

        paziente = MagicMock()
        paziente.name = "Anna"
        paziente.surname = "Bianchi"
        paziente.doctors = set()  # set reale per l'operazione .add()

        MockPaziente.get.return_value = paziente
        MockTerapia.return_value = MagicMock()

        # chiamata alla core
        result = doctor.save_terapia_core(
            1,                           # n_clicks
            "anna",                      # paziente_id
            "Metformina",                # nome_farmaco
            "500mg",                     # dosaggio
            2,                           # assunzioni_giornaliere
            "mattina",                   # indicazioni_select -> STRINGA, non lista!
            "2025-09-01",                # data_inizio
            None,                        # data_fine
            "note di test",              # note
            get_current_medico_func=lambda: medico
        )

        # l'output è un dbc.Alert: controllo sul testo nei children
        text = str(getattr(result, "children", result))
        self.assertIn("metformina", text.lower())
        # il medico è stato associato al paziente
        self.assertIn(medico, paziente.doctors)

    @patch("controller.doctor.Paziente")
    def test_paziente_non_trovato(self, MockPaziente):
        # nessun paziente trovato
        MockPaziente.get.return_value = None

        medico = MagicMock()
        medico.name = "Mario"
        medico.surname = "Rossi"

        result = doctor.save_terapia_core(
            1,
            "sconosciuto",
            "Farmaco",
            "10mg",
            1,
            "",                 # indicazioni vuote OK
            "2025-09-01",
            None,
            "",
            get_current_medico_func=lambda: medico
        )

        # anche qui l'output è un dbc.Alert
        text = str(getattr(result, "children", result))
        self.assertIn("paziente non trovato", text.lower())


if __name__ == "__main__":
    unittest.main()
