import ast
import json
import os
import argparse
import re
from typing import List, Dict, Any
from modelos import SemanticUnit, TraceabilityMetadata

class UniversalIRAnalyzer(ast.NodeVisitor):
    def __init__(self, config_path="config_analizador.json", filter_method=None, file_path=""):
        self.units: List[SemanticUnit] = []
        self.filter_method = filter_method
        self.file_path = file_path
        self.load_config(config_path)

    def load_config(self, path):
        # Intentar cargar configuración; si no existe, usar valores por defecto
        try:
            with open(path, "r", encoding="utf-8") as f:
                full_config = json.load(f)
                profile_name = full_config.get("active_profile", "legacy")
                self.profile = full_config["profiles"].get(profile_name, {})
        except Exception:
            self.profile = {
                "mutable_calls": ["write", "create", "delete", "update", "save"],
                "signal_calls": ["send", "trigger", "emit", "rpc"],
                "identity_contexts": ["user", "group", "password", "session", "login", "auth"],
                "storage_contexts": ["table", "db", "mmap", "cache", "pool"],
                "ui_contexts": ["menu", "view", "interface", "preference", "avatar"]
            }

    def _extract_action_name(self, method_name: str) -> str:
        # Convierte snake_case o camelCase a formato de Acción (ej. guardar_usuario -> GuardarUsuario)
        words = re.findall(r'[A-Za-z0-9]+', method_name)
        return "".join(w.capitalize() for w in words)

    def _get_node_source_code(self, node) -> str:
        # Intenta obtener una representación textual simple del nodo de comparación o condición
        if isinstance(node, ast.Compare):
            left = self._get_node_source_code(node.left)
            ops = []
            for op in node.ops:
                if isinstance(op, ast.Eq): ops.append("==")
                elif isinstance(op, ast.NotEq): ops.append("!=")
                elif isinstance(op, ast.Lt): ops.append("<")
                elif isinstance(op, ast.LtE): ops.append("<=")
                elif isinstance(op, ast.Gt): ops.append(">")
                elif isinstance(op, ast.GtE): ops.append(">=")
                elif isinstance(op, ast.Is): ops.append("is")
                elif isinstance(op, ast.IsNot): ops.append("is not")
                elif isinstance(op, ast.In): ops.append("in")
                elif isinstance(op, ast.NotIn): ops.append("not in")
                else: ops.append("?")
            comparators = [self._get_node_source_code(c) for c in node.comparators]
            parts = [left]
            for op, comp in zip(ops, comparators):
                parts.append(op)
                parts.append(comp)
            return " ".join(parts)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_source_code(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.UnaryOp):
            op_str = "not " if isinstance(node.op, ast.Not) else "-"
            return f"{op_str}{self._get_node_source_code(node.operand)}"
        elif isinstance(node, ast.BoolOp):
            op_str = " and " if isinstance(node.op, ast.And) else " or "
            return f"({op_str.join(self._get_node_source_code(v) for v in node.values)})"
        elif isinstance(node, ast.BinOp):
            op_map = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%"}
            op_str = op_map.get(type(node.op), "?")
            return f"({self._get_node_source_code(node.left)} {op_str} {self._get_node_source_code(node.right)})"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_node_source_code(node.value)}[{self._get_node_source_code(node.slice)}]"
        elif isinstance(node, ast.Index):
            return self._get_node_source_code(node.value)
        elif isinstance(node, ast.Slice):
            lower = self._get_node_source_code(node.lower) if node.lower else ""
            upper = self._get_node_source_code(node.upper) if node.upper else ""
            return f"{lower}:{upper}"
        elif isinstance(node, ast.Call):
            args_str = ", ".join(self._get_node_source_code(a) for a in node.args)
            return f"{self._get_node_source_code(node.func)}({args_str})"
        return str(node)

    def analyze_method(self, node: ast.FunctionDef, class_name: str):
        if self.filter_method and node.name != self.filter_method:
            return

        method_name = node.name
        
        # 1. Trazabilidad
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line)
        traceability = TraceabilityMetadata(
            file_path=self.file_path,
            class_name=class_name,
            name=method_name,
            start_line=start_line,
            end_line=end_line,
            node_type="FunctionDef"
        )

        # 2. Análisis del AST - Recorrido de Nodos
        all_nodes = list(ast.walk(node))
        returns = [n for n in all_nodes if isinstance(n, ast.Return)]
        raises = [n for n in all_nodes if isinstance(n, ast.Raise)]
        assertions = [n for n in all_nodes if isinstance(n, ast.Assert)]
        calls_nodes = [n for n in all_nodes if isinstance(n, ast.Call)]
        assigns = [n for n in all_nodes if isinstance(n, ast.Assign)]

        # 3. Roles Múltiples y Confianzas (Heurísticas)
        roles = []
        if raises or assertions:
            roles.append({"role": "VALIDATOR", "confidence": 1.0})
        
        # Detectar lógica condicional interna que actúa como guardia
        has_guards = False
        for child in node.body:
            if isinstance(child, ast.If):
                # Si el cuerpo del IF tiene raise o return de error/None al principio del método
                sub_returns = [n for n in ast.walk(child) if isinstance(n, ast.Return)]
                sub_raises = [n for n in ast.walk(child) if isinstance(n, ast.Raise)]
                if sub_raises or (sub_returns and len(child.body) <= 2):
                    has_guards = True
        
        if has_guards and not any(r["role"] == "VALIDATOR" for r in roles):
            roles.append({"role": "VALIDATOR", "confidence": 0.8})

        # Detectar Persistencia
        called_names = []
        dependencies = set()
        for call in calls_nodes:
            if isinstance(call.func, ast.Attribute):
                attr_name = call.func.attr
                called_names.append(attr_name)
                # Extraer la dependencia (ej. self.user_repository -> user_repository)
                base = self._get_node_source_code(call.func.value)
                if base.startswith("self."):
                    dep = base.replace("self.", "")
                    dependencies.add(dep)
            elif isinstance(call.func, ast.Name):
                called_names.append(call.func.id)

        has_persistence = any(c in self.profile.get("mutable_calls", []) for c in called_names)
        if has_persistence:
            roles.append({"role": "PERSISTER", "confidence": 0.95})

        # Detectar Extractor / Transformador
        has_return_data = False
        for ret in returns:
            if ret.value is not None:
                if not (isinstance(ret.value, ast.Constant) and ret.value.value is None):
                    has_return_data = True
        
        has_loops = any(isinstance(n, (ast.For, ast.While)) for n in all_nodes)
        
        if has_return_data:
            roles.append({"role": "EXTRACTOR", "confidence": 0.90})
            if has_loops or len(assigns) > 2:
                roles.append({"role": "TRANSFORMER", "confidence": 0.80})

        if not roles:
            roles.append({"role": "EXTRACTOR", "confidence": 0.50})  # Rol por defecto de baja confianza

        # 4. Acciones y Confianza
        actions = []
        action_name = self._extract_action_name(method_name)
        # Buscar verbos comunes en el nombre del método
        verb_pattern = r'^(save|create|update|delete|write|send|validate|check|get|fetch|remove|add|authenticate|login|logout)'
        if re.match(verb_pattern, method_name.lower()):
            actions.append({"action": action_name, "confidence": 0.90})
        else:
            actions.append({"action": action_name, "confidence": 0.70})

        # 5. Entradas y Salidas
        inputs = []
        for arg in node.args.args:
            if arg.arg not in ("self", "cls"):
                inputs.append(arg.arg)

        outputs = []
        if node.returns:
            outputs.append(self._get_node_source_code(node.returns))
        else:
            # Deducir de los returns encontrados
            for ret in returns:
                if ret.value:
                    if isinstance(ret.value, ast.Constant):
                        val_type = type(ret.value.value).__name__
                        if val_type not in outputs:
                            outputs.append(val_type)
                    elif isinstance(ret.value, ast.Name):
                        if ret.value.id not in outputs:
                            outputs.append(ret.value.id)
            if not outputs and returns:
                outputs.append("None")

        # 6. Llamadas y Dependencias
        calls = []
        for call in calls_nodes:
            call_str = self._get_node_source_code(call.func)
            calls.append(call_str)

        # 7. Cambios de Estado
        memory_change = False
        for assign in assigns:
            for target in assign.targets:
                if isinstance(target, ast.Attribute) and self._get_node_source_code(target.value) == "self":
                    memory_change = True
        
        persistent_change = has_persistence
        external_change = any(c in self.profile.get("signal_calls", []) for c in called_names)
        
        state_changes = {
            "persistent": persistent_change,
            "memory": memory_change,
            "external": external_change
        }

        # 8. Excepciones
        exceptions = []
        for raise_node in raises:
            if raise_node.exc:
                if isinstance(raise_node.exc, ast.Call) and isinstance(raise_node.exc.func, ast.Name):
                    exceptions.append(raise_node.exc.func.id)
                elif isinstance(raise_node.exc, ast.Name):
                    exceptions.append(raise_node.exc.id)
        
        # También buscar excepciones atrapadas en try-except
        for handler in [n for n in all_nodes if isinstance(n, ast.ExceptHandler)]:
            if isinstance(handler.type, ast.Name):
                exceptions.append(handler.type.id)
            elif isinstance(handler.type, ast.Tuple):
                for el in handler.type.elts:
                    if isinstance(el, ast.Name):
                        exceptions.append(el.id)

        exceptions = list(set(exceptions))

        # 9. Precondiciones
        preconditions = []
        for child in node.body:
            if isinstance(child, ast.If):
                # Extraer la condición del IF
                cond_str = self._get_node_source_code(child.test)
                # Si el if contiene un raise o return de error, asumimos que es una precondición
                sub_returns = [n for n in ast.walk(child) if isinstance(n, ast.Return)]
                sub_raises = [n for n in ast.walk(child) if isinstance(n, ast.Raise)]
                if sub_raises or sub_returns:
                    preconditions.append(cond_str)
            elif isinstance(child, ast.Assert):
                cond_str = self._get_node_source_code(child.test)
                preconditions.append(cond_str)

        # 10. Postcondiciones
        postconditions = []
        if persistent_change:
            postconditions.append("Persistencia de datos actualizada")
        if memory_change:
            postconditions.append("Estado en memoria actualizado")
        if external_change:
            postconditions.append("Señal o evento externo emitido")
        if outputs:
            postconditions.append(f"Retorna valor del tipo {', '.join(outputs)}")

        # 11. Dominio
        domain = "GENERIC"
        full_text = (method_name + class_name).lower()
        if any(w in full_text for w in self.profile.get("identity_contexts", [])):
            domain = "IDENTITY"
        elif any(w in full_text for w in self.profile.get("storage_contexts", [])):
            domain = "STORAGE"
        elif any(w in full_text for w in self.profile.get("ui_contexts", [])):
            domain = "UI_CONFIG"

        unit = SemanticUnit(
            traceability=traceability,
            roles=roles,
            actions=actions,
            inputs=inputs,
            outputs=outputs,
            dependencies=list(dependencies),
            calls=calls,
            state_changes=state_changes,
            exceptions=exceptions,
            preconditions=preconditions,
            postconditions=postconditions,
            domain=domain
        )
        self.units.append(unit)

    def visit_ClassDef(self, node):
        class_name = node.name
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.analyze_method(item, class_name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Maneja funciones a nivel de módulo (sin clase)
        # Si ya se analizó como parte de una clase, evitamos duplicar
        # Para esto, ast.NodeVisitor visita recursivamente. El visit_ClassDef llamará a analyze_method,
        # pero para evitar que visit_FunctionDef vuelva a analizar el método de la clase de manera aislada,
        # chequeamos si el padre directo es un ClassDef. 
        # En Python no hay parent pointer por defecto en AST, así que llevamos el control en visit_ClassDef.
        # Por lo tanto, si está a nivel de módulo, class_name es vacío.
        # Para evitar doble visita, podemos validar si ya está en traceability.
        already_analyzed = any(u.traceability.name == node.name and u.traceability.start_line == node.lineno for u in self.units)
        if not already_analyzed:
            self.analyze_method(node, "")
        self.generic_visit(node)

def analizar(path: str, config_path: str = "config_analizador.json", filter_method: str = None) -> List[SemanticUnit]:
    files_to_process = []
    if os.path.isfile(path):
        files_to_process.append(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".py"):
                    files_to_process.append(os.path.join(root, f))

    all_units: List[SemanticUnit] = []
    for file_path in files_to_process:
        # Convertir a ruta absoluta para mejor legibilidad y trazabilidad
        abs_path = os.path.abspath(file_path).replace("\\", "/")
        analyzer = UniversalIRAnalyzer(config_path=config_path, filter_method=filter_method, file_path=abs_path)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
                analyzer.visit(tree)
                all_units.extend(analyzer.units)
            except SyntaxError as e:
                print(f"Error de sintaxis al parsear {file_path}: {e}")
    
    return all_units

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analizador Semántico Universal (SIR-FE)")
    parser.add_argument("path", help="Ruta al archivo .py o directorio")
    parser.add_argument("--method", help="Filtrar por un método específico", default=None)
    parser.add_argument("--config", help="Ruta al archivo de configuración", default="config_analizador.json")
    args = parser.parse_args()

    resultados = analizar(args.path, config_path=args.config, filter_method=args.method)
    
    with open("representacion_intermedia_semantica.json", "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in resultados], f, indent=4, ensure_ascii=False)
    
    print(f"Procesadas {len(resultados)} unidades semánticas.")
