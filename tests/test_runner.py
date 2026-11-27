import asyncio
from datetime import timedelta

from sqlalchemy import func, select

from app.agent import runner
from app.events import bus
from app.models import AgentRun, Job, SourceState, utcnow


def run(db, client, **kw):
    return asyncio.run(runner.run_agent(db, client=client, **kw))


def test_ejecucion_completa_guarda_filtra_y_deduplica(db, mock_client):
    queue = bus.subscribe()
    result = run(db, mock_client(), trigger="manual", force=True)
    assert result.status == "ok"
    titles = set(db.scalars(select(Job.title)).all())
    # Coincidencias esperadas con las palabras clave por defecto
    assert "DevOps Engineer (AWS/OCI)" in titles
    assert "Analista de Soporte TI N2" in titles
    assert "Senior SRE" in titles
    # Excluidas: practicante (palabra excluida), aviso de 60 días (antigüedad), frontend (sin keyword)
    assert "Practicante de Soporte" not in titles
    assert "Consultor Oracle Fusion SCM" not in titles
    assert "Frontend Engineer (React)" not in titles
    # El DevOps de Andes Cloud aparece en 2 fuentes y se guarda una sola vez
    assert db.scalar(select(func.count(Job.id)).where(Job.company == "Andes Cloud SpA")) == 1
    assert result.new_jobs == db.scalar(select(func.count(Job.id)))
    events = []
    while not queue.empty():
        events.append(queue.get_nowait()["event"])
    bus.unsubscribe(queue)
    assert events[0] == "run_started" and events[-1] == "run_finished"
    assert events.count("job_new") == result.new_jobs


def test_segunda_ejecucion_no_duplica(db, mock_client):
    first = run(db, mock_client(), force=True)
    second = run(db, mock_client(), force=True)
    assert first.new_jobs > 0
    assert second.new_jobs == 0


def test_respeta_intervalo_y_pausa(db, mock_client):
    run(db, mock_client(), force=True)
    skipped = run(db, mock_client(), trigger="cron")
    assert skipped.status == "skipped" and "intervalo" in skipped.message
    cfg = runner.get_config(db)
    cfg.active = False
    db.commit()
    paused = run(db, mock_client(), trigger="cron")
    assert paused.status == "skipped" and "pausado" in paused.message


def test_vuelve_a_correr_cuando_pasa_el_intervalo(db, mock_client):
    run(db, mock_client(), force=True)
    last = db.scalars(select(AgentRun)).first()
    last.started_at = utcnow() - timedelta(hours=3)
    db.commit()
    assert runner.is_due(db, runner.get_config(db))


def test_fuente_caida_deja_estado_parcial(db, mock_client):
    result = run(db, mock_client(fail={"remoteok.com"}), force=True)
    assert result.status == "partial"
    assert result.per_source["remoteok"]["status"] == "error"
    state = db.get(SourceState, "remoteok")
    assert state.last_status == "error" and "HTTPStatusError" in state.last_error
    assert result.new_jobs > 0  # las demás fuentes siguen funcionando


def test_remotive_no_se_consulta_dos_veces_en_6_horas(db, mock_client):
    calls: list = []
    run(db, mock_client(calls=calls), force=True)
    assert "remotive.com" in calls
    calls.clear()
    run(db, mock_client(calls=calls), force=True)
    assert "remotive.com" not in calls


def test_notifica_por_correo_las_mejores(db, mock_client, monkeypatch):
    sent = {}

    async def fake_send(to, subject, html_body, text_body):
        sent.update(to=to, subject=subject, html=html_body)
        return True

    monkeypatch.setattr(runner, "send_email", fake_send)
    cfg = runner.get_config(db)
    cfg.notify_email = "ely@example.com"
    cfg.notify_min_score = 50
    db.commit()
    result = run(db, mock_client(), force=True)
    assert result.notified > 0
    assert sent["to"] == "ely@example.com" and "nuevas ofertas" in sent["subject"]
    assert db.scalar(select(func.count(Job.id)).where(Job.notified.is_(True))) == result.notified


def test_sin_smtp_no_marca_notificadas(db, mock_client):
    result = run(db, mock_client(), force=True)
    assert result.notified == 0
