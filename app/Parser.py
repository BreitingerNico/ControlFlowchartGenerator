import ast
from typing import List, Tuple, Optional

class CFGNode:
    """Represents a single point (node) in the program's execution flow."""
    _id_counter = 0

    def __init__(self, label: str):
        self.id = CFGNode._id_counter
        CFGNode._id_counter += 1
        self.label = label

    def __repr__(self):
        return f"Node({self.id}: {self.label})"

class CFGBuilder(ast.NodeVisitor):
    """
    Analyzes Python code and builds a network of nodes and edges 
    representing the program's logical control flow.
    """

    def __init__(self):
        self.nodes: List[CFGNode] = []
        self.edges: List[Tuple[CFGNode, CFGNode]] = []
        # 'current' tracks the node from which the next connection will start
        self.current: Optional[CFGNode] = None
        # stack to handle loop exit points (crucial for break/continue logic)
        self.loop_stack: List[CFGNode] = [] 

    def new_node(self, label: str) -> CFGNode:
        """Creates a new node and adds it to the list of total nodes."""
        node = CFGNode(label)
        self.nodes.append(node)
        return node

    def connect(self, src: Optional[CFGNode], dst: CFGNode):
        """Creates a directed edge between two nodes."""
        if src is not None:
            self.edges.append((src, dst))

    def build(self, tree: ast.AST):
        """
        Main entry point: Initializes the ENTRY node, 
        traverses the tree, and concludes with the EXIT node.
        """
        entry = self.new_node("ENTRY")
        self.current = entry

        # Start the recursive traversal of the Abstract Syntax Tree (AST)
        self.visit(tree)

        # Connect the final processed statement to the EXIT node
        exit_node = self.new_node("EXIT")
        if self.current is not None:
            self.connect(self.current, exit_node)
        else:
            # Fallback for empty bodies or early returns
            if self.nodes:
                last_node = self.nodes[-2] 
                self.connect(last_node, exit_node)

        return self.nodes, self.edges
    
    def visit_Module(self, node: ast.Module):
        """Visits every statement in the main Python module."""
        for stmt in node.body:
            self.visit(stmt)

    def generic_statement(self, node, label=None):
        """Helper for standard statements (assignments, expressions, etc.)."""
        # ast.unparse converts the AST node back into readable Python code
        display_label = label if label else ast.unparse(node)
        stmt_node = self.new_node(display_label)
        self.connect(self.current, stmt_node)
        # The new statement becomes the starting point for the next one
        self.current = stmt_node

    def visit_Assign(self, node: ast.Assign):
        self.generic_statement(node)
        
    def visit_AugAssign(self, node: ast.AugAssign):
        # Handles operations like 'index += 1'
        self.generic_statement(node)

    def visit_Expr(self, node: ast.Expr):
        self.generic_statement(node)

    def visit_Return(self, node: ast.Return):
        """Creates a node for return statements and connects it."""
        display_label = f"return {ast.unparse(node.value)}" if node.value else "return"
        return_node = self.new_node(display_label)
        self.connect(self.current, return_node)
        self.current = return_node

    # ---------- IF STATEMENTS ----------

    def visit_If(self, node: ast.If):
        """Handles branching logic by creating divergent paths."""
        condition_text = f"if {ast.unparse(node.test)}:"
        if_node = self.new_node(condition_text)
        self.connect(self.current, if_node)
        
        # Path 1: If condition is True (body)
        self.current = if_node
        for stmt in node.body:
            self.visit(stmt)
        then_end = self.current

        # Path 2: If condition is False (orelse)
        self.current = if_node
        for stmt in node.orelse:
            self.visit(stmt)
        else_end = self.current

    # ---------- WHILE LOOPS ----------
    def visit_While(self, node: ast.While):
        """Handles while loops by creating a cycle back to the condition."""
        condition_text = f"while {ast.unparse(node.test)}:"
        while_node = self.new_node(condition_text)
        self.connect(self.current, while_node)

        # Node representing the point where the loop is finished/exited
        loop_exit = self.new_node(f"End {condition_text}")
        self.loop_stack.append(loop_exit)

        # Process the loop body
        self.current = while_node
        for stmt in node.body:
            self.visit(stmt)

        # Back-edge: After the body, flow returns to the condition check
        if self.current:
            self.connect(self.current, while_node)

        # Exit-edge: Triggered when the condition evaluates to False
        self.connect(while_node, loop_exit)
        self.loop_stack.pop()
        self.current = loop_exit

    # ---------- FOR LOOPS ----------
    def visit_For(self, node: ast.For):
        """Handles for loops similarly to while loops with iteration back-edges."""
        for_text = f"for {ast.unparse(node.target)} in {ast.unparse(node.iter)}:"
        for_node = self.new_node(for_text)
        self.connect(self.current, for_node)

        loop_exit = self.new_node(f"End {for_text}")
        self.loop_stack.append(loop_exit)

        # Process the loop body
        self.current = for_node
        for stmt in node.body:
            self.visit(stmt)

        # Back-edge to the header for the next iteration
        if self.current:
            self.connect(self.current, for_node)

        # Final edge to the exit node
        self.connect(for_node, loop_exit)
        self.loop_stack.pop()
        self.current = loop_exit

    # ---------- TRY / EXCEPT / FINALLY ----------
    def visit_Try(self, node: ast.Try):
        """Handles error handling and merges all paths into the 'finally' block."""
        try_node = self.new_node("try:")
        self.connect(self.current, try_node)
        
        finally_node = self.new_node("finally:")

        # 1. Normal execution path (Try block)
        self.current = try_node
        for stmt in node.body:
            self.visit(stmt)
        if self.current:
            self.connect(self.current, finally_node)

        # 2. Error paths (Except handlers)
        for handler in node.handlers:
            exc_label = "except"
            if handler.type:
                exc_label += f" {ast.unparse(handler.type)}"
            except_node = self.new_node(f"{exc_label}:")
            # Every exception path branches directly from the 'try:' node
            self.connect(try_node, except_node)

            self.current = except_node
            for stmt in handler.body:
                self.visit(stmt)
            # Every handler path merges into the 'finally' block
            if self.current:
                self.connect(self.current, finally_node)

        # 3. Final cleanup path (Finally block)
        self.current = finally_node
        for stmt in node.finalbody:
            self.visit(stmt)