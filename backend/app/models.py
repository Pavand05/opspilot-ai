import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

def uid(): return str(uuid.uuid4())
def now(): return datetime.utcnow()

class Tenant(Base):
    __tablename__="tenants"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); name: Mapped[str]=mapped_column(String(120),unique=True); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class User(Base):
    __tablename__="users"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); email: Mapped[str]=mapped_column(String(255),unique=True); name: Mapped[str]=mapped_column(String(120)); password_hash: Mapped[str|None]=mapped_column(String(255),nullable=True); role: Mapped[str]=mapped_column(String(30),default="employee"); firebase_uid: Mapped[str|None]=mapped_column(String(128),unique=True); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Employee(Base):
    __tablename__="employees"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); user_id: Mapped[str|None]=mapped_column(ForeignKey("users.id")); name: Mapped[str]=mapped_column(String(120)); title: Mapped[str]=mapped_column(String(120)); skills: Mapped[list]=mapped_column(JSON,default=list); capacity_hours: Mapped[int]=mapped_column(Integer,default=40); active: Mapped[bool]=mapped_column(Boolean,default=True)
class Project(Base):
    __tablename__="projects"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); name: Mapped[str]=mapped_column(String(160)); description: Mapped[str]=mapped_column(Text,default=""); status: Mapped[str]=mapped_column(String(30),default="planned"); deadline: Mapped[datetime|None]=mapped_column(DateTime); owner_id: Mapped[str|None]=mapped_column(ForeignKey("users.id")); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Milestone(Base):
    __tablename__="milestones"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); project_id: Mapped[str]=mapped_column(ForeignKey("projects.id",ondelete="CASCADE")); name: Mapped[str]=mapped_column(String(160)); due_date: Mapped[datetime|None]=mapped_column(DateTime)
class Task(Base):
    __tablename__="tasks"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); project_id: Mapped[str]=mapped_column(ForeignKey("projects.id",ondelete="CASCADE")); title: Mapped[str]=mapped_column(String(200)); status: Mapped[str]=mapped_column(String(30),default="todo"); priority: Mapped[str]=mapped_column(String(20),default="medium"); assignee_id: Mapped[str|None]=mapped_column(ForeignKey("employees.id")); due_date: Mapped[datetime|None]=mapped_column(DateTime); estimated_hours: Mapped[int]=mapped_column(Integer,default=8)
class Approval(Base):
    __tablename__="approvals"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); title: Mapped[str]=mapped_column(String(200)); status: Mapped[str]=mapped_column(String(20),default="pending"); requested_by: Mapped[str]=mapped_column(ForeignKey("users.id")); related_project_id: Mapped[str|None]=mapped_column(ForeignKey("projects.id")); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class ApprovalHistory(Base):
    __tablename__="approval_history"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); approval_id: Mapped[str]=mapped_column(ForeignKey("approvals.id",ondelete="CASCADE")); actor_id: Mapped[str]=mapped_column(ForeignKey("users.id")); decision: Mapped[str]=mapped_column(String(20)); note: Mapped[str]=mapped_column(Text,default=""); decided_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Release(Base):
    __tablename__="releases"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); name: Mapped[str]=mapped_column(String(120)); status: Mapped[str]=mapped_column(String(30),default="planned"); planned_at: Mapped[datetime|None]=mapped_column(DateTime); notes: Mapped[str]=mapped_column(Text,default="")
class AgentRun(Base):
    __tablename__="agent_runs"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); agent_name: Mapped[str]=mapped_column(String(80)); input_summary: Mapped[str]=mapped_column(Text); status: Mapped[str]=mapped_column(String(30)); result_summary: Mapped[str]=mapped_column(Text,default=""); error: Mapped[str|None]=mapped_column(Text); started_at: Mapped[datetime]=mapped_column(DateTime,default=now); ended_at: Mapped[datetime|None]=mapped_column(DateTime)
class AuditLog(Base): __tablename__="audit_logs"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); actor_id: Mapped[str|None]=mapped_column(String); action: Mapped[str]=mapped_column(String(100)); metadata_: Mapped[dict]=mapped_column("metadata",JSON,default=dict); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Notification(Base): __tablename__="notifications"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(ForeignKey("tenants.id"),index=True); user_id: Mapped[str|None]=mapped_column(String); message: Mapped[str]=mapped_column(Text); read: Mapped[bool]=mapped_column(Boolean,default=False); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class IdempotencyKey(Base): __tablename__="idempotency_keys"; id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); tenant_id: Mapped[str]=mapped_column(String,index=True); key: Mapped[str]=mapped_column(String(255)); response: Mapped[dict]=mapped_column(JSON,default=dict); __table_args__=(UniqueConstraint("tenant_id","key"),)
