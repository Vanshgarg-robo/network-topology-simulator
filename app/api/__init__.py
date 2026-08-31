"""API layer router aggregations."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.links import router as links_router
from app.api.metrics import router as metrics_router
from app.api.nodes import router as nodes_router
from app.api.packets import router as packets_router
from app.api.topology import router as topology_router

api_router = APIRouter()

api_router.include_router(nodes_router, prefix="/nodes", tags=["Nodes"])
api_router.include_router(links_router, prefix="/links", tags=["Links"])
api_router.include_router(packets_router, prefix="/packets", tags=["Packets"])
api_router.include_router(topology_router, prefix="/topology", tags=["Topology"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])

__all__ = ["api_router", "health_router"]
