"""Enumerations for domain model statuses and reasons.

Centralising enums eliminates magic strings across the codebase and
provides type-safe status values with IDE autocomplete.
"""

from enum import StrEnum


class NodeStatus(StrEnum):
    """Operational status of a network node."""

    ONLINE = "online"
    OFFLINE = "offline"


class LinkStatus(StrEnum):
    """Operational status of a network link."""

    ACTIVE = "active"
    DOWN = "down"


class PacketStatus(StrEnum):
    """Lifecycle status of a network packet."""

    CREATED = "created"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DROPPED = "dropped"


class DropReason(StrEnum):
    """Reason a packet was dropped."""

    SOURCE_OFFLINE = "SOURCE_OFFLINE"
    DESTINATION_OFFLINE = "DESTINATION_OFFLINE"
    NO_ROUTE = "NO_ROUTE"
