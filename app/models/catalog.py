import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, enum_column


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(80))
    address: Mapped[str] = mapped_column(String(255))
    capacity: Mapped[int]


class Event(TimestampMixin, Base):
    __tablename__ = "events"
    __table_args__ = (
        # Event listing: "published events, soonest first".
        Index("ix_events_status_starts_at", "status", "starts_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    starts_at: Mapped[datetime]
    status: Mapped[EventStatus] = mapped_column(
        enum_column(EventStatus), default=EventStatus.DRAFT
    )

    tiers: Mapped[list["TicketTier"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class TicketTier(TimestampMixin, Base):
    """A sellable category of an event (e.g. Standard, VIP) with its own stock."""

    __tablename__ = "ticket_tiers"
    __table_args__ = (
        UniqueConstraint("event_id", "name"),
        # Database-level safety net: even a buggy code path cannot oversell.
        CheckConstraint("available_quantity >= 0", name="available_non_negative"),
        CheckConstraint("available_quantity <= total_quantity", name="available_lte_total"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(80))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_quantity: Mapped[int]
    available_quantity: Mapped[int]
    # Used by the optimistic-locking variant of the reservation flow.
    version: Mapped[int] = mapped_column(default=1)

    event: Mapped["Event"] = relationship(back_populates="tiers")
