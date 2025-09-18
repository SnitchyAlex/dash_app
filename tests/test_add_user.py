# tests/test_add_user.py
import unittest
from unittest.mock import patch, MagicMock
from model.operations import add_user  

class TestAddUser(unittest.TestCase):

    def test_username_gia_esistente_ritorna_false(self):
        with patch("model.user.User") as User, \
             patch("model.medico.Medico"), \
             patch("model.paziente.Paziente"), \
             patch("model.operations.commit"):
            User.get.return_value = MagicMock()  # utente già presente

            ok = add_user("u1", "pwd", "Nome", "Cognome", role="paziente")
            self.assertFalse(ok)
            User.get.assert_called_once_with(username="u1")

    def test_crea_medico_success(self):
        with patch("model.user.User") as User, \
             patch("model.medico.Medico") as Medico, \
             patch("model.paziente.Paziente"), \
             patch("model.operations.commit") as commit, \
             patch("model.operations.generate_password_hash", return_value="HASH"):
            User.get.return_value = None

            ok = add_user("doc1", "pwd", "Doc", "House", role="medico", is_admin=True)
            self.assertTrue(ok)

            Medico.assert_called_once()
            kwargs = Medico.call_args.kwargs
            self.assertEqual(kwargs["username"], "doc1")
            self.assertEqual(kwargs["password_hash"], "HASH")
            self.assertEqual(kwargs["name"], "Doc")
            self.assertEqual(kwargs["surname"], "House")
            self.assertTrue(kwargs["is_admin"])
            commit.assert_called_once()
            User.assert_not_called()

    def test_crea_paziente_success(self):
        with patch("model.user.User") as User, \
             patch("model.medico.Medico"), \
             patch("model.paziente.Paziente") as Paziente, \
             patch("model.operations.commit") as commit, \
             patch("model.operations.generate_password_hash", return_value="HASH"):
            User.get.return_value = None

            ok = add_user("p1", "pwd", "Anna", "Rossi", role="paziente")
            self.assertTrue(ok)

            Paziente.assert_called_once()
            kwargs = Paziente.call_args.kwargs
            self.assertEqual(kwargs["username"], "p1")
            self.assertEqual(kwargs["password_hash"], "HASH")
            self.assertEqual(kwargs["name"], "Anna")
            self.assertEqual(kwargs["surname"], "Rossi")
            commit.assert_called_once()


    def test_eccezione_durante_creazione_ritorna_false(self):
        with patch("model.user.User") as User, \
             patch("model.medico.Medico"), \
             patch("model.paziente.Paziente") as Paziente, \
             patch("model.operations.commit") as commit, \
             patch("model.operations.generate_password_hash", return_value="HASH"):
            User.get.return_value = None
            Paziente.side_effect = RuntimeError("BOOM")

            ok = add_user("p_err", "pwd", "X", "Y", role="paziente")
            self.assertFalse(ok)
            commit.assert_not_called()

if __name__ == "__main__":
    unittest.main()
