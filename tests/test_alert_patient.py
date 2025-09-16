#Funzioni da testare per verificare funzionamento alert corretto per il paziente
# tests/test_alerts_subset.py
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import types

import controller.patient as patient


class TestCheckPatientAlerts(unittest.TestCase):

    @patch("controller.patient._has_glicemia_today", return_value=False)
    @patch("controller.patient._has_active_therapies", return_value=False)
    @patch("controller.patient._has_assunzioni_today", return_value=False)
    @patch("controller.patient._check_therapy_alerts", return_value=[])
    def test_no_therapy_alerts_e_niente_assunzioni_terapie_attive_aggiunge_info_e_warning(
        self, mock_cta, mock_has_ass, mock_has_act, mock_has_glic
    ):
        paz = MagicMock()
        alerts = patient._check_patient_alerts(paz)
        types_ = [a["type"] for a in alerts]
        self.assertIn("info", types_)     # promemoria assunzioni giornaliere
        self.assertIn("warning", types_)  # promemoria glicemia mancante

    @patch("controller.patient._has_glicemia_today", return_value=True)
    @patch("controller.patient._has_active_therapies", return_value=False)
    @patch("controller.patient._has_assunzioni_today", return_value=False)
    @patch("controller.patient._check_therapy_alerts", return_value=[])
    def test_se_glicemia_presente_solo_info_niente_warning(self, *_mocks):
        paz = MagicMock()
        alerts = patient._check_patient_alerts(paz)
        self.assertTrue(any(a["type"] == "info" for a in alerts))
        self.assertFalse(any(a["type"] == "warning" for a in alerts))

    @patch("controller.patient._has_glicemia_today", return_value=False)
    @patch("controller.patient._check_therapy_alerts", return_value=[{"type": "danger"}])
    def test_con_therapy_alerts_niente_info_ma_warning_se_glicemia_mancante(
        self, mock_cta, mock_has_glic
    ):
        paz = MagicMock()
        alerts = patient._check_patient_alerts(paz)
        types_ = [a["type"] for a in alerts]
        self.assertIn("danger", types_)   # ereditato dai therapy alerts
        self.assertIn("warning", types_)  # aggiunto per glicemia mancante
        self.assertNotIn("info", types_)  # niente info quando therapy_alerts non è vuoto


class TestCheckTherapyAlerts(unittest.TestCase):

    @patch("controller.patient._get_active_therapies")
    @patch("controller.patient._get_assunzioni_today")
    def test_calcolo_mancanti_e_totali(self, mock_get_ass, mock_get_act):
        # nessuna assunzione fatta oggi
        mock_get_ass.return_value = []
        # terapia: Metformina 2 volte/die
        terapia = types.SimpleNamespace(
            nome_farmaco="Metformina",
            dosaggio_per_assunzione="500 mg",
            assunzioni_giornaliere=2,
            data_inizio=datetime.now(), data_fine=None
        )
        mock_get_act.return_value = [terapia]

        paz = MagicMock()
        alerts = patient._check_therapy_alerts(paz)
        self.assertEqual(len(alerts), 1)
        a = alerts[0]
        self.assertEqual(a["type"], "danger")
        self.assertEqual(a["farmaco"], "Metformina")
        self.assertEqual(a["mancanti"], 2)
        self.assertEqual(a["totali"], 2)

    @patch("controller.patient._get_active_therapies")
    @patch("controller.patient._get_assunzioni_today")
    def test_case_insensitive_su_nomi_farmaco(self, mock_get_ass, mock_get_act):
        # 1 assunzione fatta con nome in lower
        ass = types.SimpleNamespace(nome_farmaco="metformina")
        mock_get_ass.return_value = [ass]
        # terapia con nome mixed-case e 3/die
        terapia = types.SimpleNamespace(
            nome_farmaco="MetFormina",
            dosaggio_per_assunzione="500 mg",
            assunzioni_giornaliere=3,
            data_inizio=datetime.now(), data_fine=None
        )
        mock_get_act.return_value = [terapia]

        paz = MagicMock()
        alerts = patient._check_therapy_alerts(paz)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["mancanti"], 2)  # 3 richieste - 1 fatta

    @patch("controller.patient._get_active_therapies")
    @patch("controller.patient._get_assunzioni_today")
    def test_nessun_alert_se_coperte_tutte_le_assunzioni(self, mock_get_ass, mock_get_act):
        # 2 assunzioni fatte, 2 richieste (case-insensitive)
        a1 = types.SimpleNamespace(nome_farmaco="metformina")
        a2 = types.SimpleNamespace(nome_farmaco="Metformina")
        mock_get_ass.return_value = [a1, a2]
        terapia = types.SimpleNamespace(
            nome_farmaco="METFORMINA",
            dosaggio_per_assunzione="500 mg",
            assunzioni_giornaliere=2,
            data_inizio=datetime.now(), data_fine=None
        )
        mock_get_act.return_value = [terapia]

        paz = MagicMock()
        alerts = patient._check_therapy_alerts(paz)
        self.assertEqual(alerts, [])  # coperto => nessun alert

if __name__ == "__main__":
    unittest.main()
