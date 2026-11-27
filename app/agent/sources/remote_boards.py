"""Portales remotos internacionales con API pública oficial.

Términos respetados:
- Remotive: máx. ~4 consultas al día y enlace de atribución al aviso.
- Remote OK: el primer elemento es el aviso legal; exige enlace de vuelta y mencionar la fuente.
- Arbeitnow, Himalayas, Jobicy: APIs públicas gratuitas con atribución.
"""

import httpx

from app.agent.sources.base import (
    USER_AGENT,
    JobPosting,
    JobSource,
    parse_datetime,
    strip_html,
    to_float,
)


class RemotiveSource(JobSource):
    name = "remotive"
    label = "Remotive"
    homepage = "https://remotive.com"
    min_interval_minutes = 360  # 4 veces al día

    async def fetch(self, client: httpx.AsyncClient, keywords: list[str]) -> list[JobPosting]:
        resp = await client.get("https://remotive.com/api/remote-jobs", params={"category": "software-dev"})
        resp.raise_for_status()
        return self.parse(resp.json())

    @staticmethod
    def parse(payload) -> list[JobPosting]:
        jobs = []
        for item in (payload or {}).get("jobs", []):
            jobs.append(
                JobPosting(
                    source="remotive",
                    external_id=str(item.get("id")),
                    url=item.get("url") or "",
                    title=(item.get("title") or "").strip(),
                    company=item.get("company_name") or "",
                    location=item.get("candidate_required_location") or "Remoto",
                    remote=True,
                    modality="Remoto",
                    tags=list(item.get("tags") or [])[:10],
                    description=strip_html(item.get("description")),
                    published_at=parse_datetime(item.get("publication_date")),
                )
            )
        return [j for j in jobs if j.title and j.url]


class RemoteOKSource(JobSource):
    name = "remoteok"
    label = "Remote OK"
    homepage = "https://remoteok.com"
    min_interval_minutes = 60

    async def fetch(self, client: httpx.AsyncClient, keywords: list[str]) -> list[JobPosting]:
        resp = await client.get("https://remoteok.com/api", headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        return self.parse(resp.json())

    @staticmethod
    def parse(payload) -> list[JobPosting]:
        jobs = []
        for item in payload or []:
            if not isinstance(item, dict) or "position" not in item:
                continue  # el primer elemento es el aviso legal
            jobs.append(
                JobPosting(
                    source="remoteok",
                    external_id=str(item.get("id")),
                    url=item.get("url") or f"https://remoteok.com/remote-jobs/{item.get('id')}",
                    title=(item.get("position") or "").strip(),
                    company=item.get("company") or "",
                    location=item.get("location") or "Remoto",
                    remote=True,
                    modality="Remoto",
                    tags=list(item.get("tags") or [])[:10],
                    salary_min=to_float(item.get("salary_min")),
                    salary_max=to_float(item.get("salary_max")),
                    currency="USD" if item.get("salary_min") else "",
                    description=strip_html(item.get("description")),
                    published_at=parse_datetime(item.get("epoch") or item.get("date")),
                )
            )
        return [j for j in jobs if j.title]


class ArbeitnowSource(JobSource):
    name = "arbeitnow"
    label = "Arbeitnow"
    homepage = "https://www.arbeitnow.com"
    min_interval_minutes = 60

    async def fetch(self, client: httpx.AsyncClient, keywords: list[str]) -> list[JobPosting]:
        resp = await client.get("https://www.arbeitnow.com/api/job-board-api")
        resp.raise_for_status()
        return self.parse(resp.json())

    @staticmethod
    def parse(payload) -> list[JobPosting]:
        jobs = []
        for item in (payload or {}).get("data", []):
            remote = bool(item.get("remote"))
            jobs.append(
                JobPosting(
                    source="arbeitnow",
                    external_id=str(item.get("slug")),
                    url=item.get("url") or "",
                    title=(item.get("title") or "").strip(),
                    company=item.get("company_name") or "",
                    location=item.get("location") or ("Remoto" if remote else ""),
                    country="Alemania" if not remote else "",
                    remote=remote,
                    modality="Remoto" if remote else "Presencial",
                    tags=list(item.get("tags") or [])[:10],
                    description=strip_html(item.get("description")),
                    published_at=parse_datetime(item.get("created_at")),
                )
            )
        return [j for j in jobs if j.title and j.url]


class HimalayasSource(JobSource):
    name = "himalayas"
    label = "Himalayas"
    homepage = "https://himalayas.app"
    min_interval_minutes = 60

    async def fetch(self, client: httpx.AsyncClient, keywords: list[str]) -> list[JobPosting]:
        resp = await client.get("https://himalayas.app/jobs/api", params={"limit": 50})
        resp.raise_for_status()
        return self.parse(resp.json())

    @staticmethod
    def parse(payload) -> list[JobPosting]:
        jobs = []
        for item in (payload or {}).get("jobs", []):
            restrictions = item.get("locationRestrictions") or []
            location = ", ".join(restrictions) if restrictions else "Remoto (global)"
            ext = item.get("guid") or item.get("applicationLink") or item.get("title")
            jobs.append(
                JobPosting(
                    source="himalayas",
                    external_id=str(ext)[:200],
                    url=item.get("applicationLink") or item.get("guid") or "",
                    title=(item.get("title") or "").strip(),
                    company=item.get("companyName") or "",
                    location=location,
                    remote=True,
                    modality="Remoto",
                    tags=list(item.get("categories") or [])[:10],
                    salary_min=to_float(item.get("minSalary")),
                    salary_max=to_float(item.get("maxSalary")),
                    currency=item.get("currency") or "",
                    description=strip_html(item.get("excerpt") or item.get("description")),
                    published_at=parse_datetime(item.get("pubDate")),
                )
            )
        return [j for j in jobs if j.title and j.url]


class JobicySource(JobSource):
    name = "jobicy"
    label = "Jobicy"
    homepage = "https://jobicy.com"
    min_interval_minutes = 60

    async def fetch(self, client: httpx.AsyncClient, keywords: list[str]) -> list[JobPosting]:
        resp = await client.get("https://jobicy.com/api/v2/remote-jobs", params={"count": 50, "industry": "dev"})
        resp.raise_for_status()
        return self.parse(resp.json())

    @staticmethod
    def parse(payload) -> list[JobPosting]:
        jobs = []
        for item in (payload or {}).get("jobs", []):
            industry = item.get("jobIndustry") or []
            if isinstance(industry, str):
                industry = [industry]
            jobs.append(
                JobPosting(
                    source="jobicy",
                    external_id=str(item.get("id")),
                    url=item.get("url") or "",
                    title=strip_html(item.get("jobTitle"), 300),
                    company=item.get("companyName") or "",
                    location=item.get("jobGeo") or "Remoto",
                    remote=True,
                    modality="Remoto",
                    tags=[strip_html(t, 60) for t in industry][:10],
                    salary_min=to_float(item.get("annualSalaryMin")),
                    salary_max=to_float(item.get("annualSalaryMax")),
                    currency=item.get("salaryCurrency") or "",
                    description=strip_html(item.get("jobExcerpt") or item.get("jobDescription")),
                    published_at=parse_datetime(item.get("pubDate")),
                )
            )
        return [j for j in jobs if j.title and j.url]
