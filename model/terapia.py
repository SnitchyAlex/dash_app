# model/terapia.py
from datetime import datetime
from pony.orm import Required, Optional, Set, PrimaryKey
from .database import db
from .medico import Medico
from .paziente import Paziente

class Terapia(db.Entity):
    """Entità per le terapie prescritte dai medici ai pazienti"""
    medico = Optional(Medico)  # Medico che prescrive la terapia optional per poter cancellare il medico e non la terapia
    paziente = Required(Paziente)  # Paziente a cui è assegnata la terapia
    
    # Dati del farmaco
    nome_farmaco = Required(str)
    dosaggio_per_assunzione = Required(str)  # es. "500mg", "1 compressa"
    assunzioni_giornaliere = Required(int)  # numero di volte al giorno
    medico_nome = Required(str)
    modificata = Optional(str)   # Nome dell'ultimo medico che ha modificato la terapia
    
    # Indicazioni e note
    indicazioni = Optional(str)  # es. "dopo i pasti", "lontano dai pasti"
    note = Optional(str)
    
    # Date
    data_inizio = Required(datetime)  # quando iniziare la terapia
    data_fine = Optional(datetime)  # quando terminare (se applicabile)
    
    PrimaryKey(medico_nome, paziente, nome_farmaco, data_inizio)