# model/medico.py
from pony.orm import Optional, Set, Required
from .user import User

# Define the medico entity
class Medico(User):
    # Attributi specifici dei medici
    specializzazione = Optional(str)
    email = Required(str, unique=True)
    
    # Relazione many-to-many con i pazienti
    pazienti_riferimento = Set("Paziente", reverse="medico_riferimento")
    patients = Set("Paziente", reverse="doctors")
    terapies = Set("Terapia", reverse="medico")