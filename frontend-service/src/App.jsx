import React, { useState, useEffect } from "react";
import { API_AUTH_URL, API_RESERVATION_URL } from "./config/api";

function App() {
  // Estado para la autenticación
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const [userName, setUserName] = useState("");
  const [token, setToken] = useState("");
  const [authMode, setAuthMode] = useState("login");
  const [authFormData, setAuthFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  // Estado del formulario de reservas (Incluye recurso_id)
  const [formData, setFormData] = useState({
    nombre_completo: "",
    email: "",
    fecha: "",
    hora: "",
    recurso_id: "", // 🌟 Nuevo campo para el formulario
    notas: "",
  });

  const [notification, setNotification] = useState({
    show: false,
    message: "",
    type: "",
  });

  const [reservationsList, setReservationsList] = useState([]);
  const [recursosList, setRecursosList] = useState([]); // 🌟 Estado para la lista de recursos de la BD
  const [horariosList, setHorariosList] = useState([]); // 🌟 NUEVO: Estado dinámico para los bloques de horarios gestionados por el admin
  const today = new Date().toISOString().split("T")[0];

  // Obtener la lista de recursos desde el backend de reservas
  const fetchRecursos = async () => {
    try {
      const response = await fetch(
        `${API_RESERVATION_URL}/reservations/recursos`,
      );
      if (response.ok) {
        const data = await response.json();
        setRecursosList(data);
      }
    } catch (error) {
      console.error("Error al cargar recursos:", error);
    }
  };

  // 🌟 NUEVO: Obtener la lista de bloques de horarios dinámicos desde el backend de reservas
  const fetchHorarios = async () => {
    try {
      const response = await fetch(
        `${API_RESERVATION_URL}/reservations/horarios`,
      );
      if (response.ok) {
        const data = await response.json();
        setHorariosList(data);
      }
    } catch (error) {
      console.error("Error al cargar los bloques de horarios:", error);
    }
  };

  // Obtener las reservas filtradas por el usuario logueado
  const fetchReservations = async (currentToken) => {
    const activeToken = currentToken || token;
    if (!activeToken) return;

    try {
      const response = await fetch(`${API_RESERVATION_URL}/reservations/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${activeToken}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setReservationsList(data);
      }
    } catch (error) {
      console.error("Error al cargar el panel:", error);
    }
  };

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchReservations();
      fetchRecursos(); // 🚀 Carga los recursos automáticamente al iniciar sesión
      fetchHorarios(); // 🚀 Carga los horarios dinámicos de la BD automáticamente al iniciar sesión
    }
  }, [isAuthenticated, token]);

  // Manejadores de inputs
  const handleAuthChange = (e) => {
    const { name, value } = e.target;
    setAuthFormData({ ...authFormData, [name]: value });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Enviar Login o Registro al Backend
  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    // 🌟 INTERCEPCIÓN DIRECTA: Redirección inmediata al panel de administración
    if (
      authFormData.email === "admin@admin.com" &&
      authFormData.password === "123456"
    ) {
      window.location.href = `${API_RESERVATION_URL}/admin`;
      return; // Detiene el flujo para que no intente validar en el auth-service
    }
    const endpoint = authMode === "login" ? "/auth/login" : "/auth/register";

    const bodyData =
      authMode === "login"
        ? { email: authFormData.email, password: authFormData.password }
        : {
            nombre_completo: authFormData.nombre_completo,
            email: authFormData.email,
            password: authFormData.password,
          };

    try {
      const response = await fetch(`${API_AUTH_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyData),
      });

      const data = await response.json();

      if (response.ok) {
        if (authMode === "login") {
          const emailLogueado = authFormData.email;

          setToken(data.access_token);
          setUserEmail(emailLogueado);
          setUserName(emailLogueado.split("@")[0]);
          setIsAuthenticated(true);

          setFormData({
            nombre_completo: "",
            email: "",
            fecha: "",
            hora: "",
            recurso_id: "",
            notes: "",
          });

          setNotification({
            show: true,
            message: "¡Bienvenido de nuevo al sistema!",
            type: "success",
          });

          fetchReservations(data.access_token);
        } else {
          setAuthMode("login");
          setNotification({
            show: true,
            message: "Usuario registrado con éxito. Por favor, inicia sesión.",
            type: "success",
          });
        }
      } else {
        setNotification({
          show: true,
          message: data.detail || "Ocurrió un error en la autenticación.",
          type: "error",
        });
      }
    } catch (error) {
      setNotification({
        show: true,
        message: "Error de conexión con el servidor de autenticación.",
        type: "error",
      });
    }
  };

  // Enviar reserva
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.fecha < today) {
      setNotification({
        show: true,
        message: "Por favor, selecciona una fecha válida (hoy o posterior).",
        type: "error",
      });
      return;
    }

    // Convertimos el recurso_id a entero o null antes de despachar
    const payloaddeReserva = {
      ...formData,
      recurso_id: formData.recurso_id ? parseInt(formData.recurso_id) : null,
    };

    try {
      const response = await fetch(`${API_RESERVATION_URL}/reservations/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payloaddeReserva),
      });

      if (response.ok) {
        setNotification({
          show: true,
          message: "¡Tu reserva ha sido registrada con éxito!",
          type: "success",
        });

        setFormData({
          nombre_completo: "",
          email: "",
          fecha: "",
          hora: "",
          recurso_id: "",
          notas: "",
        });

        fetchReservations();
      } else {
        const errorData = await response.json();
        setNotification({
          show: true,
          message: errorData.detail || "No se pudo procesar la reserva.",
          type: "error",
        });
      }
    } catch (error) {
      setNotification({
        show: true,
        message: "Hubo un problema de conexión con el servidor.",
        type: "error",
      });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Estás seguro de que deseas cancelar esta reserva?"))
      return;

    try {
      const response = await fetch(
        `${API_RESERVATION_URL}/reservations/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (response.ok) {
        setNotification({
          show: true,
          message: "La reserva ha sido cancelada correctamente.",
          type: "success",
        });
        fetchReservations();
      } else {
        alert("No se pudo eliminar la reserva.");
      }
    } catch (error) {
      console.error("Error en la petición DELETE:", error);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserEmail("");
    setUserName("");
    setToken("");
    setReservationsList([]);
    setRecursosList([]);
    setHorariosList([]); // Limpiar estado de horarios
    setFormData({
      nombre_completo: "",
      email: "",
      fecha: "",
      hora: "",
      recurso_id: "",
      notas: "",
    });
  };

  return (
    <>
      <style
        dangerouslySetInnerHTML={{
          __html: `
        body {
          margin: 0;
          padding: 40px 20px;
          box-sizing: border-box;
          background-color: #0f172a;
          font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          color: #f8fafc;
          display: flex;
          flex-direction: column;
          gap: 24px;
          align-items: center;
          min-height: 100vh;
        }
        .app-workspace, .admin-panel, .auth-card {
          background: #1e293b;
          border-radius: 16px;
          width: 100%;
          max-width: 460px;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
          padding: 32px;
          box-sizing: border-box;
        }
        .workspace-header {
          text-align: center;
          margin-bottom: 24px;
        }
        .workspace-header h1 {
          font-size: 1.75rem;
          margin: 0 0 8px 0;
          color: #ffffff;
          font-weight: 700;
        }
        .workspace-header p {
          color: #94a3b8;
          margin: 0;
          font-size: 0.95rem;
        }
        .toast-alert {
          padding: 12px 16px;
          border-radius: 10px;
          font-size: 0.9rem;
          margin-bottom: 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-weight: 500;
          width: 100%;
          box-sizing: border-box;
        }
        .toast-alert.success {
          background-color: rgba(16, 185, 129, 0.15);
          border: 1px solid rgba(16, 185, 129, 0.3);
          color: #34d399;
        }
        .toast-alert.error {
          background-color: rgba(239, 68, 68, 0.15);
          border: 1px solid rgba(239, 68, 68, 0.3);
          color: #f87171;
        }
        .alert-close-btn {
          background: none;
          border: none;
          color: inherit;
          cursor: pointer;
          font-size: 1.1rem;
        }
        .booking-form, .auth-form {
          display: flex;
          flex-direction: column;
          gap: 18px;
        }
        .field-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .field-row {
          display: flex;
          gap: 16px;
        }
        .field-row .field-group {
          flex: 1;
        }
        label {
          font-size: 0.85rem;
          color: #cbd5e1;
          font-weight: 500;
        }
        input, select, textarea {
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 8px;
          padding: 12px 14px;
          color: #ffffff;
          font-size: 0.95rem;
          font-family: inherit;
          transition: border-color 0.15s ease;
          box-sizing: border-box;
          width: 100%;
        }
        input:focus, select:focus, textarea:focus {
          outline: none;
          border-color: #38bdf8;
        }
        input::placeholder, textarea::placeholder {
          color: #64748b;
        }
        textarea {
          resize: vertical;
          min-height: 80px;
        }
        .btn-action {
          background: #38bdf8;
          color: #0f172a;
          border: none;
          border-radius: 8px;
          padding: 14px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background-color 0.15s ease;
          margin-top: 6px;
        }
        .btn-action:hover {
          background: #7dd3fc;
        }
        .auth-toggle-text {
          text-align: center;
          font-size: 0.875rem;
          color: #94a3b8;
          margin-top: 14px;
        }
        .auth-toggle-link {
          color: #38bdf8;
          cursor: pointer;
          text-decoration: underline;
        }
        .auth-toggle-link:hover {
          color: #7dd3fc;
        }
        .panel-title {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0 0 16px 0;
          color: #ffffff;
          border-bottom: 1px solid #334155;
          padding-bottom: 12px;
          text-align: center;
        }
        .table-responsive {
          overflow-x: auto;
        }
        .admin-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
          font-size: 0.85rem;
        }
        .admin-table th {
          color: #94a3b8;
          font-weight: 600;
          padding: 10px 8px;
          border-bottom: 2px solid #334155;
        }
        .admin-table td {
          padding: 10px 8px;
          border-bottom: 1px solid #334155;
          color: #e2e8f0;
          white-space: nowrap;
        }
        .btn-delete {
          background: rgba(239, 68, 68, 0.15);
          color: #f87171;
          border: 1px solid rgba(239, 68, 68, 0.3);
          padding: 4px 10px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.75rem;
          transition: all 0.15s ease;
        }
        .btn-delete:hover {
          background: #ef4444;
          color: #ffffff;
        }
        .btn-logout {
          background: transparent;
          color: #94a3b8;
          border: 1px solid #334155;
          padding: 6px 12px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.8 habit;
          transition: all 0.15s ease;
        }
        .btn-logout:hover {
          background: #334155;
          color: #ffffff;
        }
        .header-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          width: 100%;
          max-width: 460px;
        }
        .empty-message {
          text-align: center;
          color: #64748b;
          padding: 16px;
          font-style: italic;
          font-size: 0.9rem;
        }
        .workspace-footer {
          text-align: center;
          font-size: 0.8rem;
          color: #64748b;
          margin-top: 8px;
          width: 100%;
        }
      `,
        }}
      />

      {notification.show && (
        <div style={{ width: "100%", maxWidth: "460px" }}>
          <div className={`toast-alert ${notification.type}`}>
            <span>{notification.message}</span>
            <button
              className="alert-close-btn"
              onClick={() => setNotification({ ...notification, show: false })}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {!isAuthenticated ? (
        <div className="auth-card">
          <div className="workspace-header">
            <h1>{authMode === "login" ? "Iniciar Sesión" : "Crear Cuenta"}</h1>
            <p>
              {authMode === "login"
                ? "Ingresa tus credenciales para acceder al sistema"
                : "Regístrate para comenzar a gestionar tus espacios"}
            </p>
          </div>

          <form className="auth-form" onSubmit={handleAuthSubmit}>
            {authMode === "register" && (
              <div className="field-group">
                <label>Nombre Completo</label>
                <input
                  type="text"
                  name="nombre_completo"
                  placeholder="Ej. Juan Pérez"
                  required
                  value={authFormData.nombre_completo || ""}
                  onChange={handleAuthChange}
                />
              </div>
            )}

            <div className="field-group">
              <label>Correo Electrónico</label>
              <input
                type="email"
                name="email"
                placeholder="correo@ejemplo.com"
                required
                value={authFormData.email}
                onChange={handleAuthChange}
              />
            </div>

            <div className="field-group">
              <label>Contraseña</label>
              <input
                type="password"
                name="password"
                placeholder="••••••••"
                required
                value={authFormData.password}
                onChange={handleAuthChange}
              />
            </div>

            <button type="submit" className="btn-action">
              {authMode === "login" ? "Ingresar" : "Registrarse"}
            </button>
          </form>

          <div className="auth-toggle-text">
            {authMode === "login" ? (
              <>
                ¿No tienes una cuenta?{" "}
                <span
                  className="auth-toggle-link"
                  onClick={() => setAuthMode("register")}
                >
                  Regístrate aquí
                </span>
              </>
            ) : (
              <>
                ¿Ya tienes una cuenta?{" "}
                <span
                  className="auth-toggle-link"
                  onClick={() => setAuthMode("login")}
                >
                  Inicia sesión
                </span>
              </>
            )}
          </div>
        </div>
      ) : (
        <>
          <div className="header-row">
            <span
              style={{
                fontSize: "0.85rem",
                color: "#38bdf8",
                fontWeight: "500",
              }}
            >
              👤 Sesión:{" "}
              <span style={{ color: "#ffffff", fontWeight: "700" }}>
                {userName}
              </span>{" "}
              ({userEmail})
            </span>
            <button className="btn-logout" onClick={handleLogout}>
              Cerrar Sesión
            </button>
          </div>

          <div className="app-workspace">
            <div className="workspace-header">
              <h1>Asignación de Reservas</h1>
            </div>

            <form className="booking-form" onSubmit={handleSubmit}>
              <div className="field-group">
                <label>Nombre del Asistente</label>
                <input
                  type="text"
                  name="nombre_completo"
                  placeholder="Nombre de quien asistirá"
                  required
                  value={formData.nombre_completo}
                  onChange={handleChange}
                />
              </div>

              <div className="field-group">
                <label>Correo de Contacto</label>
                <input
                  type="email"
                  name="email"
                  placeholder="correo@contacto.com"
                  required
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>

              <div className="field-group">
                <label>Tipo de Recurso</label>
                <select
                  name="recurso_id"
                  required
                  value={formData.recurso_id}
                  onChange={handleChange}
                >
                  <option value="">Seleccionar recurso...</option>
                  {recursosList.map((rec) => (
                    <option key={rec.id} value={rec.id}>
                      {rec.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field-row">
                <div className="field-group">
                  <label>Fecha</label>
                  <input
                    type="date"
                    name="fecha"
                    min={today}
                    required
                    value={formData.fecha}
                    onChange={handleChange}
                  />
                </div>

                <div className="field-group">
                  <label>Horario disponible</label>
                  <select
                    name="hora"
                    required
                    value={formData.hora}
                    onChange={handleChange}
                  >
                    <option value="">Seleccionar...</option>
                    {/* 🌟 CAMBIO AQUÍ: Renderizado dinámico conectado a la base de datos */}
                    {horariosList.map((h) => (
                      <option key={h.id} value={h.hora}>
                        {h.hora}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="field-group">
                <label>Notas o requerimientos (Opcional)</label>
                <textarea
                  name="notas"
                  placeholder="Escribe aquí si necesitas añadir algún detalle..."
                  value={formData.notas}
                  onChange={handleChange}
                ></textarea>
              </div>

              <button type="submit" className="btn-action">
                Confirmar Reserva
              </button>
            </form>
          </div>

          <div className="admin-panel">
            <div className="panel-title">📋 Mis Reservas</div>
            <div className="table-responsive">
              {reservationsList.length === 0 ? (
                <div className="empty-message">
                  No tienes ninguna reserva registrada.
                </div>
              ) : (
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Asistente / Recurso</th>
                      <th>Fecha/Hora</th>
                      <th>Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reservationsList.map((res) => (
                      <tr key={res.id}>
                        <td>
                          <div style={{ fontWeight: "600" }}>
                            {res.nombre_completo}
                          </div>
                          <div
                            style={{
                              fontSize: "0.8rem",
                              color: "#38bdf8",
                              margin: "2px 0",
                            }}
                          >
                            📍 {res.recurso ? res.recurso.nombre : "General"}
                          </div>
                          <div
                            style={{ fontSize: "0.75rem", color: "#64748b" }}
                          >
                            {res.notas ? `📝 ${res.notas}` : "Sin notas"}
                          </div>
                        </td>
                        <td>
                          <div>{res.fecha}</div>
                          <div style={{ color: "#38bdf8", fontSize: "0.8rem" }}>
                            {res.hora}
                          </div>
                        </td>
                        <td>
                          <button
                            className="btn-delete"
                            onClick={() => handleDelete(res.id)}
                          >
                            ×
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </>
      )}

      <div className="workspace-footer">
        Alkemy Cloud Architecture • Conexión Segura
      </div>
    </>
  );
}

export default App;
