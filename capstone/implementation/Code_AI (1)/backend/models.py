from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ==========================================================
# User
# ==========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(256),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(128),
        nullable=False,
    )

    hashed_password = Column(
        String(256),
        nullable=False,
    )

    role = Column(
        String(32),
        default="user",
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    logs = relationship(
        "LogEntry",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# ==========================================================
# Project
# ==========================================================

class Project(Base):

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(256),
        nullable=False,
    )

    description = Column(
        Text,
        default="",
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner = relationship(
        "User",
        back_populates="projects",
    )

    generated_code = relationship(
        "GeneratedCode",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    review_history = relationship(
        "ReviewHistory",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    vulnerabilities = relationship(
        "Vulnerability",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    reports = relationship(
        "Report",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# ==========================================================
# Generated Code
# ==========================================================

class GeneratedCode(Base):

    __tablename__ = "generated_code"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    code = Column(Text, nullable=False)

    prompt = Column(Text, nullable=False)

    model_name = Column(
        String(128),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="generated_code",
    )


# ==========================================================
# Review History
# ==========================================================

class ReviewHistory(Base):

    __tablename__ = "review_history"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    summary = Column(Text, nullable=False)

    findings = Column(Text, nullable=False)

    suggestions = Column(Text, nullable=False)

    model_name = Column(
        String(128),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="review_history",
    )


# ==========================================================
# Vulnerability
# ==========================================================

class Vulnerability(Base):

    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    severity = Column(
        String(32),
        nullable=False,
        index=True,
    )

    pattern = Column(
        String(256),
        nullable=False,
    )

    description = Column(Text, nullable=False)

    recommendation = Column(Text, nullable=False)

    cwe_id = Column(
        String(32),
        default="Unknown",
    )

    risk_score = Column(
        Float,
        default=0.0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="vulnerabilities",
    )


# ==========================================================
# Recommendation
# ==========================================================

class Recommendation(Base):

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    title = Column(
        String(256),
        nullable=False,
    )

    details = Column(
        Text,
        nullable=False,
    )

    category = Column(
        String(128),
        default="General",
    )

    priority = Column(
        Integer,
        default=1,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="recommendations",
    )


# ==========================================================
# Report
# ==========================================================

class Report(Base):

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    filename = Column(
        String(256),
        nullable=False,
    )

    format = Column(
        String(32),
        nullable=False,
    )

    generated_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="reports",
    )


# ==========================================================
# Log Entry
# ==========================================================

class LogEntry(Base):

    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    event = Column(
        String(256),
        nullable=False,
    )

    details = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="logs",
    )