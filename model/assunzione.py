from datetime import datetime
from pony.orm import Required, Optional, Set, PrimaryKey
from .database import db
from .paziente import Paziente

class Assunzione(db.Entity):
    """Entità per le assunzioni di farmaci"""
    paziente = Required(Paziente)  # Relazione con paziente
    
    # Dati dell'assunzione
    nome_farmaco = Required(str)
    dosaggio = Required(str)
    data_ora = Required(datetime)
    
    # Campi opzionali
    note = Optional(str)

    PrimaryKey(paziente, data_ora, nome_farmaco)  # Chiave composta per permettere più farmaci alla stessa data/ora