"""
Notebook Runner Utility
Executes Jupyter Notebook (.ipynb) files sequentially in the console,
displaying markdown headers, cell outputs, and rendering Matplotlib plots.
"""

import ast
import json
import os
import sys
import traceback
from pathlib import Path

# Force unbuffered standard output for real-time console feedback
sys.stdout.reconfigure(line_buffering=True)


def execute_cell(code_str: str, global_vars: dict, cell_idx: int, nb_name: str) -> bool:
    """Executes a single code cell, automatically displaying the last expression value (like Jupyter)."""
    if not code_str.strip():
        return True

    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        print(f"[SYNTAX ERROR in Cell {cell_idx}]: {e}")
        return False

    if not tree.body:
        return True

    try:
        # If the last AST node is an expression (e.g. df.head(), variable name, arithmetic),
        # evaluate and display its output just like Jupyter does.
        if isinstance(tree.body[-1], ast.Expr):
            exec_body = tree.body[:-1]
            eval_expr = tree.body[-1]

            if exec_body:
                exec_mod = ast.Module(body=exec_body, type_ignores=[])
                exec(compile(exec_mod, f"<{nb_name}_cell_{cell_idx}>", "exec"), global_vars)

            expr_mod = ast.Expression(body=eval_expr.value)
            result = eval(compile(expr_mod, f"<{nb_name}_cell_{cell_idx}>", "eval"), global_vars)
            if result is not None:
                print(result)
        else:
            exec(compile(tree, f"<{nb_name}_cell_{cell_idx}>", "exec"), global_vars)
        return True
    except Exception as e:
        print(f"\n[ERROR in Cell {cell_idx}]: {e}")
        traceback.print_exc()
        return False


def run_notebook(notebook_path: str) -> bool:
    """Loads a .ipynb file and runs all markdown and code cells."""
    path = Path(notebook_path).resolve()
    if not path.exists():
        print(f"[ERROR] Notebook file not found: {path}")
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read notebook JSON: {e}")
        return False

    print("\n" + "=" * 70)
    print(f"  RUNNING NOTEBOOK: {path.name}")
    print(f"  Path: {path}")
    print("=" * 70 + "\n")

    orig_cwd = os.getcwd()
    # Change working directory to the notebook's folder so relative datasets (CSV, images) resolve properly
    os.chdir(path.parent)

    namespace = {
        "__name__": "__main__",
        "__file__": str(path),
    }

    cells = nb.get("cells", [])
    total_code_cells = sum(1 for c in cells if c.get("cell_type") == "code")
    code_count = 0

    success = True
    for cell in cells:
        cell_type = cell.get("cell_type")
        source = "".join(cell.get("source", []))

        if cell_type == "markdown":
            headers = [line.strip() for line in source.splitlines() if line.strip().startswith("#")]
            if headers:
                print("\n" + "-" * 50)
                print("\n".join(headers))
                print("-" * 50)
        elif cell_type == "code":
            code_count += 1
            print(f"\n>>> [Cell {code_count}/{total_code_cells}] Running code...")
            ok = execute_cell(source, namespace, code_count, path.name)
            if not ok:
                success = False
                print(f"[WARNING] Stopped at Cell {code_count} due to an error.")
                break

    os.chdir(orig_cwd)

    print("\n" + "=" * 70)
    if success:
        print(f" [SUCCESS] Successfully executed all {code_count} code cells in {path.name}!")
    else:
        print(f" [FAILED] Execution failed during notebook run.")
    print("=" * 70 + "\n")

    return success


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_nb = sys.argv[1]
    else:
        target_nb = os.path.join("BOOTCAMP ON AI_Practicals", "Day_1.ipynb")

    ok = run_notebook(target_nb)
    sys.exit(0 if ok else 1)
