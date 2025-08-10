from .database import db, configure_db

# Configura il database per primo
db_path = configure_db()

# Solo se la configurazione è riuscita, procedi
if db_path is not None:
    # Poi importa tutte le entità
    from .user import User
    from .paziente import Paziente
    from .medico import Medico

    # Debug: stampa gli attributi delle entità
    print("=== Debug Entity Attributes ===")
    print(f"User attributes: {[attr.name for attr in User._attrs_]}")
    print(f"Paziente attributes: {[attr.name for attr in Paziente._attrs_]}")
    print(f"Medico attributes: {[attr.name for attr in Medico._attrs_]}")
    print("=== End Debug ===")

    # Ora genera il mapping e crea le tabelle
    try:
        db.generate_mapping(create_tables=True)
        print(f"Database tables created successfully at: {db_path}")
        
        # Infine inizializza i dati
        from .operations import initialize_db
        initialize_db()
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Database configuration failed, skipping table creation")

# Import delle funzioni di operations per renderle disponibili
from .operations import (
    assign_doctor_to_patient,
    remove_doctor_from_patient,
    get_patient_doctors,
    get_doctor_patients,
    get_patient_info,
    get_doctor_info
)

__all__ = [
    'db', 'User', 'Paziente', 'Medico',
    'assign_doctor_to_patient', 'remove_doctor_from_patient',
    'get_patient_doctors', 'get_doctor_patients',
    'get_patient_info', 'get_doctor_info'
]