"""
Módulo de ejemplo sintético para demostración reproducible de SIR-FE.

Propósito:
Este módulo está diseñado como un caso sintético para comprobar el análisis estático.
Contiene de forma explícita las estructuras y patrones sintácticos que las heurísticas
de SIR-FE detectan (guardas con raise/assert, persistencia mediante .write(), mutaciones
de atributos en self, transformaciones con bucles y emisión de eventos con .send()).

Para permitir además su ejecución interactiva directa en Python sin errores de runtime,
incluye implementaciones mínimas (mocks) de las dependencias externas (db y event_bus).
"""

class MockDatabase:
    """Simulador mínimo de almacenamiento para permitir ejecución en runtime."""
    def write(self, data):
        return True

class MockEventBus:
    """Simulador mínimo de bus de eventos para permitir ejecución en runtime."""
    def send(self, event_name, payload):
        return True

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.audit_log = []
        self.db = MockDatabase()
        self.event_bus = MockEventBus()

    def login(self, username, password):
        """Verifica credenciales del usuario (Heurística: VALIDATOR + EXTRACTOR)."""
        if not username or not password:
            raise ValueError("El usuario y la contrasenia son requeridos.")
        
        token = f"tok_{username}_123"
        self.active_sessions[username] = token
        return token

    def validate_session(self, token):
        """Valida si una sesión está activa (Heurística: EXTRACTOR / Guarda)."""
        if token is None or not token.startswith("tok_"):
            return False
        return token in self.active_sessions.values()

    def update_user_preferences(self, username, preferences):
        """Transforma preferencias y persiste cambios (Heurística: TRANSFORMER + PERSISTER)."""
        assert username in self.active_sessions
        
        sanitized = {}
        for key, val in preferences.items():
            sanitized[key.lower()] = str(val).strip()
            
        self.db.write(sanitized)
        self.audit_log.append(f"Actualizadas preferencias para {username}")
        return True

    def logout(self, username):
        """Cierra la sesión y emite notificación externa (Heurística: SIGNAL / EXTRACTOR)."""
        if username not in self.active_sessions:
            return None
        del self.active_sessions[username]
        self.event_bus.send("user_logged_out", username)
        return True

if __name__ == "__main__":
    # Comprobación de ejecución real en runtime
    print("=== Comprobación de Ejecución en Runtime del Ejemplo Sintético ===")
    manager = SessionManager()
    
    token = manager.login("usuario_demo", "clave_segura")
    print(f"1. Login exitoso -> Token: {token}")
    
    es_valida = manager.validate_session(token)
    print(f"2. Validación de sesión -> {es_valida}")
    
    manager.update_user_preferences("usuario_demo", {"Tema": " Oscuro ", "Idioma": " ES "})
    print("3. Preferencias actualizadas y guardadas en mock db")
    
    manager.logout("usuario_demo")
    print("4. Cierre de sesión y evento emitido a mock event_bus")
    print("Resultado: Ejecución en runtime completada sin errores.")
