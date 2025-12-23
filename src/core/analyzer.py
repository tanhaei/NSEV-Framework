import ast

class CodeAnalyzer:
    """
    Identifies code constructs to support Phases 2, 3, 4, 5, and 7[cite: 68, 153, 206].
    Extracts structural metadata for LLM-based Semantic Lifting.
    """

    def __init__(self, source_code):
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        # Identify local functions for Phase 5 selective inlining [cite: 173]
        self.local_defs = {node.name for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)}
        self.metadata = {
            "loops": [],
            "branches": [],
            "functions": [],
            "concurrency_flags": False
        }

    def analyze(self):
        """
        Main analysis loop to populate metadata for Phases 2-7[cite: 101, 153].
        """
        for node in ast.walk(self.tree):
            # Phase 2 & 3: Loops for Induction and Nesting [cite: 101, 131]
            if isinstance(node, (ast.For, ast.While)):
                self.metadata["loops"].append(self._get_node_info(node))
            
            # Phase 4: Complex Branches and Path Conditions [cite: 153-154]
            elif isinstance(node, (ast.If, ast.Match)):
                self.metadata["branches"].append(self._get_node_info(node))
            
            # Phase 5: Function Strategy (Inlining vs Abstraction) [cite: 171-172]
            elif isinstance(node, ast.Call):
                self._analyze_function_call(node)

            # Phase 7: Detecting Concurrency (threading/multiprocessing) [cite: 206, 211]
            elif self._is_concurrency_construct(node):
                self.metadata["concurrency_flags"] = True

        return self.metadata

    def _get_node_info(self, node):
        return {
            "type": type(node).__name__,
            "lineno": node.lineno,
            "end_lineno": getattr(node, "end_lineno", node.lineno)
        }

    def _analyze_function_call(self, node):
        """Phase 5: Decides between inlining and uninterpreted function modeling[cite: 173, 178]."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            strategy = "Inlining" if func_name in self.local_defs else "Abstraction"
            self.metadata["functions"].append({"name": func_name, "strategy": strategy})

    def _is_concurrency_construct(self, node):
        """Phase 7: Detects if the mutant affects concurrent behaviors[cite: 213, 220]."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ["threading", "multiprocessing"]:
                    return True
        return False