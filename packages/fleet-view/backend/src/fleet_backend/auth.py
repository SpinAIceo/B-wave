from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production-use-32-chars-min")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class Role(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class TokenData(BaseModel):
    sub: str
    role: Role
    exp: datetime


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: Role
    disabled: bool = False


# ── Simple in-memory user store (replace with DB query in production) ─────────
# Passwords are plain-text here only for demo. In production use bcrypt.
_USERS: dict[str, UserInDB] = {
    "admin": UserInDB(
        username="admin",
        hashed_password=os.environ.get("ADMIN_PASSWORD", "bwave-admin"),
        role=Role.ADMIN,
    ),
    "operator": UserInDB(
        username="operator",
        hashed_password=os.environ.get("OPERATOR_PASSWORD", "bwave-operator"),
        role=Role.OPERATOR,
    ),
    "viewer": UserInDB(
        username="viewer",
        hashed_password=os.environ.get("VIEWER_PASSWORD", "bwave-viewer"),
        role=Role.VIEWER,
    ),
}


def _verify_password(plain: str, hashed: str) -> bool:
    return plain == hashed  # swap for bcrypt.checkpw in production


def _authenticate_user(username: str, password: str) -> UserInDB | None:
    user = _USERS.get(username)
    if user is None or user.disabled:
        return None
    if not _verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, role: Role) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> UserInDB | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        role_str: str = payload.get("role", "")
        if not username:
            return None
        return UserInDB(
            username=username,
            hashed_password="",
            role=Role(role_str),
        )
    except (JWTError, ValueError):
        return None


def require_role(*roles: Role):
    """Dependency factory: raises 403 if the authenticated user lacks required role."""
    async def _check(user: Annotated[UserInDB | None, Depends(get_current_user)]):
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not permitted. Required: {[r for r in roles]}",
            )
        return user
    return _check


# Convenience dependency aliases
RequireAdmin = Depends(require_role(Role.ADMIN))
RequireOperator = Depends(require_role(Role.ADMIN, Role.OPERATOR))
RequireViewer = Depends(require_role(Role.ADMIN, Role.OPERATOR, Role.VIEWER))


# ── Token endpoint models ─────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    expires_in: int


async def login_for_access_token(form_data: OAuth2PasswordRequestForm) -> Token:
    user = _authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.username, user.role)
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
