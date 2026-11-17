from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import AgentRun, Employee, Project, Task, Approval

def chat(db:Session, user, message:str):
    run=AgentRun(tenant_id=user.tenant_id,user_id=user.id,agent_name="manager",input_summary=message,status="running"); db.add(run); db.flush()
    lower=message.lower(); involved=[]; data={}
    if "overload" in lower or "workload" in lower:
        involved=["workforce","analytics"]
        rows=db.query(Employee.name,func.coalesce(func.sum(Task.estimated_hours),0)).outerjoin(Task,Task.assignee_id==Employee.id).filter(Employee.tenant_id==user.tenant_id).group_by(Employee.id).all()
        data={"recommendations":[{"employee":name,"assigned_hours":hours,"status":"overloaded" if hours>40 else "available"} for name,hours in rows]}
        summary="Workforce analysis completed. Reassignment requires manager approval."
    elif "create" in lower and "project" in lower:
        involved=["planning","workforce","approval"]
        project=Project(tenant_id=user.tenant_id,name=_title(message),description=message,status="planned",owner_id=user.id,deadline=datetime.utcnow()+timedelta(days=30)); db.add(project); db.flush()
        tasks=["Define scope","Build implementation","Quality review"]
        for title in tasks: db.add(Task(tenant_id=user.tenant_id,project_id=project.id,title=title,due_date=project.deadline))
        approval=Approval(tenant_id=user.tenant_id,title=f"Approve plan: {project.name}",requested_by=user.id,related_project_id=project.id); db.add(approval)
        data={"project_id":project.id,"approval_id":approval.id,"tasks_created":len(tasks)}; summary="Project plan drafted and submitted for human approval; no sensitive action was auto-approved."
    elif "release" in lower and ("ready" in lower or "readiness" in lower):
        involved=["release"]
        open_tasks=db.query(Task).filter(Task.tenant_id==user.tenant_id,Task.status!="done").count(); data={"open_tasks":open_tasks,"ready":open_tasks==0}; summary="Release readiness is based on persisted task status."
    else:
        involved=["analytics"]; projects=db.query(Project).filter_by(tenant_id=user.tenant_id).count(); tasks=db.query(Task).filter_by(tenant_id=user.tenant_id).count(); data={"projects":projects,"tasks":tasks}; summary="I can create a project, analyze workload, identify overdue tasks, or assess release readiness."
    run.status="completed"; run.result_summary=summary; run.ended_at=datetime.utcnow(); db.commit()
    return {"message":summary,"agents":involved,"data":data,"run_id":run.id}
def _title(text): return text.replace("Create","").replace("create","").strip()[:150] or "New project"
