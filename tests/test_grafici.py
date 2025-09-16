#test grafici paziente,simili a medico
# tests/test_grafici.py
import unittest
from datetime import datetime, timedelta
import pandas as pd
import controller.patient as patient
import plotly.graph_objects as go

class TestGraficiPatient(unittest.TestCase):

    def _df_week_current(self):
        """DataFrame con un punto per ogni giorno della settimana corrente."""
        now = datetime.now()
        start_week = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        dates = [start_week + timedelta(days=i, hours=8) for i in range(7)]
        values = [90, 110, 130, 150, 120, 100, 140]
        df = pd.DataFrame({"data": dates, "valore": values}).sort_values("data")
        df["data"] = pd.to_datetime(df["data"])
        df.set_index("data", inplace=True)
        return df

    def _df_last_weeks(self, weeks=10, points_per_week=2):
        """DataFrame negli ultimi 'weeks' con più punti a settimana."""
        now = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        dates = []
        values = []
        for w in range(weeks):
            base = now - timedelta(weeks=w)
            for k in range(points_per_week):
                dates.append(base - timedelta(days=k*2))
                values.append(100 + ((w + k) % 5) * 10)
        df = pd.DataFrame({"data": dates, "valore": values})
        df["data"] = pd.to_datetime(df["data"])
        df = df.sort_values("data")
        df.set_index("data", inplace=True)
        return df

    def _df_current_year_months(self):
        """DataFrame con punti in 3 mesi dell'anno corrente."""
        year = datetime.now().year
        dates = [
            datetime(year, 1, 10, 8), datetime(year, 2, 12, 8),
            datetime(year, 6, 5, 8), datetime(year, 6, 20, 8)
        ]
        values = [100, 110, 120, 130]
        df = pd.DataFrame({"data": dates, "valore": values})
        df["data"] = pd.to_datetime(df["data"])
        df = df.sort_values("data")
        df.set_index("data", inplace=True)
        return df

    # --- DataFrame helper ----------------------------------------------------

    def test_create_glicemia_dataframe(self):
        # usa la helper per creare il df da oggetti fittizi
        class G:  # finta entity
            def __init__(self, ts, v): self.data_ora, self.valore = ts, v
        now = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        glicemie = [G(now - timedelta(days=1), 110), G(now - timedelta(days=2), 100)]
        df = patient._create_glicemia_dataframe(glicemie)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.index.is_monotonic_increasing)
        self.assertIn("valore", df.columns)  # come serie

    # --- Empty figures -------------------------------------------------------

    def test_create_empty_figures_message(self):
        f1, f2, f3 = patient._create_empty_figures("Nessun dato")
        for f in (f1, f2, f3):
            self.assertIsInstance(f, go.Figure)
            # y-range fissata 0..300
            self.assertEqual(f.layout.yaxis.range, (0, 300))
            # deve avere un'annotazione col messaggio
            anns = f.layout.annotations or []
            self.assertTrue(any("Nessun dato" in (a.text or "") for a in anns))

    # --- Weekly DOW ----------------------------------------------------------

    def test_weekly_dow_chart_has_mean_and_thresholds(self):
        df = self._df_week_current()
        fig = patient._create_weekly_dow_chart(df)
        self.assertIsInstance(fig, go.Figure)
        # mean + 3 tracce soglie (alto + 2 per fascia riempita) => almeno 4
        self.assertGreaterEqual(len(fig.data), 4)
        # asse Y 0..300
        self.assertEqual(fig.layout.yaxis.range, (0, 300))

    # --- Weekly average ------------------------------------------------------

    def test_weekly_avg_chart_non_empty_within_window(self):
        df = self._df_last_weeks(weeks=6, points_per_week=3)
        fig = patient._create_weekly_avg_chart(df, weeks_window=8)  # finestra più larga dei dati
        self.assertIsInstance(fig, go.Figure)
        # almeno una traccia (la serie delle medie settimanali)
        self.assertGreaterEqual(len(fig.data), 1)
        # niente messaggio “nessuna settimana...”
        anns = fig.layout.annotations or []
        self.assertFalse(any("Nessuna settimana" in (a.text or "") for a in anns))

    # --- Monthly average -----------------------------------------------------

    def test_monthly_avg_chart_12_points_axis(self):
        df = self._df_current_year_months()
        fig = patient._create_monthly_avg_chart(df)
        self.assertIsInstance(fig, go.Figure)

    # deve esserci almeno la serie mensile + 3 soglie
        self.assertGreaterEqual(len(fig.data), 4)

    # la prima traccia è la media mensile dell'anno corrente
        year = datetime.now().year
        self.assertEqual(getattr(fig.data[0], "name", ""), f"Media mensile {year}")
        self.assertEqual(len(fig.data[0].x), 12)

    # presenza della soglia alta 180 mg/dL
        names = [getattr(t, "name", "") for t in fig.data]
        self.assertIn("Glicemia superiore a 180", names)

    # range Y fissato
        self.assertEqual(fig.layout.yaxis.range, (0, 300))


if __name__ == "__main__":
    unittest.main()
