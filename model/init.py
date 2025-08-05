from .database import db, configure_db

from .user import User
from .paziente import Paziente
from .medico import Medico

# Configurazione automatica all'import
configure_db()
db.generate_mapping(create_tables=True)

__all__ = ['db', 'User', 'Paziente', 'Medico']