from datetime import datetime, date
from pony.orm import Required, Optional, Set, PrimaryKey
from .database import db
from .paziente import Paziente

class Sintomi(db.Entity):
    """Entità per sintomi, patologie e trattamenti concomitanti"""
    paziente = Required(Paziente)  # Relazione con paziente
    
    # Dati del sintomo/patologia/trattamento
    tipo = Required(str)  # 'sintomo', 'patologia', 'trattamento'
    descrizione = Required(str)  # Nome/descrizione del sintomo/patologia/trattamento
    
    # Periodo di manifestazione/durata
    data_inizio = Required(date)
    data_fine = Optional(date)  # Se None, è ancora in corso
    
    # Frequenza (per sintomi)
    frequenza = Optional(str)  # 'occasionale', 'frequente', 'continuo'
    
    # Campi opzionali
    note = Optional(str)

    PrimaryKey(paziente, tipo, descrizione, data_inizio)  # Chiave composta