from datetime import datetime, timedelta
from app.database import Base,engine,SessionLocal
from app.models import *
from app.security import hash_password

def main():
 Base.metadata.create_all(engine);db=SessionLocal()
 if db.query(Tenant).first(): print("Database already seeded");return
 t=Tenant(name="Acme Operations");db.add(t);db.flush(); users=[]
 for email,name,role in [("admin@acme.test","Avery Admin","admin"),("manager@acme.test","Morgan Manager","manager"),("manager2@acme.test","Jordan Manager","manager")]:
  u=User(tenant_id=t.id,email=email,name=name,role=role,password_hash=hash_password("DemoPass123!"));db.add(u);users.append(u)
 db.flush();employees=[]
 for i,name in enumerate(["Riya Shah","Noah Kim","Maya Patel","Leo Garcia","Sara Chen"]):
  e=Employee(tenant_id=t.id,name=name,title="Operations Specialist",skills=["python","planning"] if i<2 else ["operations","analysis"]);db.add(e);employees.append(e)
 db.flush()
 for pidx,name in enumerate(["Platform Modernization","Customer Onboarding","Release Automation"]):
  p=Project(tenant_id=t.id,name=name,description="Demo operations program",status="active",owner_id=users[1].id,deadline=datetime.utcnow()+timedelta(days=30+pidx*10));db.add(p);db.flush()
  for j in range(5): db.add(Task(tenant_id=t.id,project_id=p.id,title=f"{name} task {j+1}",status="done" if j==0 else "todo",assignee_id=employees[j].id,due_date=datetime.utcnow()+timedelta(days=j-2),estimated_hours=8))
  db.add(Approval(tenant_id=t.id,title=f"Approve {name} plan",requested_by=users[1].id,related_project_id=p.id))
 db.add(Release(tenant_id=t.id,name="v1.0.0",status="planned",planned_at=datetime.utcnow()+timedelta(days=14)))
 db.commit();print("Seeded Acme Operations")
if __name__=="__main__":main()
