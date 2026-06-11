import time

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Generar un email único basado en el timestamp actual
UNIQUE_EMAIL = f"user_{int(time.time())}@example.com"


def test_register_user_success():
    """Prueba que un usuario se puede registrar exitosamente"""
    payload = {
        "username": "test_pytest",
        "email": UNIQUE_EMAIL,  # 🔄 Usamos el email dinámico único
        "password": "password123",
    }
    response = client.post("/auth/register", json=payload)

    assert response.status_code in [200, 201]

    data = response.json()
    assert "email" in data
    assert data["email"] == UNIQUE_EMAIL


def test_login_user_success():
    """Prueba que un usuario registrado puede iniciar sesión y obtener su JWT"""
    payload = {
        "email": UNIQUE_EMAIL,  # 🔄 Iniciar sesión con el email recién creado
        "password": "password123",
    }
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_wrong_password():
    """Prueba que el sistema rechaza credenciales inválidas"""
    payload = {
        "email": UNIQUE_EMAIL,  # 🔄 Mismo email dinámico
        "password": "contraseña_incorrecta",
    }
    response = client.post("/auth/login", json=payload)

    assert response.status_code in [400, 401]
