from datetime import datetime
from pony.orm import Required, Optional, Set, PrimaryKey
from .database import db
from .paziente import Paziente

class Glicemia(db.Entity):
    """Entità per le misurazioni della glicemia"""
    paziente = Required(Paziente) # Relazione con paziente
    
    # Dati della misurazione
    valore = Required(float)  # mg/dL
    data_ora = Required(datetime)
    momento_pasto = Required(str)  # 'prima_pasto', 'dopo_pasto', 'digiuno'
    due_ore_pasto = Optional(bool)
    
    # Campi opzionali
    note = Optional(str)

    PrimaryKey(paziente, data_ora)
    