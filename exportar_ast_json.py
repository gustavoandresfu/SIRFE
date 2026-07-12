import ast
import json
import os
import sys
import argparse

def ast_to_dict(node):
    result = {"_type": node.__class__.__name__}
    for field, value in ast.iter_fields(node):
        if isinstance(value, ast.AST):
            result[field] = ast_to_dict(value)
        elif isinstance(value, list):
            result[field] = [ast_to_dict(item) if isinstance(item, ast.AST) else item for item in value]
        else:
            result[field] = value
    if hasattr(node, "lineno"):
        result["lineno"] = node.lineno
    return result

def export_ast(src_path):
    if not os.path.exists(src_path):
        print(f"Error: No existe {src_path}")
        return
    
    with open(src_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    base_name = os.path.basename(src_path).replace(".py", "")
    output_path = f"ast_{base_name}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ast_to_dict(tree), f, indent=4, ensure_ascii=False)
    
    print(f"AST JSON exportado a: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exportador AST Dinámico")
    parser.add_argument("path", help="Ruta al archivo .py o carpeta")
    args = parser.parse_args()
    
    if os.path.isfile(args.path):
        export_ast(args.path)
    elif os.path.isdir(args.path):
        for root, dirs, files in os.walk(args.path):
            for file in files:
                if file.endswith(".py"):
                    export_ast(os.path.join(root, file))
