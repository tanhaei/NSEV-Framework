# tests/test_analyzer.py
import unittest
from src.core.analyzer import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    """
    Unit tests for verifying structural analysis (Phases 2-5 & 7).
    """

    def test_loop_detection(self):
        """Tests Phase 2 & 3: Detection of for and while loops."""
        code = "for i in range(10): print(i)"
        analyzer = CodeAnalyzer(code)
        metadata = analyzer.analyze()
        
        self.assertEqual(len(metadata["loops"]), 1)
        self.assertEqual(metadata["loops"][0]["type"], "For")

    def test_function_strategy(self):
        """Tests Phase 5: Differentiation between Inlining and Abstraction."""
        code = """
def local_func(x):
    return x + 1

y = local_func(5)
z = external_lib_func(10)
        """
        analyzer = CodeAnalyzer(code)
        metadata = analyzer.analyze()
        
        # Checking local_func (Should be Inlining)
        local_call = next(f for f in metadata["functions"] if f["name"] == "local_func")
        self.assertEqual(local_call["strategy"], "Inlining")
        
        # Checking external_lib_func (Should be Abstraction)
        ext_call = next(f for f in metadata["functions"] if f["name"] == "external_lib_func")
        self.assertEqual(ext_call["strategy"], "Abstraction")

    def test_concurrency_detection(self):
        """Tests Phase 7: Identification of threading and multiprocessing."""
        code = "import threading\ndef task(): pass"
        analyzer = CodeAnalyzer(code)
        metadata = analyzer.analyze()
        
        self.assertTrue(metadata["concurrency_flags"])

    def test_branch_detection(self):
        """Tests Phase 4: Identification of If and Match constructs."""
        code = "if x > 0: return True"
        analyzer = CodeAnalyzer(code)
        metadata = analyzer.analyze()
        
        self.assertEqual(len(metadata["branches"]), 1)
        self.assertEqual(metadata["branches"][0]["type"], "If")

if __name__ == "__main__":
    unittest.main()
