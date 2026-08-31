"""Custom exception hierarchy and FastAPI exception handlers.

Every domain error has a dedicated exception class, making error handling
explicit and enabling precise HTTP status code mapping.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logger import get_logger

logger = get_logger("core.exceptions")


# ---------------------------------------------------------------------------
# Base exception
# ---------------------------------------------------------------------------

class SimulatorError(Exception):
    """Base exception for all simulator domain errors."""

    def __init__(self, message: str, detail: str | None = None) -> None:
        self.message = message
        self.detail = detail
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Node exceptions
# ---------------------------------------------------------------------------

class NodeNotFoundError(SimulatorError):
    """Raised when a node with the given identifier does not exist."""

    def __init__(self, node_id: str) -> None:
        super().__init__(
            message=f"Node not found: {node_id}",
            detail=f"No node exists with id '{node_id}'",
        )
        self.node_id = node_id


class DuplicateNodeError(SimulatorError):
    """Raised when attempting to create a node with a name that already exists."""

    def __init__(self, name: str) -> None:
        super().__init__(
            message=f"Duplicate node name: {name}",
            detail=f"A node with name '{name}' already exists",
        )
        self.name = name


class NodeOfflineError(SimulatorError):
    """Raised when an operation requires a node to be online but it is offline."""

    def __init__(self, node_id: str, role: str) -> None:
        super().__init__(
            message=f"Node offline: {node_id} ({role})",
            detail=f"The {role} node '{node_id}' is currently offline",
        )
        self.node_id = node_id
        self.role = role


# ---------------------------------------------------------------------------
# Link exceptions
# ---------------------------------------------------------------------------

class LinkNotFoundError(SimulatorError):
    """Raised when a link with the given identifier does not exist."""

    def __init__(self, link_id: str) -> None:
        super().__init__(
            message=f"Link not found: {link_id}",
            detail=f"No link exists with id '{link_id}'",
        )
        self.link_id = link_id


class DuplicateLinkError(SimulatorError):
    """Raised when a link between the same source and destination already exists."""

    def __init__(self, source: str, destination: str) -> None:
        super().__init__(
            message=f"Duplicate link: {source} -> {destination}",
            detail=f"A link from '{source}' to '{destination}' already exists",
        )
        self.source = source
        self.destination = destination


# ---------------------------------------------------------------------------
# Packet exceptions
# ---------------------------------------------------------------------------

class PacketNotFoundError(SimulatorError):
    """Raised when a packet with the given identifier does not exist."""

    def __init__(self, packet_id: str) -> None:
        super().__init__(
            message=f"Packet not found: {packet_id}",
            detail=f"No packet exists with id '{packet_id}'",
        )
        self.packet_id = packet_id


# ---------------------------------------------------------------------------
# Routing exceptions
# ---------------------------------------------------------------------------

class NoRouteError(SimulatorError):
    """Raised when no path exists between source and destination nodes."""

    def __init__(self, source: str, destination: str) -> None:
        super().__init__(
            message=f"No route: {source} -> {destination}",
            detail=f"No network path exists from '{source}' to '{destination}'",
        )
        self.source = source
        self.destination = destination


# ---------------------------------------------------------------------------
# FastAPI exception handlers
# ---------------------------------------------------------------------------

def _build_error_response(status_code: int, error: SimulatorError) -> JSONResponse:
    """Build a consistent JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": type(error).__name__,
            "message": error.message,
            "detail": error.detail,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(NodeNotFoundError)
    async def node_not_found_handler(
        request: Request, exc: NodeNotFoundError
    ) -> JSONResponse:
        logger.warning("Node not found: %s [%s %s]", exc.node_id, request.method, request.url.path)
        return _build_error_response(404, exc)

    @app.exception_handler(LinkNotFoundError)
    async def link_not_found_handler(
        request: Request, exc: LinkNotFoundError
    ) -> JSONResponse:
        logger.warning("Link not found: %s [%s %s]", exc.link_id, request.method, request.url.path)
        return _build_error_response(404, exc)

    @app.exception_handler(PacketNotFoundError)
    async def packet_not_found_handler(
        request: Request, exc: PacketNotFoundError
    ) -> JSONResponse:
        logger.warning("Packet not found: %s [%s %s]", exc.packet_id, request.method, request.url.path)
        return _build_error_response(404, exc)

    @app.exception_handler(DuplicateNodeError)
    async def duplicate_node_handler(
        request: Request, exc: DuplicateNodeError
    ) -> JSONResponse:
        logger.warning("Duplicate node: %s [%s %s]", exc.name, request.method, request.url.path)
        return _build_error_response(409, exc)

    @app.exception_handler(DuplicateLinkError)
    async def duplicate_link_handler(
        request: Request, exc: DuplicateLinkError
    ) -> JSONResponse:
        logger.warning("Duplicate link: %s->%s [%s %s]", exc.source, exc.destination, request.method, request.url.path)
        return _build_error_response(409, exc)

    @app.exception_handler(NodeOfflineError)
    async def node_offline_handler(
        request: Request, exc: NodeOfflineError
    ) -> JSONResponse:
        logger.warning("Node offline: %s [%s %s]", exc.node_id, request.method, request.url.path)
        return _build_error_response(422, exc)

    @app.exception_handler(NoRouteError)
    async def no_route_handler(
        request: Request, exc: NoRouteError
    ) -> JSONResponse:
        logger.warning("No route: %s->%s [%s %s]", exc.source, exc.destination, request.method, request.url.path)
        return _build_error_response(422, exc)

    @app.exception_handler(SimulatorError)
    async def simulator_error_handler(
        request: Request, exc: SimulatorError
    ) -> JSONResponse:
        logger.error("Simulator error: %s [%s %s]", exc.message, request.method, request.url.path)
        return _build_error_response(500, exc)
