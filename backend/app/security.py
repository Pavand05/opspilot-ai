from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto"); bearer=HTTPBearer()
def hash_password(value: str): return pwd.hash(value)
def verify_password(value: str, hashed: str): return pwd.verify(value, hashed)
def issue_token(user: User): return jwt.encode({"sub":user.id,"tenant_id":user.tenant_id,"role":user.role,"exp":datetime.now(timezone.utc)+timedelta(hours=8)},settings.jwt_secret,algorithm="HS256")
def current_user(credentials: HTTPAuthorizationCredentials=Depends(bearer), db:Session=Depends(get_db)) -> User:
    try: claims=jwt.decode(credentials.credentials,settings.jwt_secret,algorithms=["HS256"])
    except jwt.PyJWTError: raise HTTPException(401,"Invalid authentication token")
    user=db.get(User,claims["sub"])
    if not user: raise HTTPException(401,"User not found")
    return user
def require(*roles):
    def check(user:User=Depends(current_user)):
        if user.role not in roles: raise HTTPException(403,"Insufficient role")
        return user
    return check
