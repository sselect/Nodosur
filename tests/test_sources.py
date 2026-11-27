import asyncio

import httpx
import pytest

from app.agent.sources import REGISTRY
from app.agent.sources.getonboard import GetOnBoardSource
from app.agent.sources.remote_boards import (
    ArbeitnowSource,
    HimalayasSource,
    JobicySource,
    RemoteOKSource,
    RemotiveSource,
)
from tests import payloads
from tests.conftest import make_transport


def test_getonboard_parse():
    jobs = GetOnBoardSource.parse(payloads.getonboard())
    devops = jobs[0]
    assert devops.title == "DevOps Engineer (AWS/OCI)"
    assert devops.company == "Andes Cloud SpA"
    assert devops.remote is True and devops.modality == "Remoto"
    assert devops.country == "Chile"
    assert devops.url.startswith("https://www.getonbrd.com/jobs/")
    assert devops.salary_min == 2500 and devops.currency == "USD"
    assert "<" not in devops.description
    assert jobs[1].modality == "Híbrido" and jobs[1].remote is False


def test_remoteok_ignora_aviso_legal():
    jobs = RemoteOKSource.parse(payloads.remoteok())
    assert len(jobs) == 2
    assert jobs[0].title == "Cloud Support Engineer" and jobs[0].salary_max == 80000


@pytest.mark.parametrize(
    "source,payload,title",
    [
        (RemotiveSource, payloads.remotive(), "Senior SRE"),
        (ArbeitnowSource, payloads.arbeitnow(), "QA Automation Engineer"),
        (HimalayasSource, payloads.himalayas(), "ERP Consultant (Oracle Cloud)"),
        (JobicySource, payloads.jobicy(), "Infrastructure Engineer & SRE"),
    ],
)
def test_parsers_remotos(source, payload, title):
    jobs = source.parse(payload)
    assert jobs[0].title == title
    assert jobs[0].url.startswith("https://")
    assert jobs[0].published_at is not None


def test_parsers_toleran_payload_vacio():
    for source in REGISTRY.values():
        assert source.parse({} if source.name != "remoteok" else []) == []


def test_fetch_con_transporte_simulado():
    async def go():
        async with httpx.AsyncClient(transport=make_transport()) as client:
            results = {}
            for name, source in REGISTRY.items():
                results[name] = await source.fetch(client, ["devops", "soporte"])
            return results

    results = asyncio.run(go())
    assert all(results[name] for name in REGISTRY), results
    # Get on Board consulta una vez por palabra clave y deduplica por id
    assert len({j.external_id for j in results["getonboard"]}) == len(results["getonboard"])


def test_respeto_de_limites_de_api():
    assert REGISTRY["remotive"].min_interval_minutes >= 360  # máx. 4 consultas/día
    assert all(s.min_interval_minutes >= 30 for s in REGISTRY.values())
