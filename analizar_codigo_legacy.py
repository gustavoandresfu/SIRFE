import ast
import json
import os
import argparse
from typing import List
from modelos import MethodMetadata, MethodIR

class UniversalIRAnalyzer(ast.NodeVisitor):
    def __init__(self, config_path="config_analizador.json", filter_method=None):
        self.methods_ir: List[MethodMetadata] = []
        self.filter_method = filter_method
        self.load_config(config_path)

    def load_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            full_config = json.load(f)
            profile_name = full_config.get("active_profile", "generic")
            self.profile = full_config["profiles"].get(profile_name, {})

    def analyze_method(self, node, class_name):
        # Filtro quirúrgico por nombre de método
        if self.filter_method and node.name != self.filter_method:
            return

        method_name = node.name.lower()
        returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
        has_logic = any(isinstance(n, (ast.If, ast.While, ast.For)) for n in ast.walk(node))
        
        role = "EXTRACTOR"
        if any(isinstance(n, ast.Raise) for n in ast.walk(node)):
            role = "GUARD"
        elif not returns and has_logic:
            role = "PERSISTER"
        elif returns and has_logic:
            role = "TRANSFORMER"

        calls = [n.func.attr for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        effect = "STABLE"
        if any(c in self.profile.get("mutable_calls", []) for c in calls):
            effect = "MUTABLE"
        elif any(c in self.profile.get("signal_calls", []) for c in calls):
            effect = "SIGNAL"

        context = "GENERIC"
        full_text = (method_name + class_name).lower()
        if any(w in full_text for w in self.profile.get("identity_contexts", [])):
            context = "IDENTITY"
        elif any(w in full_text for w in self.profile.get("storage_contexts", [])):
            context = "STORAGE"
        elif any(w in full_text for w in self.profile.get("ui_contexts", [])):
            context = "UI_CONFIG"

        op_type = "SEQUENTIAL"
        if has_logic:
            branches = [n for n in ast.walk(node) if isinstance(n, ast.If)]
            op_type = "BRANCHING" if len(branches) < 3 else "COMPLEX_BRANCHING"

        ir_obj = MethodIR(role=role, effect=effect, op_type=op_type, context=context)
        self.methods_ir.append(MethodMetadata(class_name=class_name, method=node.name, ir=ir_obj))

    def visit_ClassDef(self, node):
        class_name = node.name
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.analyze_method(item, class_name)
        self.generic_visit(node)

def analizar(path: str, config_path: str = "config_analizador.json", filter_method: str = None) -> List[MethodMetadata]:
    analyzer = UniversalIRAnalyzer(config_path=config_path, filter_method=filter_method)
    
    files_to_process = []
    if os.path.isfile(path):
        files_to_process.append(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".py"): 
                    files_to_process.append(os.path.join(root, f))

    for file_path in files_to_process:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
                analyzer.visit(tree)
            except SyntaxError as e:
                print(f"Error de sintaxis al parsear {file_path}: {e}")
    
    return analyzer.methods_ir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analizador Semántico Universal")
    parser.add_argument("path", help="Ruta al archivo .py o directorio")
    parser.add_argument("--method", help="Filtrar por un método específico", default=None)
    parser.add_argument("--config", help="Ruta al archivo de configuración", default="config_analizador.json")
    args = parser.parse_args()

    resultados = analizar(args.path, config_path=args.config, filter_method=args.method)
    
    # Escribir a JSON para mantener compatibilidad
    with open("representacion_intermedia_semantica.json", "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in resultados], f, indent=4)
    
    print(f"Procesados {len(resultados)} métodos.")
