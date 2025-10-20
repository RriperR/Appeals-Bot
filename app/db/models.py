from datetime import datetime
from enum import StrEnum
from sqlalchemy import String, Text, Boolean, ForeignKey, BigInteger, func, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class AppealStatus(StrEnum):
    NEW = "NEW"
    IN_REVIEW = "IN_REVIEW"
    ON_HOLD = "ON_HOLD"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    DELETED = "DELETED"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    appeals: Mapped[list["Appeal"]] = relationship(back_populates="user")

class Commission(Base):
    __tablename__ = "commissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    appeals: Mapped[list["Appeal"]] = relationship(back_populates="commission")

class Appeal(Base):
    __tablename__ = "appeals"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    commission_id: Mapped[int] = mapped_column(ForeignKey("commissions.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    contact: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), index=True, default=AppealStatus.NEW.value)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="appeals")
    commission: Mapped[Commission] = relationship(back_populates="appeals")
    files: Mapped[list["AppealFile"]] = relationship(back_populates="appeal", cascade="all, delete-orphan")

Index("ix_appeal_user_commission", Appeal.user_id, Appeal.commission_id)

class AppealFile(Base):
    __tablename__ = "appeal_files"
    id: Mapped[int] = mapped_column(primary_key=True)
    appeal_id: Mapped[int] = mapped_column(ForeignKey("appeals.id"), index=True)
    telegram_file_id: Mapped[str] = mapped_column(String(512))
    file_name: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    appeal: Mapped[Appeal] = relationship(back_populates="files")

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    appeal_id: Mapped[int | None] = mapped_column(ForeignKey("appeals.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    sent_ok: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)

class AdminRequestStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"

class AdminRequest(Base):
    __tablename__ = "admin_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default=AdminRequestStatus.PENDING.value, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

class AdminRole(Base):
    __tablename__ = "admin_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    __table_args__ = (UniqueConstraint("user_id", name="uq_admin_roles_user"),)
