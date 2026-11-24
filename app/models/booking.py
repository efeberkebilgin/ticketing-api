import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, enum_column


class ReservationStatus(str, enum.Enum):
    HELD = "held"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Reservation(TimestampMixin, Base):
    __tablename__ = "reservations"
    __table_args__ = (
        # A retried request with the same key must map to the same reservation.
        UniqueConstraint("user_id", "idempotency_key"),
        # The expiry job scans "held reservations that are past expires_at".
        Index("ix_reservations_status_expires_at", "status", "expires_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ReservationStatus] = mapped_column(
        enum_column(ReservationStatus), default=ReservationStatus.HELD
    )
    expires_at: Mapped[datetime]
    idempotency_key: Mapped[str] = mapped_column(String(64))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["ReservationItem"]] = relationship(
        back_populates="reservation", cascade="all, delete-orphan"
    )


class ReservationItem(Base):
    __tablename__ = "reservation_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE")
    )
    tier_id: Mapped[int] = mapped_column(ForeignKey("ticket_tiers.id"))
    quantity: Mapped[int]
    # Price is copied at booking time so later price changes do not rewrite history.
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    reservation: Mapped["Reservation"] = relationship(back_populates="items")


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[PaymentStatus] = mapped_column(
        enum_column(PaymentStatus), default=PaymentStatus.PENDING
    )
