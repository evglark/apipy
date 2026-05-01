from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from apipy.database import Base


class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    password_hash: Mapped[str]


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_agent: Mapped[str]
    ip: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[int] = mapped_column(BigInteger)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    revoked: Mapped[bool] = mapped_column(default=False)
    reuse_detected: Mapped[bool] = mapped_column(default=False)
    session_id: Mapped[str]
    device_id: Mapped[str]
    created_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)


class BlacklistedToken(Base):
    __tablename__ = "token_blacklist"

    token: Mapped[str] = mapped_column(primary_key=True)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    username: Mapped[str] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(default=0)
    blocked_until: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event: Mapped[str]
    ts: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    details: Mapped[str | None]


class MagicToken(Base):
    __tablename__ = "magic_tokens"

    token: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    exp: Mapped[int] = mapped_column(BigInteger)
    used: Mapped[bool] = mapped_column(default=False)


class IPRateLimitAttempt(Base):
    __tablename__ = "ip_rate_limit_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(index=True)
    ts: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
