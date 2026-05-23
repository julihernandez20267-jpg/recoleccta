from sqlalchemy import Column, Integer, String, Enum, Text, TIMESTAMP, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role_rel")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    displayName = Column(String(255), nullable=True)
    photoURL = Column(Text(length=16777215), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # OTP columns
    otp_code = Column(String(6), nullable=True)
    otp_expiry = Column(TIMESTAMP, nullable=True)

    role_rel = relationship("Role", back_populates="users")
    route_assignments = relationship("GuardianRouteAssignment", back_populates="guardian", cascade="all, delete-orphan")

    @property
    def uid(self):
        return self.id

    @property
    def role(self) -> str:
        return self.role_rel.name if self.role_rel else "user"

    @role.setter
    def role(self, role_name: str):
        role_map = {"admin": 1, "guardian": 2, "user": 3}
        self.role_id = role_map.get(role_name, 3)


class Route(Base):
    __tablename__ = "routes"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    zone = Column(String(255), nullable=False)
    points = Column(Text, nullable=False)  # JSON-encoded coordinates list
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class GuardianRouteAssignment(Base):
    __tablename__ = "guardian_route_assignments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    guardian_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    route_id = Column(String(50), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum('pending', 'in-progress', 'completed'), default='pending', nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    guardian = relationship("User", back_populates="route_assignments")
    route = relationship("Route", primaryjoin="foreign(GuardianRouteAssignment.route_id) == Route.id", uselist=False)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String(255), nullable=False)
    neighborhood = Column(String(255), nullable=True)
    status = Column(Enum('pending', 'in-progress', 'completed'), default='pending', nullable=False)
    type = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observations = Column(Text, nullable=True)
    reporter_name = Column(String(255), nullable=True)
    has_evidence = Column(Boolean, default=False, nullable=False)
    assigned_guardian_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    assigned_guardian = relationship("User", primaryjoin="foreign(Report.assigned_guardian_id) == User.id")

    @property
    def assignedGuardianName(self):
        return self.assigned_guardian.displayName if self.assigned_guardian else None



