"""Respuestas de ejemplo con el formato real de cada API pública (fechas relativas a hoy)."""

from datetime import UTC, datetime, timedelta


def _now() -> datetime:
    return datetime.now(UTC)


def getonboard() -> dict:
    ts = int((_now() - timedelta(days=1)).timestamp())
    old = int((_now() - timedelta(days=60)).timestamp())
    return {
        "data": [
            {
                "id": "devops-engineer-andes-cloud-santiago",
                "type": "job",
                "attributes": {
                    "title": "DevOps Engineer (AWS/OCI)",
                    "description": "<p>Buscamos <strong>DevOps</strong> con experiencia en cloud y Python.</p>",
                    "functions": "<ul><li>Pipelines CI/CD</li></ul>",
                    "desirable": "Oracle Cloud Infrastructure",
                    "remote": True,
                    "remote_modality": "fully_remote",
                    "countries": ["Chile"],
                    "category_name": "SysAdmin / DevOps / QA",
                    "seniority_name": "Semi Senior",
                    "min_salary": 2500,
                    "max_salary": 3500,
                    "published_at": ts,
                    "company": {
                        "data": {"id": "andes-cloud", "type": "company", "attributes": {"name": "Andes Cloud SpA"}}
                    },
                },
                "links": {"public_url": "https://www.getonbrd.com/jobs/devops-engineer-andes-cloud-santiago"},
            },
            {
                "id": "soporte-ti-n2-retail",
                "type": "job",
                "attributes": {
                    "title": "Analista de Soporte TI N2",
                    "description": "Mesa de ayuda, Active Directory y redes.",
                    "remote": False,
                    "remote_modality": "hybrid",
                    "countries": ["Chile"],
                    "category_name": "SysAdmin / DevOps / QA",
                    "published_at": ts,
                    "company": {"data": {"attributes": {"name": "Retail Sur S.A."}}},
                },
                "links": {"public_url": "https://www.getonbrd.com/jobs/soporte-ti-n2-retail"},
            },
            {
                "id": "practicante-soporte",
                "type": "job",
                "attributes": {
                    "title": "Practicante de Soporte",
                    "description": "Práctica profesional",
                    "remote": False,
                    "countries": ["Chile"],
                    "published_at": ts,
                    "company": {"data": {"attributes": {"name": "Retail Sur S.A."}}},
                },
                "links": {"public_url": "https://www.getonbrd.com/jobs/practicante-soporte"},
            },
            {
                "id": "oracle-fusion-old",
                "type": "job",
                "attributes": {
                    "title": "Consultor Oracle Fusion SCM",
                    "description": "Proyecto antiguo",
                    "remote": True,
                    "countries": ["Chile"],
                    "published_at": old,
                    "company": {"data": {"attributes": {"name": "Consultora X"}}},
                },
                "links": {"public_url": "https://www.getonbrd.com/jobs/oracle-fusion-old"},
            },
        ],
        "meta": {"page": 1, "total_pages": 1},
    }


def remotive() -> dict:
    return {
        "job-count": 2,
        "jobs": [
            {
                "id": 2090910,
                "url": "https://remotive.com/remote-jobs/software-dev/senior-sre-2090910",
                "title": "Senior SRE",
                "company_name": "Globex",
                "tags": ["kubernetes", "python", "sre"],
                "candidate_required_location": "LatAm",
                "publication_date": (_now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S"),
                "description": "<p>Site reliability for our cloud platform.</p>",
            },
            {
                "id": 2090911,
                "url": "https://remotive.com/remote-jobs/software-dev/frontend-2090911",
                "title": "Frontend Engineer (React)",
                "company_name": "Initech",
                "tags": ["react"],
                "candidate_required_location": "USA only",
                "publication_date": (_now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S"),
                "description": "<p>UI work</p>",
            },
        ],
    }


def remoteok() -> list:
    return [
        {"last_updated": 1700000000, "legal": "Please link back to Remote OK and mention it as a source."},
        {
            "id": "1129876",
            "epoch": int((_now() - timedelta(hours=5)).timestamp()),
            "company": "Hooli",
            "position": "Cloud Support Engineer",
            "tags": ["cloud", "support", "aws"],
            "location": "Worldwide",
            "salary_min": 60000,
            "salary_max": 80000,
            "url": "https://remoteok.com/remote-jobs/1129876",
            "description": "Help customers with cloud infrastructure.",
        },
        # Mismo aviso que en Get on Board, publicado por otra fuente (debe deduplicarse por huella)
        {
            "id": "1129877",
            "epoch": int((_now() - timedelta(hours=5)).timestamp()),
            "company": "Andes Cloud SpA",
            "position": "DevOps Engineer (AWS/OCI)",
            "tags": ["devops"],
            "location": "Remote",
            "url": "https://remoteok.com/remote-jobs/1129877",
            "description": "duplicate",
        },
    ]


def arbeitnow() -> dict:
    return {
        "data": [
            {
                "slug": "qa-engineer-berlin-123",
                "company_name": "Umbrella GmbH",
                "title": "QA Automation Engineer",
                "description": "<p>Testautomatisierung mit Python.</p>",
                "remote": True,
                "url": "https://www.arbeitnow.com/jobs/companies/umbrella/qa-engineer-berlin-123",
                "tags": ["QA", "Python"],
                "location": "Berlin",
                "created_at": int((_now() - timedelta(days=3)).timestamp()),
            }
        ],
        "links": {},
        "meta": {},
    }


def himalayas() -> dict:
    return {
        "jobs": [
            {
                "title": "ERP Consultant (Oracle Cloud)",
                "excerpt": "Implement Oracle Fusion ERP modules for clients.",
                "companyName": "Stark Industries",
                "locationRestrictions": ["Spain", "Chile"],
                "categories": ["ERP", "Consulting"],
                "minSalary": 50000,
                "maxSalary": 70000,
                "currency": "USD",
                "pubDate": int((_now() - timedelta(days=1)).timestamp()),
                "applicationLink": "https://himalayas.app/companies/stark/jobs/erp-consultant",
                "guid": "https://himalayas.app/companies/stark/jobs/erp-consultant",
            }
        ]
    }


def jobicy() -> dict:
    return {
        "jobs": [
            {
                "id": 98765,
                "url": "https://jobicy.com/jobs/98765-infra-engineer",
                "jobTitle": "Infrastructure Engineer &amp; SRE",
                "companyName": "Wayne Enterprises",
                "jobIndustry": ["DevOps &amp; Sysadmin"],
                "jobGeo": "LATAM",
                "jobExcerpt": "Terraform, cloud, on-call.",
                "pubDate": (_now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            }
        ]
    }


ROUTES = {
    "www.getonbrd.com": getonboard,
    "remotive.com": remotive,
    "remoteok.com": remoteok,
    "www.arbeitnow.com": arbeitnow,
    "himalayas.app": himalayas,
    "jobicy.com": jobicy,
}
