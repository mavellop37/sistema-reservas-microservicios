from typing import Optional

from pydantic import BaseModel, EmailStr


# Información enviada por el cliente al registrarse
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nombre_completo: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nombre_completo: str

    class Config:
        from_attributes = True


# Esquema para el Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Esquema para el Token JWT
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
