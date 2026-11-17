from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import *
from app.security import current_user, hash_password, verify_password, issue_token, require
from app.agents.orchestrator import chat

r=APIRouter(prefix="/api/v1")
class Login(BaseModel): email:EmailStr; password:str
class Register(Login): name:str; tenant_name:str="Demo Organization"
class Entity(BaseModel): name:str; description:str=""; deadline:datetime|None=None; status:str="planned"
class TaskIn(BaseModel): title:str; project_id:str; priority:str="medium"; assignee_id:str|None=None; due_date:datetime|None=None; estimated_hours:int=8
class Chat(BaseModel): message:str
@r.post("/auth/login")
def login(x:Login,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(email=x.email).first()
    if not u or not u.password_hash or not verify_password(x.password,u.password_hash): raise HTTPException(401,"Invalid credentials")
    return {"access_token":issue_token(u),"token_type":"bearer"}
@r.post("/auth/register")
def register(x:Register,db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=x.email).first(): raise HTTPException(409,"Email already exists")
    t=Tenant(name=x.tenant_name); db.add(t); db.flush(); u=User(tenant_id=t.id,email=x.email,name=x.name,password_hash=hash_password(x.password),role="admin"); db.add(u);db.commit();return {"access_token":issue_token(u)}
@r.get("/auth/me")
def me(u=Depends(current_user)): return {"id":u.id,"email":u.email,"name":u.name,"role":u.role,"tenant_id":u.tenant_id}
def scoped(model):
    def list_(db:Session=Depends(get_db),u=Depends(current_user)): return db.query(model).filter_by(tenant_id=u.tenant_id).all()
    return list_
@r.get("/employees")
def employees(db:Session=Depends(get_db),u=Depends(current_user)): return db.query(Employee).filter_by(tenant_id=u.tenant_id).all()
@r.post("/employees")
def employee(x:Entity,db:Session=Depends(get_db),u=Depends(require("admin","manager"))): e=Employee(tenant_id=u.tenant_id,name=x.name,title=x.description or "Team member");db.add(e);db.commit();return e
@r.get("/projects")
def projects(db:Session=Depends(get_db),u=Depends(current_user)): return db.query(Project).filter_by(tenant_id=u.tenant_id).all()
@r.post("/projects")
def project(x:Entity,db:Session=Depends(get_db),u=Depends(require("admin","manager"))): p=Project(tenant_id=u.tenant_id,name=x.name,description=x.description,status=x.status,deadline=x.deadline,owner_id=u.id);db.add(p);db.commit();return p
@r.get("/tasks")
def tasks(db:Session=Depends(get_db),u=Depends(current_user)): return db.query(Task).filter_by(tenant_id=u.tenant_id).all()
@r.post("/tasks")
def task(x:TaskIn,db:Session=Depends(get_db),u=Depends(require("admin","manager"))):
    if not db.query(Project).filter_by(id=x.project_id,tenant_id=u.tenant_id).first(): raise HTTPException(404,"Project not found")
    t=Task(tenant_id=u.tenant_id,**x.model_dump());db.add(t);db.commit();return t
@r.get("/approvals")
def approvals(db:Session=Depends(get_db),u=Depends(current_user)): return db.query(Approval).filter_by(tenant_id=u.tenant_id).all()
@r.post("/approvals/{approval_id}/{decision}")
def decide(approval_id:str,decision:str,db:Session=Depends(get_db),u=Depends(require("admin","manager"))):
    if decision not in {"approve","reject"}: raise HTTPException(400,"Unsupported decision")
    a=db.query(Approval).filter_by(id=approval_id,tenant_id=u.tenant_id).first()
    if not a: raise HTTPException(404,"Approval not found")
    a.status="approved" if decision=="approve" else "rejected";db.add(ApprovalHistory(approval_id=a.id,actor_id=u.id,decision=a.status));db.commit();return a
@r.get("/releases")
def releases(db:Session=Depends(get_db),u=Depends(current_user)): return db.query(Release).filter_by(tenant_id=u.tenant_id).all()
@r.post("/agents/chat")
def agent(x:Chat,db:Session=Depends(get_db),u=Depends(current_user)): return chat(db,u,x.message)
@r.get("/agents/runs")
def runs(db:Session=Depends(get_db),u=Depends(current_user)): return db.query(AgentRun).filter_by(tenant_id=u.tenant_id).order_by(AgentRun.started_at.desc()).all()
@r.get("/analytics/overview")
def analytics(db:Session=Depends(get_db),u=Depends(current_user)):
    q=lambda m:db.query(m).filter_by(tenant_id=u.tenant_id).count(); overdue=db.query(Task).filter(Task.tenant_id==u.tenant_id,Task.due_date<datetime.utcnow(),Task.status!="done").count(); done=db.query(Task).filter_by(tenant_id=u.tenant_id,status="done").count();return {"employees":q(Employee),"projects":q(Project),"pending_approvals":db.query(Approval).filter_by(tenant_id=u.tenant_id,status="pending").count(),"completed_tasks":done,"overdue_tasks":overdue}
