import ast
import sys
import os
from Parser import CFGBuilder
from CfgBuilder import CfgDiagrammBuilder

def get_input_code():
    """Handles user input from file path or direct console entry."""
    print("=== Python CFG Generator ===")
    print("Option 1: Enter a path to a .py file")
    print("Option 2: Paste code directly (type 'EOF' on a new line to finish)")
    
    user_input = input("\nInput: ").strip()

    # Check if input is a valid file path
    if os.path.isfile(user_input):
        try:
            with open(user_input, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    else:
        # Multi-line input mode
        print("Direct mode: Paste your code (type 'EOF' to confirm):")
        lines = [user_input]
        while True:
            line = sys.stdin.readline()
            if line.strip() == "EOF":
                break
            lines.append(line)
        return "".join(lines)

def main():
    source = get_input_code()
    if not source or not source.strip():
        print("No valid code provided. Exiting.")
        return

    try:
        # Validate syntax
        tree = ast.parse(source)
        
        # Build logical structure
        parser = CFGBuilder()
        nodes, edges = parser.build(tree)

        # Generate visualization
        diagram_builder = CfgDiagrammBuilder()
        graph = diagram_builder.createGraph(nodes, edges)

        # Render and save
        output_file = "cfg_output"
        graph.render("cfg_output", format="png", cleanup=True, view=False)
        print(f"\nSuccess! Diagram saved as '{output_file}.png'.")
        
    except SyntaxError as e:
        print(f"\n[SYNTAX ERROR]: Line {e.lineno}: {e.msg}")
        print(f"Offending code: {e.text.strip() if e.text else ''}")
    except Exception as e:
        print(f"\n[ERROR]: {e}")

if __name__ == "__main__":
    main()
