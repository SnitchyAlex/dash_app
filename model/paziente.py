# model/paziente.py
from datetime import datetime
from pony.orm import Optional, Set
from .user import User

# Define the paziente entity
class Paziente(User):
    # Attributi specifici dei pazienti
    birth_date = Optional(datetime)
    eta = Optional(int)
    codice_fiscale = Optional(str)
    # Relazione many-to-many con i medici
    doctors = Set("Medico", reverse="patients")
    rilevazione = Set("Glicemia", reverse="paziente")
    assunzione = Set("Assunzione", reverse="paziente")