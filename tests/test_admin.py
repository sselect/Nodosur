import asyncio

from app.agent import runner
from app.config import Settings


def seed(db, mock_client):
    return asyncio.run(runner.run_agent(db, client=mock_client(), force=True))


def test_panel_requiere_login(client):
    r = client.get("/admin", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/admin/login"
    assert client.get("/admin/api/stats").status_code == 401


def test_login_incorrecto_y_limite(client):
    bad = {"email": "admin@nodosur.cl", "password": "mala"}
    codes = [client.post("/admin/login", data=bad).status_code for _ in range(6)]
    assert codes[:5] == [401] * 5 and codes[5] == 429


def test_login_y_dashboard(admin):
    r = admin.get("/admin")
    assert r.status_code == 200 and "Ejecutar ahora" in r.text


def test_stats_y_listado(admin, db, mock_client):
    result = seed(db, mock_client)
    stats = admin.get("/admin/api/stats").json()
    assert stats["total"] == result.new_jobs > 0
    assert len(stats["by_day"]) == 14 and sum(d["count"] for d in stats["by_day"]) == stats["total"]
    assert sum(stats["score_buckets"].values()) == stats["total"]
    assert {s["name"] for s in stats["sources"]} >= {"getonboard", "remotive"}

    jobs = admin.get("/admin/api/jobs", params={"sort": "score"}).json()
    assert jobs["total"] == stats["total"]
    scores = [j["score"] for j in jobs["items"]]
    assert scores == sorted(scores, reverse=True)
    remote_only = admin.get("/admin/api/jobs", params={"remote": "1"}).json()
    assert all(j["remote"] for j in remote_only["items"])
    found = admin.get("/admin/api/jobs", params={"q": "andes"}).json()
    assert found["total"] == 1

    csv = admin.get("/admin/api/jobs.csv")
    assert csv.status_code == 200 and "titulo" in csv.text.splitlines()[0]


def test_prospectos(admin, db, mock_client):
    seed(db, mock_client)
    companies = {c["company"] for c in admin.get("/admin/api/companies").json()}
    assert "Retail Sur S.A." in companies  # publica "Soporte TI N2"


def test_cambio_de_estado_exige_cabecera(admin, db, mock_client):
    seed(db, mock_client)
    job_id = admin.get("/admin/api/jobs").json()["items"][0]["id"]
    no_header = admin.patch(f"/admin/api/jobs/{job_id}", json={"status": "saved"}, headers={"X-NodoSur": ""})
    assert no_header.status_code == 403
    ok = admin.patch(f"/admin/api/jobs/{job_id}", json={"status": "applied"})
    assert ok.status_code == 200 and ok.json()["status"] == "applied"
    assert admin.patch(f"/admin/api/jobs/{job_id}", json={"status": "inventado"}).status_code == 422
    assert admin.patch("/admin/api/jobs/99999", json={"status": "saved"}).status_code == 404


def test_configuracion_del_agente(admin):
    cfg = admin.get("/admin/api/config").json()
    cfg.update(keywords=[" Oracle ", "oracle", "QA"], interval_minutes=30, sources=["getonboard"])
    cfg.pop("updated_at")
    saved = admin.put("/admin/api/config", json=cfg).json()
    assert saved["keywords"] == ["Oracle", "QA"]  # sin espacios ni duplicados
    assert saved["interval_minutes"] == 30
    bad = dict(cfg, sources=["linkedin-scraper"])
    assert admin.put("/admin/api/config", json=bad).status_code == 422
    assert admin.put("/admin/api/config", json=dict(cfg, interval_minutes=1)).status_code == 422
    assert admin.put("/admin/api/config", json=dict(cfg, keywords=[])).status_code == 422


def test_ejecucion_manual_y_historial(admin, monkeypatch):
    called = {}

    async def fake_run(db, trigger="manual", force=False, client=None):
        called.update(trigger=trigger, force=force)

    monkeypatch.setattr("app.routers.admin.run_agent", fake_run)
    r = admin.post("/admin/api/run")
    assert r.status_code == 200 and called == {"trigger": "manual", "force": True}
    assert admin.get("/admin/api/runs").status_code == 200


def test_leads_en_panel(admin, client):
    client.post("/api/contact", json={"name": "Luis", "email": "luis@empresa.cl", "kind": "erp_demo"})
    leads = admin.get("/admin/api/leads").json()
    assert leads[0]["kind"] == "erp_demo"
    upd = admin.patch(f"/admin/api/leads/{leads[0]['id']}", json={"status": "contacted"})
    assert upd.json()["status"] == "contacted"
    assert admin.get("/admin/api/stats").json()["new_leads"] == 0


def test_disparador_cron_con_token(client, monkeypatch):
    async def fake_run(db, trigger="manual", force=False, client=None):
        from app.models import AgentRun

        return AgentRun(trigger=trigger, status="skipped", message="test")

    monkeypatch.setattr("app.routers.agent_api.run_agent", fake_run)
    assert client.post("/api/agent/run").status_code == 401
    assert client.post("/api/agent/run", headers={"Authorization": "Bearer malo"}).status_code == 401
    ok = client.post("/api/agent/run", headers={"Authorization": "Bearer token-de-prueba-123"})
    assert ok.status_code == 200 and ok.json()["trigger"] == "cron"


def test_config_segura_en_prod():
    import pytest

    weak = Settings(env="prod", secret_key="dev-secret-change-me", admin_password="admin", agent_token="x")
    with pytest.raises(RuntimeError):
        weak.validate_for_prod()
    strong = Settings(env="prod", secret_key="s" * 32, admin_password="p" * 16, agent_token="t" * 32)
    strong.validate_for_prod()
    assert Settings(database_url="postgres://u:p@h/db").sqlalchemy_url == "postgresql+psycopg://u:p@h/db"
