# model/paziente.py
from datetime import datetime
from pony.orm import Optional, Set, Required
from .user import User

# Define the paziente entity
class Paziente(User):
    # Attributi specifici dei pazienti
    birth_date = Optional(datetime)
    eta = Optional(int)
    codice_fiscale = Optional(str)

    # Dati clinici
    fattori_rischio = Optional(str)
    pregresse_patologie = Optional(str) 
    comorbidita = Optional(str)
    info_aggiornate = Optional(str)

    # Relazione many-to-many con i medici
    medico_riferimento = Optional("Medico", reverse="pazienti_riferimento")
    doctors = Set("Medico", reverse="patients")
    rilevazione = Set("Glicemia", reverse="paziente")
    assunzione = Set("Assunzione", reverse="paziente")
    sintomi = Set("Sintomi", reverse="paziente")
    terapies = Set("Terapia", reverse="paziente")