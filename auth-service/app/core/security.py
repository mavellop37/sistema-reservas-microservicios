from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# CONFIGURACIÓN JWT
SECRET_KEY = "tu_clave_secreta_super_segura_para_firmar_tokens"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# --- FUNCIONES DE CONTRASEÑA (BCRYPT) ---


def get_password_hash(password: str) -> str:
    """Transforma la contraseña en texto plano en un hash seguro usando bcrypt nativo."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano con el hash de la base de datos."""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# --- FUNCIONES DE SEGURIDAD JWT ---


def create_access_token(data: dict) -> str:
    """Genera un token JWT firmado que expira en el tiempo configurado."""
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependencia para proteger rutas.
    Extrae, descifra y valida el email del usuario contenido en el token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales o el token ha expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        return email

    except jwt.PyJWTError:
        raise credentials_exception
