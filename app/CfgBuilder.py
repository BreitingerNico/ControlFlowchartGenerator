import graphviz

class CfgDiagrammBuilder: 
    """
    Diese Klasse nimmt die logischen Daten (Nodes und Edges) vom Parser entgegen
    und transformiert sie in eine grafische Darstellung mittels Graphviz.
    """

    def __init__(self):
        self.dot = graphviz.Digraph(comment='Control Flow Graph', engine='dot')
        self.dot.attr(nodesep='0.5', ranksep='0.5')
        self.dot.attr('node', 
                      fontname='Segoe UI,Arial,sans-serif', 
                      fontsize='10', 
                      color='#475569',  
                      penwidth='1.2',    
                      style='filled, rounded') 
        
        self.dot.attr('edge', 
                      color='#64748b',  
                      arrowsize='0.8', 
                      penwidth='1.0')

    def createGraph(self, nodes, edges):
        for node in nodes:
            shape = self._determine_shape(node.label)
            color = self._determine_color(node.label)
            
            self.dot.node(
                name=str(node.id), 
                label=node.label, 
                shape=shape, 
                style='filled', 
                fillcolor=color
            )

        for src_node, dst_node in edges:
            self.dot.edge(str(src_node.id), str(dst_node.id))

        return self.dot

    def _determine_shape(self, label):
        label_lower = label.lower().strip() # strip() entfernt führende Leerzeichen
        
        # Erweiterte Prüfung für Kontrollfluss-Keywords
        if label_lower.startswith(("if ", "while ", "for ", "try", "except")):
            return "diamond"
        
        elif any(x in label_lower for x in ["entry", "exit", "break", "continue", "return", "end "]):
            return "ellipse"
        
        else:
            return "rectangle"

    def _determine_color(self, label):
        label_lower = label.lower().strip()
        
        if "entry" in label_lower: 
            return "#D1FAE5" 
            
        if any(x in label_lower for x in ["exit", "end ", "return"]): 
            return "#F9C2C2" 
            
        if label_lower.startswith(("if ", "while ", "for ", "try", "except", "finally")): 
            return "#FAF3D7" 
            
        return "#CFE3F7"
