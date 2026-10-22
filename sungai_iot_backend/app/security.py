import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.db import get_db
from app.models import User
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
def hash_password(p): return pwd_context.hash(p)
def verify_password(p,h): return pwd_context.verify(p,h)
def hash_key(k): return hashlib.sha256(k.encode()).hexdigest()
def create_token(user):
    return jwt.encode({"sub":str(user.id),"role":user.role,"exp":datetime.now(timezone.utc)+timedelta(minutes=settings.jwt_expire_minutes)},settings.jwt_secret,algorithm="HS256")
def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Token diperlukan")

    token = credentials.credentials

    try:
        uid = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        ).get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid")

    user = db.get(User, int(uid)) if uid else None

    if not user or not user.aktif:
        raise HTTPException(
            status_code=401,
            detail="Pengguna tidak aktif/tidak ditemukan",
        )

    return user
def roles(*allowed):
    def guard(user:User=Depends(current_user)):
        if user.role not in allowed: raise HTTPException(403,"Akses ditolak")
        return user
    return guard
