import ast
from typing import List, Tuple, Optional


class CFGNode:
    _id_counter = 0

    def __init__(self, label: str):
        self.id = CFGNode._id_counter
        CFGNode._id_counter += 1
        self.label = label

    def __repr__(self):
        return f"Node({self.id}: {self.label})"

class CFGBuilder(ast.NodeVisitor):

    def __init__(self):
        self.nodes: List[CFGNode] = []
        self.edges: List[Tuple[CFGNode, CFGNode]] = []

        self.current: Optional[CFGNode] = None
        self.loop_stack: List[CFGNode] = []  # for break/continue targets

    def new_node(self, label: str) -> CFGNode:
        node = CFGNode(label)
        self.nodes.append(node)
        return node

    def connect(self, src: Optional[CFGNode], dst: CFGNode):
        if src is not None:
            self.edges.append((src, dst))

    # entry
    def build(self, tree: ast.AST):
        entry = self.new_node("ENTRY")
        self.current = entry

        self.visit(tree)

        exit_node = self.new_node("EXIT")
        if self.current is not None:
            self.connect(self.current, exit_node)
        else:
            if self.nodes:
                last_node = self.nodes[-2] 
                self.connect(last_node, exit_node)

        return self.nodes, self.edges
    
    def visit_Module(self, node: ast.Module):
        for stmt in node.body:
            self.visit(stmt)

    def generic_statement(self, node, label=None):
        # if there's no label given, choose code instead
        display_label = label if label else ast.unparse(node)
        stmt_node = self.new_node(display_label)
        self.connect(self.current, stmt_node)
        self.current = stmt_node

    def visit_Assign(self, node: ast.Assign):
        self.generic_statement(node)
        
    def visit_AugAssign(self, node: ast.AugAssign):
        # for operations like 'index += 1'
        self.generic_statement(node)

    def visit_Expr(self, node: ast.Expr):
        self.generic_statement(node)

    def visit_Return(self, node: ast.Return):
        display_label = f"return {ast.unparse(node.value)}" if node.value else "return"
        return_node = self.new_node(display_label)
        self.connect(self.current, return_node)
        self.current = return_node

    # ---------- IF ----------

    def visit_If(self, node: ast.If):
        condition_text = f"if {ast.unparse(node.test)}:"
        if_node = self.new_node(condition_text)
        self.connect(self.current, if_node)
        
        self.current = if_node
        for stmt in node.body:
            self.visit(stmt)
        then_end = self.current

        self.current = if_node
        for stmt in node.orelse:
            self.visit(stmt)
        else_end = self.current

        """
        merge = self.new_node("Merge")

        if then_end:
            self.connect(then_end, merge)
        if else_end:
            self.connect(else_end, merge)

        self.current = merge """

    # ---------- WHILE ----------
    def visit_While(self, node: ast.While):
        # Bedingung extrahieren, z.B. "while x < 10:"
        condition_text = f"while {ast.unparse(node.test)}:"
        while_node = self.new_node(condition_text)
        self.connect(self.current, while_node)

        loop_exit = self.new_node(f"End {condition_text}")
        self.loop_stack.append(loop_exit)

        # Body
        self.current = while_node
        for stmt in node.body:
            self.visit(stmt)

        # Rückkante zur Bedingung
        if self.current:
            self.connect(self.current, while_node)

        # Exit-Kante (wenn Bedingung falsch ist)
        self.connect(while_node, loop_exit)
        self.loop_stack.pop()
        self.current = loop_exit

    # ---------- FOR ----------
    def visit_For(self, node: ast.For):
        # Wichtig: "for " am Anfang für die Erkennung im Builder
        for_text = f"for {ast.unparse(node.target)} in {ast.unparse(node.iter)}:"
        for_node = self.new_node(for_text)
        self.connect(self.current, for_node)

        loop_exit = self.new_node(f"End {for_text}")
        self.loop_stack.append(loop_exit)

        self.current = for_node
        for stmt in node.body:
            self.visit(stmt)

        if self.current:
            self.connect(self.current, for_node)

        self.connect(for_node, loop_exit)
        self.loop_stack.pop()
        self.current = loop_exit

    # ---------- TRY / EXCEPT / FINALLY ----------
    def visit_Try(self, node: ast.Try):
        try_node = self.new_node("try:")
        self.connect(self.current, try_node)
        
        finally_node = self.new_node("finally:")

        self.current = try_node
        for stmt in node.body:
            self.visit(stmt)
        if self.current:
            self.connect(self.current, finally_node)

        for handler in node.handlers:
            exc_label = "except"
            if handler.type:
                exc_label += f" {ast.unparse(handler.type)}"
            except_node = self.new_node(f"{exc_label}:")
            self.connect(try_node, except_node)

            self.current = except_node
            for stmt in handler.body:
                self.visit(stmt)
            if self.current:
                self.connect(self.current, finally_node)

        self.current = finally_node
        for stmt in node.finalbody:
            self.visit(stmt)
