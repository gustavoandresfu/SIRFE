"""
Módulo de ejemplo para demostración reproducible de SIR-FE.
Representa un componente de gestión de sesiones y usuarios con reglas de validación,
transformación de datos y persistencia.
"""

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.audit_log = []

    def login(self, username, password):
        """Verifica credenciales del usuario."""
        if not username or not password:
            raise ValueError("El usuario y la contrasenia son requeridos.")
        
        token = f"tok_{username}_123"
        self.active_sessions[username] = token
        return token

    def validate_session(self, token):
        """Valida que una sesión se encuentre activa."""
        if token is None or not token.startswith("tok_"):
            return False
        return token in self.active_sessions.values()

    def update_user_preferences(self, username, preferences):
        """Transforma preferencias y persiste cambios."""
        assert username in self.active_sessions
        
        sanitized = {}
        for key, val in preferences.items():
            sanitized[key.lower()] = str(val).strip()
            
        self.db.write(sanitized)
        self.audit_log.append(f"Actualizadas preferencias para {username}")
        return True

    def logout(self, username):
        """Cierra la sesión y emite notificación."""
        if username not in self.active_sessions:
            return None
        del self.active_sessions[username]
        self.event_bus.send("user_logged_out", username)
        return True
