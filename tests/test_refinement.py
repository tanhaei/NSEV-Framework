# tests/test_refinement.py
import unittest
from src.core.refinement import RefinementEngine

class TestNSEVRefinement(unittest.TestCase):
    """
    تست‌های واحد برای تایید عملکرد Phase 8 (Self-Correction Loop).
    این تست‌ها سناریوهای مختلف بازخورد حل‌کننده Z3 را شبیه‌سازی می‌کنند.
    """

    def setUp(self):
        # مقداردهی اولیه موتور پالایش با بودجه محدود برای تست
        self.engine = RefinementEngine(max_budget=3)

    def test_syntax_refinement_trigger(self):
        """تست فاز 8.1: اطمینان از تولید پرامپت اصلاحی برای خطاهای سینتکسی Z3."""
        error_msg = "Z3 Error: line 10, column 5: unknown constant x"
        prompt = self.engine.analyze_z3_feedback(solver_status="error", error_log=error_msg)
        
        self.assertIn("REFINE_PROMPT", prompt)
        self.assertIn("Syntax/Type Error", prompt)
        self.assertEqual(self.engine.current_attempt, 1)

    def test_cegar_refinement_trigger(self):
        """تست فاز 8.2: اطمینان از تولید پرامپت تقویت اینواریانت (CEGAR) با استفاده از مدل نقض."""
        mock_model = "[n = 5, res = 10]"
        prompt = self.engine.analyze_z3_feedback(solver_status="sat", model=mock_model)
        
        self.assertIn("counter-example", prompt)
        self.assertIn("strengthen", prompt)
        self.assertIn("[n = 5, res = 10]", prompt)
        self.assertEqual(self.engine.current_attempt, 1)

    def test_budget_exhaustion(self):
        """تست مدیریت بودجه: اطمینان از اینکه سیستم پس از اتمام بودجه متوقف می‌شود."""
        # شبیه‌سازی 3 بار تلاش ناموفق
        for _ in range(3):
            self.engine.analyze_z3_feedback(solver_status="unknown")
            
        self.assertTrue(self.engine.is_budget_exceeded())
        self.assertEqual(self.engine.current_attempt, 3)

if __name__ == "__main__":
    unittest.main()
