from app.agent.sources.base import JobPosting, JobSource
from app.agent.sources.getonboard import GetOnBoardSource
from app.agent.sources.remote_boards import (
    ArbeitnowSource,
    HimalayasSource,
    JobicySource,
    RemoteOKSource,
    RemotiveSource,
)

REGISTRY: dict[str, JobSource] = {
    s.name: s
    for s in (
        GetOnBoardSource(),
        RemotiveSource(),
        RemoteOKSource(),
        ArbeitnowSource(),
        HimalayasSource(),
        JobicySource(),
    )
}

__all__ = ["REGISTRY", "JobPosting", "JobSource"]
