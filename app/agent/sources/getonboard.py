"""Get on Board: portal tech de Chile/LatAm. API pública v0, sin autenticación."""

import httpx

from app.agent.sources.base import JobPosting, JobSource, parse_datetime, strip_html, to_float

API = "https://www.getonbrd.com/api/v0/search/jobs"

MODALITY = {
    "fully_remote": "Remoto",
    "remote_local": "Remoto (país)",
    "temporarily_remote": "Remoto temporal",
    "hybrid": "Híbrido",
    "no_remote": "Presencial",
}


class GetOnBoardSource(JobSource):
    name = "getonboard"
    label = "Get on Board"
    homepage = "https://www.getonbrd.com"
    min_interval_minutes = 30

    async def fetch(self, client: httpx.AsyncClient, keywords: list[str]) -> list[JobPosting]:
        postings: dict[str, JobPosting] = {}
        for keyword in keywords[:8]:  # una consulta por palabra clave, acotado
            resp = await client.get(API, params={"query": keyword, "per_page": 50, "expand[]": "company"})
            resp.raise_for_status()
            for job in self.parse(resp.json()):
                postings[job.external_id] = job
        return list(postings.values())

    @staticmethod
    def parse(payload) -> list[JobPosting]:
        jobs = []
        for item in (payload or {}).get("data", []):
            attrs = item.get("attributes", {}) or {}
            company = ""
            comp = attrs.get("company")
            if isinstance(comp, dict):
                data = comp.get("data", comp)
                company = (data.get("attributes") or {}).get("name") or data.get("name") or ""
            modality_key = attrs.get("remote_modality") or ""
            remote = bool(attrs.get("remote")) or modality_key in {"fully_remote", "remote_local"}
            countries = attrs.get("countries") or []
            country = countries[0] if countries else ""
            location = ", ".join(countries) if countries else ("Remoto" if remote else "")
            url = (item.get("links") or {}).get("public_url") or (f"https://www.getonbrd.com/jobs/{item.get('id')}")
            description = " ".join(
                strip_html(attrs.get(k), 1500) for k in ("description", "functions", "desirable")
            ).strip()
            tags = [t for t in [attrs.get("category_name"), attrs.get("seniority_name")] if t]
            jobs.append(
                JobPosting(
                    source="getonboard",
                    external_id=str(item.get("id")),
                    url=url,
                    title=(attrs.get("title") or "").strip(),
                    company=company,
                    location=location,
                    country=country,
                    remote=remote,
                    modality=MODALITY.get(modality_key, "Remoto" if remote else ""),
                    tags=tags,
                    salary_min=to_float(attrs.get("min_salary")),
                    salary_max=to_float(attrs.get("max_salary")),
                    currency="USD" if attrs.get("min_salary") else "",
                    description=description[:4000],
                    published_at=parse_datetime(attrs.get("published_at")),
                )
            )
        return [j for j in jobs if j.title and j.external_id != "None"]
