from datetime import UTC, datetime, timedelta

from app.agent.scoring import is_excluded, location_match, score_job
from app.agent.sources.base import JobPosting, normalize, parse_datetime, strip_html

NOW = datetime(2026, 11, 27, 12, 0)


def job(**kw) -> JobPosting:
    base = {"source": "t", "external_id": "1", "url": "https://x", "title": "Analista", "description": ""}
    base.update(kw)
    return JobPosting(**base)


def test_sin_palabra_clave_es_cero():
    score, hits = score_job(job(title="Vendedor de seguros"), ["devops"], ["Chile"], now=NOW)
    assert score == 0 and hits == []


def test_palabra_en_titulo_pesa_mas_que_en_descripcion():
    in_title, _ = score_job(job(title="DevOps Engineer"), ["devops"], [], now=NOW)
    in_body, _ = score_job(job(title="Engineer", description="trabajo devops"), ["devops"], [], now=NOW)
    assert in_title > in_body > 0


def test_tildes_y_mayusculas_no_importan():
    score, hits = score_job(job(title="Ingeniero de INFRAESTRUCTURA"), ["infraestructura"], [], now=NOW)
    assert score > 0 and hits == ["infraestructura"]
    assert normalize("Configuración ÉRP") == "configuracion erp"


def test_palabra_corta_requiere_palabra_completa():
    # "qa" no debe calzar dentro de "aquarium"
    assert score_job(job(title="Aquarium keeper"), ["qa"], [], now=NOW)[0] == 0
    assert score_job(job(title="QA Engineer"), ["qa"], [], now=NOW)[0] > 0


def test_bonos_ubicacion_recencia_y_sueldo():
    base = job(title="Soporte TI", country="Chile", location="Santiago")
    bare, _ = score_job(base, ["soporte"], ["España"], now=NOW)
    located, _ = score_job(base, ["soporte"], ["Chile"], now=NOW)
    fresh = job(title="Soporte TI", published_at=NOW - timedelta(days=1), salary_min=1000)
    fresh_score, _ = score_job(fresh, ["soporte"], ["España"], now=NOW)
    assert located == bare + 20
    assert fresh_score == bare + 10 + 5


def test_remoto_y_tope_100():
    j = job(title="DevOps SRE Cloud Python QA", remote=True, published_at=NOW, salary_max=1)
    score, hits = score_job(j, ["devops", "sre", "cloud", "python", "qa"], ["Remoto"], now=NOW)
    assert score == 100 and len(hits) == 5
    assert location_match(job(title="x", remote=True), ["Remoto"])
    assert not location_match(job(title="x", remote=False, location="Lima"), ["Remoto", "Chile"])


def test_exclusion():
    assert is_excluded(job(title="Practicante de soporte"), ["practicante"])
    assert not is_excluded(job(title="Soporte N2"), ["practicante", ""])


def test_utilidades():
    assert strip_html("<p>Hola&nbsp;<b>mundo</b></p>") == "Hola mundo"
    assert parse_datetime(0) is None
    assert parse_datetime("2026-11-01T10:00:00Z") == datetime(2026, 11, 1, 10, 0)
    assert parse_datetime("2026-11-01 10:00:00") == datetime(2026, 11, 1, 10, 0)
    assert parse_datetime(datetime(2026, 1, 1, tzinfo=UTC).timestamp()) == datetime(2026, 1, 1)
    assert parse_datetime("no es fecha") is None
