# scripts/seed_test_aderenza.py
from datetime import datetime, timedelta
from pony.orm import db_session, commit,select
from model.medico import Medico
from model.paziente import Paziente
from model.terapia import Terapia
from model.assunzione import Assunzione

DEFAULT_FARMACO = "Metformina"

def _pick_by_username_or_first(entity_cls, username):
    if username:
        obj = entity_cls.get(username=username)
        if obj:
            return obj
    # fallback: primo disponibile
    try:
        return next(iter(entity_cls.select()))
    except StopIteration:
        return None

@db_session
def seed(m_username=None, p_username=None, farmaco=DEFAULT_FARMACO):
    m = _pick_by_username_or_first(Medico, m_username)
    p = _pick_by_username_or_first(Paziente, p_username)

    if not m or not p:
        print("❌ Nessun medico o paziente trovato nel DB.")
        print("Medici esistenti:", [x.username for x in Medico.select()])
        print("Pazienti esistenti:", [x.username for x in Paziente.select()])
        return

    # collega medico-paziente se serve
    if p not in m.patients:
        m.patients.add(p)
        commit()

    # crea una terapia attiva iniziata 5 giorni fa (senza data_fine)
    start_date = (datetime.now() - timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0)
    medico_nome = f"Dr. {m.name} {m.surname}"
    t = Terapia.get(medico_nome=medico_nome, paziente=p, nome_farmaco=farmaco, data_inizio=start_date)
    if not t:
        Terapia(
            medico=m,
            medico_nome=medico_nome,
            paziente=p,
            nome_farmaco=farmaco,
            dosaggio_per_assunzione="500mg",
            assunzioni_giornaliere=2,
            indicazioni="dopo i pasti",
            note="(test aderenza)",
            data_inizio=start_date,
            data_fine=None
        )
        commit()

    # pulisco eventuali assunzioni degli ultimi 3 giorni per forzare il “buco”
    today = datetime.now().date()
    from_dt = datetime.combine(today - timedelta(days=2), datetime.min.time())
    to_dt   = datetime.combine(today + timedelta(days=1), datetime.min.time())

    for a in p.assunzione:  # relazione Set("Assunzione") su Paziente
        if a.nome_farmaco == farmaco and from_dt <= a.data_ora < to_dt:
            a.delete()

    commit()

    print(f"✓ Seed completato. Medico: {m.username}, Paziente: {p.username}, Farmaco: {farmaco}")
    print("Apri la UI del medico e controlla gli alert di aderenza.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--medico", help="username medico", default=None)
    parser.add_argument("--paziente", help="username paziente", default=None)
    parser.add_argument("--farmaco", help="nome farmaco", default=DEFAULT_FARMACO)
    args = parser.parse_args()
    seed(args.medico, args.paziente, args.farmaco)
